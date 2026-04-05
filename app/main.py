from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.music import router

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