from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import get_db_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from tests.routes import test_router

DATABASE_URL = "sqlite+aiosqlite:///./sqlite3.db"

engine = create_async_engine(DATABASE_URL, connect_args={
    "check_same_thread": False
})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(test_router, prefix="/api/v1/test")
app.dependency_overrides[get_db_session] = override_get_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_main:app", host="0.0.0.0", port=8000, reload=True)
