"""
数据采集器启动脚本
统一管理链上和CEX数据采集
"""

import asyncio
import signal
import sys

from src.common.config import settings
from src.common.logger import configure_logging, get_logger
from src.data_collection.onchain.chain_manager import ChainManager
from src.data_collection.cex.cex_manager import CEXManager
from src.common.kafka_client import KafkaProducer

configure_logging(settings.log_level)
logger = get_logger(__name__)


class DataCollectorApp:
    """数据采集应用"""

    def __init__(self):
        self.chain_manager = ChainManager()
        self.cex_manager = CEXManager()
        self.kafka_producer = None
        self.running = False

    async def start(self):
        """启动采集"""
        logger.info("starting_data_collector_app")
        self.running = True

        # 初始化Kafka生产者
        self.kafka_producer = KafkaProducer()
        await self.kafka_producer.start()

        # 初始化链上采集
        self.chain_manager.init_chains()
        for collector in self.chain_manager.get_all_collectors().values():
            # 设置Kafka回调
            collector.subscribe_blocks(self._on_block)
            collector.subscribe_transactions(self._on_transaction)
        await self.chain_manager.start()

        # 初始化CEX采集
        self.cex_manager.init_exchanges()
        for collector in self.cex_manager.get_all_collectors().values():
            # 设置回调
            collector.subscribe_ticker(self._on_ticker)
            collector.subscribe_trades(self._on_trade)
            collector.subscribe_klines(self._on_kline)
        await self.cex_manager.start()

        # 订阅热门交易对
        popular_symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
        for exchange in self.cex_manager.get_all_collectors().keys():
            await self.cex_manager.subscribe_symbols(exchange, popular_symbols)

        logger.info("data_collector_app_started")

    async def stop(self):
        """停止采集"""
        logger.info("stopping_data_collector_app")
        self.running = False

        await self.chain_manager.stop()
        await self.cex_manager.stop()

        if self.kafka_producer:
            await self.kafka_producer.stop()

        logger.info("data_collector_app_stopped")

    async def _on_block(self, event):
        """区块事件处理"""
        await self.kafka_producer.send("onchain.blocks", event.model_dump())
        logger.debug("block_sent_to_kafka", block_number=event.block_number, chain=event.chain)

    async def _on_transaction(self, event):
        """交易事件处理"""
        await self.kafka_producer.send("onchain.transactions", event.model_dump())

    async def _on_ticker(self, event):
        """行情事件处理"""
        await self.kafka_producer.send("cex.ticker", event.model_dump())

    async def _on_trade(self, event):
        """成交事件处理"""
        await self.kafka_producer.send("cex.trades", event.model_dump())

    async def _on_kline(self, event):
        """K线事件处理"""
        await self.kafka_producer.send("cex.klines", event.model_dump())


async def main():
    """主函数"""
    app = DataCollectorApp()

    # 信号处理
    def signal_handler(sig, frame):
        logger.info("shutdown_signal_received")
        asyncio.create_task(app.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await app.start()

        # 保持运行
        while app.running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error("collector_app_error", error=str(e))
        await app.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
