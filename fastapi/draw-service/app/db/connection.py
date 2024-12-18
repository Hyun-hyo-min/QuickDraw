import redis.asyncio as redis
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlmodel import SQLModel
from app.config import settings


database_connection_url = settings.DRAW_DB_URL.replace(
    "postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(database_connection_url)

session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=6379,
    decode_responses=True 
)

def get_redis_client():
    return redis_client


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        # TODO: drop_table
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db(engine: AsyncEngine):
    await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise error
        finally:
            await session.close()
