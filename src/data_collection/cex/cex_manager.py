"""
CEX 管理器
统一管理多个中心化交易所采集器
"""

from typing import Dict, List, Optional

from src.common.logger import get_logger
from src.data_collection.cex.binance_collector import BinanceCollector
from src.data_collection.cex.okx_collector import OKXCollector
from src.data_collection.cex.bybit_collector import BybitCollector
from src.data_collection.cex.bitget_collector import BitgetCollector

logger = get_logger(__name__)


class CEXManager:
    """
    中心化交易所管理器

    统一管理币安、OKX、Bybit、Bitget的数据采集
    """

    # 支持的交易所
    SUPPORTED_EXCHANGES = ["binance", "okx", "bybit", "bitget"]

    def __init__(self):
        self.collectors: Dict[str, any] = {}
        self.running = False

    def init_exchanges(self, exchanges: Optional[List[str]] = None):
        """
        初始化交易所采集器

        Args:
            exchanges: 交易所列表，None则初始化所有支持的交易所
        """
        if exchanges is None:
            exchanges = self.SUPPORTED_EXCHANGES

        for exchange in exchanges:
            exchange = exchange.lower()

            try:
                if exchange == "binance":
                    self.collectors[exchange] = BinanceCollector()
                elif exchange == "okx":
                    self.collectors[exchange] = OKXCollector()
                elif exchange == "bybit":
                    self.collectors[exchange] = BybitCollector()
                elif exchange == "bitget":
                    self.collectors[exchange] = BitgetCollector()
                else:
                    logger.warning("unsupported_exchange", exchange=exchange)
                    continue

                logger.info("exchange_collector_initialized", exchange=exchange)

            except Exception as e:
                logger.error("init_exchange_collector_failed", exchange=exchange, error=str(e))

    async def start(self):
        """启动所有交易所采集器"""
        if self.running:
            return

        self.running = True

        for name, collector in self.collectors.items():
            try:
                await collector.start()
                logger.info("exchange_collector_started", exchange=name)
            except Exception as e:
                logger.error("start_exchange_collector_failed", exchange=name, error=str(e))

        logger.info("cex_manager_started", exchanges=list(self.collectors.keys()))

    async def stop(self):
        """停止所有交易所采集器"""
        self.running = False

        for name, collector in self.collectors.items():
            try:
                await collector.stop()
                logger.info("exchange_collector_stopped", exchange=name)
            except Exception as e:
                logger.error("stop_exchange_collector_failed", exchange=name, error=str(e))

        logger.info("cex_manager_stopped")

    def get_collector(self, exchange: str):
        """获取指定交易所的采集器"""
        return self.collectors.get(exchange.lower())

    def get_all_collectors(self) -> Dict[str, any]:
        """获取所有采集器"""
        return self.collectors.copy()

    async def subscribe_symbols(self, exchange: str, symbols: List[str]):
        """
        订阅指定交易所的交易对

        Args:
            exchange: 交易所名称
            symbols: 交易对列表，如 ["BTC/USDT", "ETH/USDT"]
        """
        collector = self.get_collector(exchange)
        if collector:
            await collector.subscribe_symbols(symbols)
            logger.info("subscribed_symbols", exchange=exchange, symbols=symbols)
        else:
            logger.warning("exchange_not_found", exchange=exchange)

    async def subscribe_symbols_all(self, symbols_map: Dict[str, List[str]]):
        """
        批量订阅多个交易所的交易对

        Args:
            symbols_map: {exchange: [symbols]} 格式的字典
        """
        for exchange, symbols in symbols_map.items():
            await self.subscribe_symbols(exchange, symbols)

    def get_status(self) -> Dict:
        """获取状态信息"""
        return {
            "running": self.running,
            "exchanges": list(self.collectors.keys()),
        }
