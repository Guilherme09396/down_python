from fastapi import APIRouter, Request, HTTPException, Depends
from app.services.ytdlp import run_ytdlp
from app.services.cache import get_cache, set_cache
from app.services.limiter import rate_limit
from app.worker import prefetch_audio
from app.core.config import STREAM_TTL, SEARCH_TTL
import json
import requests
import tempfile
import os
import shutil

router = APIRouter()


@router.get("/")
def root():
    return {"message": "API funcionando 🚀"}


# ================= INFO =================
@router.post("/info")
async def info(data: dict, request: Request, _: None = Depends(rate_limit)):
    url = data.get("url")

    result = run_ytdlp(url, ["--dump-single-json"])
    info = json.loads(result)

    prefetch_audio.delay(url)

    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "artist": info.get("uploader"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "url": info.get("webpage_url"),
    }


# ================= SEARCH =================
@router.post("/search")
async def search(data: dict, request: Request, _: None = Depends(rate_limit)):
    query = data.get("query")

    cache_key = f"search:{query}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    result = run_ytdlp(
        f"ytsearch8:{query}",
        ["--flat-playlist", "--dump-single-json", "--skip-download"]
    )

    data = json.loads(result)

    tracks = []
    for item in data.get("entries", []):
        if not item:
            continue

        url = item.get("url") or f"https://youtube.com/watch?v={item.get('id')}"

        tracks.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "artist": item.get("uploader") or item.get("channel"),
            "duration": item.get("duration"),
            "thumbnail": item.get("thumbnail") or f"https://i.ytimg.com/vi/{item.get('id')}/hqdefault.jpg",
            "url": url
        })

        # pré-carrega
        prefetch_audio.delay(url)

    set_cache(cache_key, tracks, SEARCH_TTL)

    return tracks


# ================= STREAM =================
@router.get("/stream")
async def stream(url: str, request: Request, _: None = Depends(rate_limit)):
    cache_key = f"stream:{url}"
    audio_url = get_cache(cache_key)

    if not audio_url:
        result = run_ytdlp(url, ["-f", "bestaudio", "--get-url"])
        audio_url = result.split("\n")[0]
        set_cache(cache_key, audio_url, STREAM_TTL)

    headers = {}
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    r = requests.get(audio_url, stream=True, headers=headers)

    def gen():
        for chunk in r.iter_content(8192):
            yield chunk

    from fastapi.responses import StreamingResponse

    res = StreamingResponse(gen(), media_type=r.headers.get("content-type", "audio/webm"))

    if "content-length" in r.headers:
        res.headers["Content-Length"] = r.headers["content-length"]

    if "content-range" in r.headers:
        res.headers["Content-Range"] = r.headers["content-range"]

    res.headers["Accept-Ranges"] = "bytes"

    return res


# ================= DOWNLOAD =================
@router.get("/download")
async def download(url: str, title: str = "music", _: None = Depends(rate_limit)):
    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, "audio.%(ext)s")

    try:
        run_ytdlp(url, [
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--add-metadata",
            "--embed-thumbnail",
            "--convert-thumbnails", "jpg",
            "-o", out
        ])

        file = next(f for f in os.listdir(tmp) if f.endswith(".mp3"))
        path = os.path.join(tmp, file)

        def stream():
            try:
                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                # 🔥 REMOVE SOMENTE AQUI (correto)
                shutil.rmtree(tmp, ignore_errors=True)

        from fastapi.responses import StreamingResponse

        return StreamingResponse(
            stream(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{title}.mp3"'
            }
        )

    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise HTTPException(500, str(e))