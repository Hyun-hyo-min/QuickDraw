import logging
from redis import asyncio as aioredis
from config import settings

logger = logging.getLogger(__name__)


async def get_redis_pool():
    redis_url = f"redis://{settings.REDIS_HOST}:6379/0"
    return await aioredis.from_url(redis_url)


class RedisSessionManager:
    def __init__(self, session_id, redis: aioredis.Redis):
        self.session_id = str(session_id)
        self.redis = redis
        self.session_key = f"session:{self.session_id}:clients"

    async def session_exists(self) -> bool:
        return await self.redis.exists(self.session_key) > 0

    async def add_client_to_session(self, client: str):
        await self.redis.sadd(self.session_key, client)
        await self.redis.expire(self.session_key, 300)
        logger.info(f"Added client {client} to session {self.session_id}")

    async def remove_client(self, client: str):
        await self.redis.srem(self.session_key, client)
        logger.info(f"Removed client {client} from session {self.session_id}")

    async def get_client_count(self) -> int:
        return await self.redis.scard(self.session_key)

    async def get_clients(self):
        clients = await self.redis.smembers(self.session_key)
        return [client.decode('utf-8') for client in clients]
