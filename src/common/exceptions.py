"""
异常定义模块
"""

from typing import Any, Dict, Optional


class OpenDuneException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DataCollectionError(OpenDuneException):
    """数据采集异常"""

    def __init__(
        self,
        message: str,
        source: str = None,
        error_code: str = "DATA_COLLECTION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.source = source


class ExchangeAPIError(DataCollectionError):
    """交易所API异常"""

    def __init__(
        self,
        exchange: str,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{exchange} API error {status_code}: {message}",
            source=exchange,
            error_code=f"EXCHANGE_API_ERROR",
            details=details
        )
        self.exchange = exchange
        self.status_code = status_code


class BlockchainError(DataCollectionError):
    """区块链节点异常"""

    def __init__(
        self,
        chain: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{chain} blockchain error: {message}",
            source=chain,
            error_code="BLOCKCHAIN_ERROR",
            details=details
        )
        self.chain = chain


class StorageError(OpenDuneException):
    """数据存储异常"""

    def __init__(
        self,
        message: str,
        storage_type: str = None,
        error_code: str = "STORAGE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
        self.storage_type = storage_type


class ValidationError(OpenDuneException):
    """数据验证异常"""

    def __init__(
        self,
        message: str,
        field: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class ConfigurationError(OpenDuneException):
    """配置错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class CircuitBreakerOpen(OpenDuneException):
    """熔断器打开异常"""

    def __init__(self, message: str = "Circuit breaker is open"):
        super().__init__(message, "CIRCUIT_BREAKER_OPEN")
