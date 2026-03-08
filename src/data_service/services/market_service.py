"""
行情服务
"""

from datetime import datetime
from typing import List, Optional

from src.common.config import settings
from src.common.logger import get_logger
from src.data_storage.redis_client import RedisClient
from src.data_storage.tdengine_client import TDengineClient

logger = get_logger(__name__)


class MarketService:
    """行情服务"""

    def __init__(self):
        self.redis = RedisClient()
        self.tdengine = TDengineClient(
            host=settings.tdengine_host,
            port=settings.tdengine_port,
            user=settings.tdengine_user,
            password=settings.tdengine_password,
            database=settings.tdengine_database,
        )

    async def get_ticker(self, symbol: str, exchange: Optional[str] = None) -> Optional[dict]:
        """获取最新行情"""
        try:
            # 先从Redis获取
            cache_key = f"ticker:{exchange}:{symbol}" if exchange else f"ticker:{symbol}"
            ticker = await self.redis.get(cache_key)

            if ticker:
                return ticker

            # TODO: 从数据库查询
            return None

        except Exception as e:
            logger.error("get_ticker_error", symbol=symbol, error=str(e))
            return None

    async def get_tickers(
        self,
        exchange: Optional[str] = None,
        symbols: Optional[List[str]] = None
    ) -> List[dict]:
        """获取多个交易对的行情"""
        try:
            # TODO: 实现批量查询
            return []
        except Exception as e:
            logger.error("get_tickers_error", error=str(e))
            return []

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        exchange: Optional[str] = None,
    ) -> List[dict]:
        """获取K线数据"""
        try:
            # 从TDengine查询
            table_name = f"kline_{interval}_{symbol}"
            if exchange:
                table_name += f"_{exchange}"

            # TODO: 实现TDengine查询
            return []

        except Exception as e:
            logger.error("get_klines_error", symbol=symbol, error=str(e))
            return []

    async def get_order_book(
        self,
        symbol: str,
        limit: int = 20,
        exchange: Optional[str] = None,
    ) -> Optional[dict]:
        """获取订单簿"""
        try:
            # 从Redis获取
            cache_key = f"orderbook:{exchange}:{symbol}" if exchange else f"orderbook:{symbol}"
            orderbook = await self.redis.get(cache_key)

            if orderbook:
                return orderbook

            return None

        except Exception as e:
            logger.error("get_order_book_error", symbol=symbol, error=str(e))
            return None
