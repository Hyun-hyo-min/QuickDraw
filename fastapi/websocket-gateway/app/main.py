from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import proxy
from app.config import settings

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    f"https://{settings.BASE_URL}",
    f"https://www.{settings.BASE_URL}",
]

app.router.redirect_slashes = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy.router)
