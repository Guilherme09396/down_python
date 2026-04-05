from celery import Celery
from app.services.ytdlp import run_ytdlp

celery = Celery("worker", broker="redis://redis:6379")

@celery.task
def prefetch_audio(url):
    try:
        run_ytdlp(url, ["-f", "bestaudio", "--get-url"])
    except:
        pass