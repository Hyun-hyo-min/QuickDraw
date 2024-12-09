from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.connection import init_db, close_db, engine
from app.routes import draw
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db(engine)
        yield
    finally:
        await close_db(engine)

app = FastAPI(
    lifespan=lifespan,
    title="Room Service",
    description="Service for managing rooms in the system",
    version="1.0.0"
)

app.router.redirect_slashes = False

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    f"https://{settings.BASE_URL}",
    f"https://{settings.BASE_URL.replace('www.', '')}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(draw.router, prefix="/draw", tags=["Draw"])
