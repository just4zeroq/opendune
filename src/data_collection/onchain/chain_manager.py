"""
链管理器
统一管理多链采集器
"""

import asyncio
from typing import Dict, List, Optional

from src.common.config import settings
from src.common.logger import get_logger
from src.data_collection.onchain.alchemy_collector import AlchemyCollector, BSC_NODES
from src.data_collection.onchain.multi_node_provider import MultiNodeProvider

logger = get_logger(__name__)


class ChainManager:
    """
    链管理器

    统一管理 Ethereum、BSC、Polygon、Arbitrum、Base 等链的采集器
    """

    # 支持的链配置
    SUPPORTED_CHAINS = {
        "ethereum": {"name": "Ethereum", "networks": ["mainnet", "sepolia"]},
        "bsc": {"name": "BSC", "networks": ["mainnet", "testnet"]},
        "polygon": {"name": "Polygon", "networks": ["mainnet", "mumbai"]},
        "arbitrum": {"name": "Arbitrum", "networks": ["mainnet", "sepolia"]},
        "base": {"name": "Base", "networks": ["mainnet", "sepolia"]},
    }

    def __init__(self):
        self.collectors: Dict[str, AlchemyCollector] = {}
        self.running = False
        self._tasks: List[asyncio.Task] = []

    def init_chains(self, chains: Optional[List[str]] = None):
        """
        初始化链采集器

        Args:
            chains: 要初始化的链列表，None则使用配置中的链
        """
        if chains is None:
            chains = settings.alchemy_chains

        api_key = settings.alchemy_api_key

        for chain in chains:
            chain = chain.lower()

            if chain not in self.SUPPORTED_CHAINS:
                logger.warning("unsupported_chain", chain=chain)
                continue

            try:
                if chain == "bsc":
                    # BSC使用多节点提供者
                    provider = MultiNodeProvider(
                        BSC_NODES + settings.bsc_backup_rpc_urls,
                        strategy="round_robin"
                    )
                    # 创建特殊的BSC采集器
                    collector = AlchemyCollector(
                        api_key="",  # BSC不需要API key
                        chain="bsc",
                        network="mainnet"
                    )
                else:
                    collector = AlchemyCollector(
                        api_key=api_key,
                        chain=chain,
                        network="mainnet"
                    )

                self.collectors[chain] = collector
                logger.info("chain_collector_initialized", chain=chain)

            except Exception as e:
                logger.error("init_chain_collector_failed", chain=chain, error=str(e))

    async def start(self):
        """启动所有采集器"""
        if self.running:
            return

        self.running = True

        for chain, collector in self.collectors.items():
            try:
                await collector.start()
                logger.info("chain_collector_started", chain=chain)
            except Exception as e:
                logger.error("start_chain_collector_failed", chain=chain, error=str(e))

        logger.info("chain_manager_started", chains=list(self.collectors.keys()))

    async def stop(self):
        """停止所有采集器"""
        self.running = False

        for chain, collector in self.collectors.items():
            try:
                await collector.stop()
                logger.info("chain_collector_stopped", chain=chain)
            except Exception as e:
                logger.error("stop_chain_collector_failed", chain=chain, error=str(e))

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        logger.info("chain_manager_stopped")

    def get_collector(self, chain: str) -> Optional[AlchemyCollector]:
        """获取指定链的采集器"""
        return self.collectors.get(chain.lower())

    def get_all_collectors(self) -> Dict[str, AlchemyCollector]:
        """获取所有采集器"""
        return self.collectors.copy()

    def subscribe_all_blocks(self, callback):
        """订阅所有链的区块"""
        for chain, collector in self.collectors.items():
            collector.subscribe_blocks(callback)
            logger.debug("subscribed_to_chain_blocks", chain=chain)

    def get_status(self) -> Dict:
        """获取状态信息"""
        return {
            "running": self.running,
            "chains": {
                chain: {
                    "connected": collector.is_connected(),
                    "subscribers": {
                        k: len(v) for k, v in collector.subscribers.items()
                    }
                }
                for chain, collector in self.collectors.items()
            }
        }
