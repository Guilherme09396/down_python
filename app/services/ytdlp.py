import subprocess
import os

# =========================
# COOKIES DINÂMICO (Railway)
# =========================
def ensure_cookies_file():
    cookies_env = os.getenv("YOUTUBE_COOKIES")

    if not cookies_env:
        print("⚠️ Nenhum cookie encontrado - rodando sem autenticação")
        return None

    path = "/tmp/cookies.txt"

    try:
        with open(path, "w") as f:
            f.write(cookies_env)

        print("🍪 Cookies carregados com sucesso")
        return path

    except Exception as e:
        print("❌ Erro ao criar arquivo de cookies:", e)
        return None


# =========================
# STRATEGIES (OTIMIZADAS)
# =========================
STRATEGIES = [
    ["--extractor-args", "youtube:player_client=android"],
    ["--extractor-args", "youtube:player_client=ios"],
    ["--extractor-args", "youtube:player_client=tv"],
]

# =========================
# BASE ARGS (SEM COOKIES FIXO)
# =========================
BASE_ARGS = [
    "--no-warnings",
    "--no-check-certificate",
    "--add-header", "user-agent:Mozilla/5.0",
    "--add-header", "accept-language:en-US,en;q=0.9"
]


# =========================
# RUN YT-DLP (ROBUSTO)
# =========================
def run_ytdlp(url, extra_args):
    last_error = None

    cookies_path = ensure_cookies_file()

    FORMATS = [
        ["-f", "bestaudio/best"],
        ["-f", "best"],
        ["-f", "worst"],
    ]

    for fmt in FORMATS:
        for strategy in STRATEGIES:
            try:
                cmd = ["yt-dlp", url] + BASE_ARGS

                if cookies_path:
                    cmd += ["--cookies", cookies_path]

                cmd += strategy + fmt + extra_args

                print("🚀 CMD:", " ".join(cmd))

                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

                return result.decode("utf-8")

            except subprocess.CalledProcessError as e:
                last_error = e
                print("❌ ERRO YT-DLP:")
                print(e.output.decode("utf-8", errors="ignore"))
                print("⚠️ Falhou:", fmt, strategy)

    # fallback final SEM cookies
    try:
        cmd = ["yt-dlp", url] + BASE_ARGS + ["-f", "bestaudio/best"] + extra_args

        print("🚀 FALLBACK FINAL:", " ".join(cmd))

        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        return result.decode("utf-8")

    except subprocess.CalledProcessError as e:
        print("❌ ERRO FINAL:")
        print(e.output.decode("utf-8", errors="ignore"))
        raise e