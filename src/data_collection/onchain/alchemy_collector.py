"""
Alchemy 链上数据采集器
支持多链实时数据获取
"""

import asyncio
import json
from decimal import Decimal
from typing import Callable, Dict, List, Optional, Any

import aiohttp
import websockets
from web3 import Web3

from src.common.config import settings
from src.common.exceptions import BlockchainError
from src.common.logger import get_logger
from src.common.models import BlockEvent, LogEvent, TransactionEvent

logger = get_logger(__name__)


# Alchemy 支持的链和网络映射
ALCHEMY_CHAINS = {
    "ethereum": {
        "mainnet": "eth-mainnet",
        "sepolia": "eth-sepolia",
    },
    "polygon": {
        "mainnet": "polygon-mainnet",
        "mumbai": "polygon-mumbai",
    },
    "arbitrum": {
        "mainnet": "arb-mainnet",
        "sepolia": "arb-sepolia",
    },
    "base": {
        "mainnet": "base-mainnet",
        "sepolia": "base-sepolia",
    },
}

# BSC 节点配置（Alchemy不支持BSC，使用公共节点）
BSC_NODES = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.defibit.io",
    "https://bsc-dataseed1.ninicoin.io",
]


class AlchemyCollector:
    """
    Alchemy 链上数据采集器

    支持功能：
    - 实时区块监听
    - 交易监控
    - 合约事件日志订阅
    - 代币转账追踪
    """

    def __init__(self, api_key: str, chain: str = "ethereum", network: str = "mainnet"):
        self.api_key = api_key
        self.chain = chain.lower()
        self.network = network.lower()

        # 构建RPC URL
        if self.chain == "bsc":
            # BSC使用公共节点
            self.http_url = BSC_NODES[0]
            self.ws_url = None  # BSC公共节点不支持WebSocket
            self.w3 = Web3(Web3.HTTPProvider(self.http_url))
        else:
            # Alchemy支持的链
            alchemy_network = ALCHEMY_CHAINS.get(self.chain, {}).get(self.network)
            if not alchemy_network:
                raise BlockchainError(
                    chain=chain,
                    message=f"Unsupported chain/network: {chain}/{network}"
                )

            self.http_url = f"https://{alchemy_network}.g.alchemy.com/v2/{api_key}"
            self.ws_url = f"wss://{alchemy_network}.g.alchemy.com/v2/{api_key}"
            self.w3 = Web3(Web3.HTTPProvider(self.http_url))

        self.running = False
        self.subscribers: Dict[str, List[Callable]] = {
            "blocks": [],
            "transactions": [],
            "logs": [],
        }
        self._tasks: List[asyncio.Task] = []

        logger.info(
            "alchemy_collector_initialized",
            chain=chain,
            network=network,
            http_url=self.http_url,
        )

    def is_connected(self) -> bool:
        """检查节点连接状态"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.warning("alchemy_connection_check_failed", error=str(e))
            return False

    async def start(self):
        """启动采集器"""
        if self.running:
            return

        self.running = True
        logger.info("alchemy_collector_started", chain=self.chain)

        # 启动区块监听
        if self.ws_url:
            task = asyncio.create_task(self._subscribe_new_heads())
            self._tasks.append(task)
        else:
            # BSC使用轮询
            task = asyncio.create_task(self._poll_blocks())
            self._tasks.append(task)

    async def stop(self):
        """停止采集器"""
        self.running = False

        # 取消所有任务
        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
        logger.info("alchemy_collector_stopped", chain=self.chain)

    def subscribe_blocks(self, callback: Callable[[BlockEvent], None]):
        """订阅新区块"""
        self.subscribers["blocks"].append(callback)
        logger.debug("block_subscriber_added", chain=self.chain)

    def subscribe_transactions(self, callback: Callable[[TransactionEvent], None]):
        """订阅交易"""
        self.subscribers["transactions"].append(callback)

    def subscribe_logs(self, callback: Callable[[LogEvent], None]):
        """订阅日志事件"""
        self.subscribers["logs"].append(callback)

    async def _subscribe_new_heads(self):
        """通过WebSocket订阅新区块"""
        while self.running:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    # 订阅新区块
                    subscribe_msg = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "eth_subscribe",
                        "params": ["newHeads"],
                    }
                    await ws.send(json.dumps(subscribe_msg))

                    # 接收确认
                    response = await ws.recv()
                    logger.debug("websocket_subscribed", response=response)

                    while self.running:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                            data = json.loads(message)

                            if "params" in data:
                                block_data = data["params"]["result"]
                                await self._process_block_header(block_data)
                        except asyncio.TimeoutError:
                            # 发送ping保持连接
                            await ws.send(json.dumps({"jsonrpc": "2.0", "method": "eth_subscription"}))

            except Exception as e:
                logger.error("websocket_error", chain=self.chain, error=str(e))
                await asyncio.sleep(5)

    async def _poll_blocks(self):
        """轮询新区块（用于BSC等不支持WebSocket的节点）"""
        last_block = 0

        while self.running:
            try:
                current_block = self.w3.eth.block_number

                if current_block > last_block:
                    for block_num in range(last_block + 1, current_block + 1):
                        block = self.w3.eth.get_block(block_num, full_transactions=False)
                        await self._process_block(block)
                    last_block = current_block

                await asyncio.sleep(3)  # 3秒轮询间隔

            except Exception as e:
                logger.error("poll_blocks_error", chain=self.chain, error=str(e))
                await asyncio.sleep(5)

    async def _process_block_header(self, header: Dict):
        """处理区块头信息"""
        try:
            # 获取完整区块
            block_number = int(header.get("number", "0"), 16)
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            await self._process_block(block)
        except Exception as e:
            logger.error("process_block_header_error", error=str(e))

    async def _process_block(self, block: Dict):
        """处理完整区块"""
        try:
            # 转换为BlockEvent
            event = BlockEvent(
                chain=self.chain,
                block_number=block.number,
                block_hash=block.hash.hex(),
                timestamp=block.timestamp,
                gas_used=block.gasUsed,
                gas_limit=block.gasLimit,
                tx_count=len(block.transactions),
                parent_hash=block.parentHash.hex(),
                miner=block.get("miner", ""),
            )

            # 通知订阅者
            for callback in self.subscribers["blocks"]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error("block_callback_error", error=str(e))

            # 处理交易
            if hasattr(block, "transactions"):
                for tx in block.transactions:
                    await self._process_transaction(tx, block.timestamp)

            logger.debug(
                "block_processed",
                chain=self.chain,
                block_number=block.number,
                tx_count=len(block.transactions),
            )

        except Exception as e:
            logger.error("process_block_error", chain=self.chain, error=str(e))

    async def _process_transaction(self, tx: Dict, timestamp: int):
        """处理交易"""
        try:
            event = TransactionEvent(
                chain=self.chain,
                tx_hash=tx.hash.hex() if hasattr(tx, "hash") else tx["hash"],
                block_number=tx.blockNumber if hasattr(tx, "blockNumber") else tx.get("blockNumber"),
                timestamp=timestamp,
                from_address=tx.get("from", ""),
                to_address=tx.get("to"),
                value=Decimal(str(tx.get("value", 0))) / Decimal(10**18),
                gas_price=tx.get("gasPrice"),
                input_data=tx.get("input", ""),
            )

            for callback in self.subscribers["transactions"]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error("transaction_callback_error", error=str(e))

        except Exception as e:
            logger.error("process_transaction_error", error=str(e))

    async def get_block(self, block_number: int, full_tx: bool = True) -> Optional[Dict]:
        """获取区块数据"""
        try:
            return self.w3.eth.get_block(block_number, full_transactions=full_tx)
        except Exception as e:
            logger.error("get_block_error", block_number=block_number, error=str(e))
            return None

    async def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """获取交易详情"""
        try:
            return self.w3.eth.get_transaction(tx_hash)
        except Exception as e:
            logger.error("get_transaction_error", tx_hash=tx_hash, error=str(e))
            return None

    async def get_logs(
        self,
        from_block: int,
        to_block: int,
        address: Optional[str] = None,
        topics: Optional[List[str]] = None,
    ) -> List[Dict]:
        """获取事件日志"""
        try:
            params = {
                "fromBlock": from_block,
                "toBlock": to_block,
            }
            if address:
                params["address"] = address
            if topics:
                params["topics"] = topics

            return self.w3.eth.get_logs(params)
        except Exception as e:
            logger.error("get_logs_error", error=str(e))
            return []

    async def get_token_transfers(
        self,
        from_block: str = "latest",
        to_block: str = "latest",
        contract_address: Optional[str] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
    ) -> List[Dict]:
        """
        获取代币转账记录
        使用 Alchemy 的 alchemy_getAssetTransfers API
        """
        if self.chain == "bsc":
            # BSC不支持Alchemy API，使用普通日志查询
            return []

        url = self.http_url
        headers = {"Content-Type": "application/json"}

        params = {
            "fromBlock": from_block,
            "toBlock": to_block,
            "category": ["erc20", "erc721", "erc1155"],
        }

        if contract_address:
            params["contractAddresses"] = [contract_address]
        if from_address:
            params["fromAddress"] = from_address
        if to_address:
            params["toAddress"] = to_address

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "alchemy_getAssetTransfers",
            "params": [params],
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    data = await response.json()
                    return data.get("result", {}).get("transfers", [])
        except Exception as e:
            logger.error("get_token_transfers_error", error=str(e))
            return []
