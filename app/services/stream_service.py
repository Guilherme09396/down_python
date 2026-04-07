import requests
from fastapi.responses import StreamingResponse
from app.services.cache import get_cache, set_cache
from app.services.ytdlp_service import run_ytdlp
from app.core.config import STREAM_TTL


def stream_audio(url, request):
    cache_key = f"stream:{url}"
    audio_url = get_cache(cache_key)

    if not audio_url:
        result = run_ytdlp(url, ["--get-url"])
        audio_url = result.split("\n")[0]

        if not audio_url:
            raise Exception("Erro ao obter áudio")

        set_cache(cache_key, audio_url, STREAM_TTL)

    headers = {}
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    r = requests.get(audio_url, stream=True, headers=headers)

    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            yield chunk

    response = StreamingResponse(generate(), media_type=r.headers.get("content-type", "audio/webm"))

    if "content-length" in r.headers:
        response.headers["Content-Length"] = r.headers["content-length"]

    if "content-range" in r.headers:
        response.headers["Content-Range"] = r.headers["content-range"]

    response.headers["Accept-Ranges"] = "bytes"

    return response