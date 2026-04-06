from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.music import router
import os


# Escreve cookies da variável de ambiente no arquivo
cookies_content = os.getenv("YOUTUBE_COOKIES")
if cookies_content:
    with open("/app/cookies.txt", "w") as f:
        f.write(cookies_content)

app = FastAPI()

# 🔥 LIBERAR CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode colocar específico depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)