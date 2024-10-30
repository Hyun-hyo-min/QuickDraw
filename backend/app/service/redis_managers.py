import logging
import json
from abc import ABC, abstractmethod
from fastapi import Depends
from redis import asyncio as aioredis
from redis.asyncio import Redis
from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = await Redis.from_url(f"redis://{settings.REDIS_HOST}:6379/0")
        return cls._instance

    @classmethod
    async def close_instance(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def get_redis_pool():
    return await RedisClient.get_instance()


class ClientSessionInterface(ABC):
    @abstractmethod
    async def add_client(self, client: str):
        pass

    @abstractmethod
    async def remove_client(self, client: str):
        pass

    @abstractmethod
    async def get_client_count(self) -> int:
        pass

    @abstractmethod
    async def publish_client(self, data: str):
        pass

    @abstractmethod
    async def listen(self):
        pass

    @abstractmethod
    async def delete_client_session(self):
        pass


class DrawSessionInterface(ABC):
    @abstractmethod
    async def session_exists(self):
        pass

    @abstractmethod
    async def save_draw_data(self, draw_data: dict):
        pass

    @abstractmethod
    async def get_all_draw_data(self):
        pass

    @abstractmethod
    async def clear_draw_data(self):
        pass


class RedisClientSessionManager(ClientSessionInterface):
    def __init__(self, session_id, redis: aioredis.Redis):
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.client_key = f"{session_id}:clients"

    async def session_exists(self) -> bool:
        return await self.redis.exists(self.client_key) > 0

    async def listen(self):
        await self.pubsub.subscribe(self.client_key)
        async for message in self.pubsub.listen():
            yield message

    async def publish_client(self, data: str):
        await self.redis.publish(self.client_key, data)

    async def add_client(self, client: str):
        await self.redis.sadd(self.client_key, client)
        await self.redis.expire(self.client_key, 300)

    async def remove_client(self, client: str):
        await self.redis.srem(self.client_key, client)

    async def get_client_count(self) -> int:
        return await self.redis.scard(self.client_key)

    async def delete_client_session(self):
        await self.redis.delete(self.client_key)


class RedisDrawSessionManager(DrawSessionInterface):
    def __init__(self, session_id, redis: aioredis.Redis):
        self.redis = redis
        self.draw_key = f"{session_id}:draws"

    async def session_exists(self) -> bool:
        return await self.redis.exists(self.draw_key) > 0

    async def save_draw_data(self, draw_data: dict):
        await self.redis.rpush(self.draw_key, json.dumps(draw_data))

    async def get_all_draw_data(self):
        drawings = await self.redis.lrange(self.draw_key, 0, -1)
        return [json.loads(draw) for draw in drawings]

    async def clear_draw_data(self):
        await self.redis.delete(self.draw_key)


def get_client_manager(
    session_id: int,
    redis: aioredis.Redis = Depends(get_redis_pool)
) -> ClientSessionInterface:
    return RedisClientSessionManager(session_id, redis)


def get_draw_manager(
    session_id: int,
    redis: aioredis.Redis = Depends(get_redis_pool)
) -> DrawSessionInterface:
    return RedisDrawSessionManager(session_id, redis)
