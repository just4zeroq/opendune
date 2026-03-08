"""
中心化交易所数据采集模块
支持币安、OKX、Bybit、Bitget
使用 CCXT 统一接口
"""

from src.data_collection.cex.binance_collector import BinanceCollector
from src.data_collection.cex.okx_collector import OKXCollector
from src.data_collection.cex.bybit_collector import BybitCollector
from src.data_collection.cex.bitget_collector import BitgetCollector
from src.data_collection.cex.cex_manager import CEXManager

__all__ = [
    "BinanceCollector",
    "OKXCollector",
    "BybitCollector",
    "BitgetCollector",
    "CEXManager",
]
