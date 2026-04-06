import subprocess
import os

COOKIES_PATH = os.getenv("COOKIES_PATH", "/app/cookies.txt")

STRATEGIES = [
    ["--extractor-args", "youtube:player_client=mweb"],
    ["--extractor-args", "youtube:player_client=ios"],
    ["--extractor-args", "youtube:player_client=android"],
    ["--extractor-args", "youtube:player_client=tv_embedded"],
    ["--extractor-args", "youtube:player_client=web"],
]

BASE_ARGS = [
    "--no-warnings",
    "--no-check-certificate",
    "--cookies", COOKIES_PATH,
    "--add-header", "user-agent:Mozilla/5.0",
    "--add-header", "accept-language:en-US,en;q=0.9"
]

def run_ytdlp(url, extra_args):
    last_error = None

    for strategy in STRATEGIES:
        try:
            cmd = ["yt-dlp", url] + BASE_ARGS + strategy + extra_args
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return result.decode("utf-8")

        except subprocess.CalledProcessError as e:
            last_error = e
            print("⚠️ Estratégia falhou, tentando próxima...")

    raise last_error