import os
from celery import Celery
from app.services.ytdlp import run_ytdlp

celery = Celery("worker", broker=os.getenv("REDIS_URL"), backend=os.getenv("REDIS_URL"),)

@celery.task
def prefetch_audio(url):
    try:
        run_ytdlp(url, ["-f", "bestaudio", "--get-url"])
    except:
        pass