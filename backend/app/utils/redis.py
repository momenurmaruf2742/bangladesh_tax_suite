import logging
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    def connect(self) -> None:
        """Establish Redis connection."""
        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Closed Redis connection.")

    async def set_value(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set a value in Redis."""
        if not self.client:
            logger.warning(f"Redis client not connected. Cannot set key: {key}")
            return False
        try:
            await self.client.set(key, value, ex=expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    async def get_value(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        if not self.client:
            logger.warning(f"Redis client not connected. Cannot get key: {key}")
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        if not self.client:
            logger.warning(f"Redis client not connected. Cannot check exists: {key}")
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking key {key} existence in Redis: {e}")
            return False


# Singleton Redis client
redis_client = RedisClient()
