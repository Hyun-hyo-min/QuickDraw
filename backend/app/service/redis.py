import logging
import json
from redis import asyncio as aioredis
from config import settings
from typing import List

logger = logging.getLogger(__name__)


async def get_redis_pool():
    redis_url = f"redis://{settings.REDIS_HOST}:6379/0"
    return await aioredis.from_url(redis_url)


class RedisSessionManager:
    def __init__(self, session_id, redis: aioredis.Redis):
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.client_key = f"{session_id}:clients"
        self.draw_key = f"{session_id}:draws"

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

    async def save_draw_data(self, draw_data: dict):
        await self.redis.rpush(self.draw_key, json.dumps(draw_data))

    async def get_all_draw_data(self):
        drawings = await self.redis.lrange(self.draw_key, 0, -1)
        return [json.loads(draw) for draw in drawings]

    async def clear_draw_data(self):
        await self.redis.delete(self.draw_key)
