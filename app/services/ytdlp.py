import subprocess
from app.core.config import COOKIES_PATH

BASE_ARGS = [
    "--no-warnings",
    "--no-check-certificate",
    "--cookies", COOKIES_PATH
]

STRATEGIES = [
    ["--extractor-args", "youtube:player_client=ios"],
    ["--extractor-args", "youtube:player_client=android"],
    ["--extractor-args", "youtube:player_client=tv_embedded"],
]


def run_ytdlp(url, extra=[]):
    last = None

    for s in STRATEGIES:
        try:
            cmd = ["yt-dlp", url, *BASE_ARGS, *s, *extra]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return out.decode().strip()
        except Exception as e:
            last = e

    raise last