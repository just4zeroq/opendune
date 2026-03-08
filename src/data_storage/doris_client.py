"""
Doris 客户端
用于OLAP分析查询
"""

from typing import Any, Dict, List, Optional

import aiomysql

from src.common.config import settings
from src.common.logger import get_logger

logger = get_logger(__name__)


class DorisClient:
    """Doris OLAP客户端（兼容MySQL协议）"""

    def __init__(self):
        self.host = settings.doris_host
        self.port = settings.doris_port
        self.user = settings.doris_user
        self.password = settings.doris_password
        self.database = settings.doris_database
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
                maxsize=10,
            )
            logger.info("doris_connected", host=self.host, database=self.database)
        except Exception as e:
            logger.error("doris_connection_failed", error=str(e))
            raise

    async def disconnect(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("doris_disconnected")

    async def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行分析查询"""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(sql, params)
                    return await cur.fetchall()
                except Exception as e:
                    logger.error("doris_query_error", sql=sql, error=str(e))
                    return []

    async def get_trade_stats(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """获取交易统计"""
        sql = """
            SELECT * FROM trade_stats
            WHERE symbol = %s AND stat_date BETWEEN %s AND %s
            ORDER BY stat_date, stat_hour
        """
        return await self.query(sql, (symbol, start_date, end_date))

    async def get_volume_report(
        self,
        exchange: str,
        date: str,
    ) -> List[Dict[str, Any]]:
        """获取成交量报表"""
        sql = """
            SELECT * FROM volume_report
            WHERE exchange = %s AND stat_date = %s
            ORDER BY total_volume DESC
        """
        return await self.query(sql, (exchange, date))
