import subprocess
import os

COOKIES_PATH = os.getenv("COOKIES_PATH", "/app/cookies.txt")

STRATEGIES = [
    ["--extractor-args", "youtube:player_client=android"],
    ["--extractor-args", "youtube:player_client=ios"],
    ["--extractor-args", "youtube:player_client=tv"],
]

BASE_ARGS = [
    "--no-warnings",
    "--no-check-certificate",
    "--cookies", COOKIES_PATH,
    "--add-header", "user-agent:Mozilla/5.0",
    "--add-header", "accept-language:en-US,en;q=0.9"
]

if not os.path.exists(COOKIES_PATH):
    print("⚠️ COOKIE NÃO EXISTE - rodando sem autenticação")
    BASE_ARGS = [arg for arg in BASE_ARGS if "--cookies" not in arg]

def run_ytdlp(url, extra_args):
    last_error = None

    for strategy in STRATEGIES:
        try:
            cmd = ["yt-dlp", url] + BASE_ARGS + strategy + extra_args

            print("🚀 CMD:", " ".join(cmd))  # DEBUG IMPORTANTE

            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

            return result.decode("utf-8")

        except subprocess.CalledProcessError as e:
            last_error = e

            print("❌ ERRO REAL DO YT-DLP:")
            print(e.output.decode("utf-8", errors="ignore"))

            print("⚠️ Estratégia falhou:", strategy)

    raise last_error