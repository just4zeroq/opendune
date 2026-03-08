"""
Redis 客户端
"""

import json
from typing import Any, Optional

import aioredis

from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis客户端"""

    def __init__(self):
        self.host = settings.redis_host
        self.port = settings.redis_port
        self.password = settings.redis_password
        self.db = settings.redis_db
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """连接Redis"""
        try:
            self._redis = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis_connected", host=self.host, port=self.port)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def disconnect(self):
        """断开连接"""
        if self._redis:
            await self._redis.close()
            logger.info("redis_disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        if not self._redis:
            await self.connect()

        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ):
        """设置值"""
        if not self._redis:
            await self.connect()

        try:
            json_value = json.dumps(value, default=str)
            await self._redis.set(key, json_value, ex=expire)
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))

    async def delete(self, key: str):
        """删除键"""
        if not self._redis:
            await self.connect()

        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.error("redis_delete_error", key=key, error=str(e))

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            await self.connect()

        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error("redis_exists_error", key=key, error=str(e))
            return False

    async def publish(self, channel: str, message: Any):
        """发布消息"""
        if not self._redis:
            await self.connect()

        try:
            await self._redis.publish(channel, json.dumps(message, default=str))
        except Exception as e:
            logger.error("redis_publish_error", channel=channel, error=str(e))
