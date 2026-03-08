"""
MySQL 客户端
"""

from typing import Any, Dict, List, Optional

import aiomysql

from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger(__name__)


class MySQLClient:
    """MySQL异步客户端"""

    def __init__(self):
        self.host = settings.mysql_host
        self.port = settings.mysql_port
        self.user = settings.mysql_user
        self.password = settings.mysql_password
        self.database = settings.mysql_database
        self.pool: Optional[aiomysql.Pool] = None

    async def connect(self):
        """创建连接池"""
        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                minsize=1,
                maxsize=settings.mysql_pool_size,
            )
            logger.info("mysql_connected", host=self.host, database=self.database)
        except Exception as e:
            logger.error("mysql_connection_failed", error=str(e))
            raise

    async def disconnect(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("mysql_disconnected")

    async def execute(self, sql: str, params: tuple = None) -> int:
        """执行SQL"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if params:
                        await cur.execute(sql, params)
                    else:
                        await cur.execute(sql)
                    await conn.commit()
                    return cur.rowcount
                except Exception as e:
                    await conn.rollback()
                    logger.error("mysql_execute_error", sql=sql, error=str(e))
                    raise

    async def fetchone(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """查询单条"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(sql, params)
                    return await cur.fetchone()
                except Exception as e:
                    logger.error("mysql_fetchone_error", sql=sql, error=str(e))
                    return None

    async def fetchall(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """查询多条"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(sql, params)
                    return await cur.fetchall()
                except Exception as e:
                    logger.error("mysql_fetchall_error", sql=sql, error=str(e))
                    return []
