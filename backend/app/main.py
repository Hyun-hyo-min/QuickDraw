from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.connection import init_db, close_db, engine
from routes.routers import router
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield
    await close_db(engine)

app = FastAPI(lifespan=lifespan)

origins = [
    'http://127.0.0.1:80',
    'http://127.0.0.1:3000',
    'http://localhost:80',
    'http://localhost:3000',
    f'https://{settings.BASE_URL}',
    f'https://{settings.BASE_URL.replace("www.", "")}',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)