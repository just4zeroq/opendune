"""
多节点故障转移提供者
支持多个RPC节点的负载均衡和故障转移
"""

import asyncio
import random
from typing import Any, Dict, List

from web3 import Web3

from src.common.exceptions import BlockchainError
from src.common.logger import get_logger

logger = get_logger(__name__)


class CircuitState:
    """熔断器状态"""
    CLOSED = "closed"       # 正常
    OPEN = "open"          # 熔断
    HALF_OPEN = "half_open"  # 半开


class CircuitBreaker:
    """熔断器实现"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def record_success(self):
        """记录成功"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("circuit_breaker_closed")

    def record_failure(self) -> bool:
        """记录失败，返回是否应该熔断"""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            return True

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("circuit_breaker_opened", failure_count=self.failure_count)
            return True

        return False

    def can_try(self) -> bool:
        """检查是否可以尝试请求"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # 检查是否过了恢复时间
            if asyncio.get_event_loop().time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("circuit_breaker_half_opened")
                return True
            return False

        return True  # HALF_OPEN


class MultiNodeProvider:
    """
    多节点故障转移提供者

    功能：
    - 多节点轮询/随机选择
    - 自动故障转移
    - 熔断保护
    - 健康检查
    """

    def __init__(self, endpoints: List[str], strategy: str = "random"):
        """
        初始化

        Args:
            endpoints: RPC节点URL列表
            strategy: 节点选择策略 random/round_robin
        """
        self.endpoints = endpoints
        self.strategy = strategy
        self.current_index = 0

        # 为每个节点创建熔断器
        self.circuit_breakers = {url: CircuitBreaker() for url in endpoints}

        # Web3实例缓存
        self._web3_instances: Dict[str, Web3] = {}

        logger.info(
            "multi_node_provider_initialized",
            node_count=len(endpoints),
            strategy=strategy,
        )

    def _get_web3(self, endpoint: str) -> Web3:
        """获取或创建Web3实例"""
        if endpoint not in self._web3_instances:
            self._web3_instances[endpoint] = Web3(Web3.HTTPProvider(endpoint))
        return self._web3_instances[endpoint]

    def _select_endpoint(self) -> str:
        """选择节点"""
        if self.strategy == "random":
            return random.choice(self.endpoints)
        else:
            # 轮询
            endpoint = self.endpoints[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.endpoints)
            return endpoint

    def _get_available_endpoint(self) -> str:
        """获取可用的节点"""
        # 先尝试获取一个可用的节点
        for _ in range(len(self.endpoints)):
            endpoint = self._select_endpoint()
            cb = self.circuit_breakers[endpoint]

            if cb.can_try():
                return endpoint

        # 所有节点都熔断了，强制选择一个
        logger.warning("all_nodes_opened_forcing_retry")
        return self._select_endpoint()

    async def call(self, method: str, *args, **kwargs) -> Any:
        """
        调用RPC方法，带故障转移

        Args:
            method: Web3方法名
            *args, **kwargs: 方法参数

        Returns:
            方法返回结果

        Raises:
            BlockchainError: 所有节点都失败时抛出
        """
        attempts = 0
        max_attempts = len(self.endpoints)
        last_error = None

        while attempts < max_attempts:
            endpoint = self._get_available_endpoint()
            cb = self.circuit_breakers[endpoint]

            try:
                w3 = self._get_web3(endpoint)
                func = getattr(w3, method)

                # 执行调用
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    # 在线程池中执行同步调用
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, func, *args, **kwargs)

                # 记录成功
                cb.record_success()
                return result

            except Exception as e:
                last_error = e
                cb.record_failure()
                logger.warning(
                    "rpc_call_failed",
                    endpoint=endpoint,
                    method=method,
                    attempt=attempts + 1,
                    error=str(e),
                )
                attempts += 1

        # 所有节点都失败了
        raise BlockchainError(
            chain="multi-node",
            message=f"All RPC endpoints failed after {max_attempts} attempts: {str(last_error)}"
        )

    async def get_block_number(self) -> int:
        """获取最新区块高度"""
        return await self.call("eth", "block_number")

    async def get_block(self, block_number: int, full_transactions: bool = False) -> Dict:
        """获取区块"""
        return await self.call("eth", "get_block", block_number, full_transactions)

    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        results = {}
        for endpoint in self.endpoints:
            try:
                w3 = self._get_web3(endpoint)
                is_connected = w3.is_connected()
                results[endpoint] = is_connected
            except Exception:
                results[endpoint] = False
        return results
