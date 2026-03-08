"""
数据模型定义
使用 Pydantic 定义核心数据模型
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MarketType(str, Enum):
    """市场类型"""
    SPOT = "spot"
    FUTURE = "future"
    MARGIN = "margin"


class TradeSide(str, Enum):
    """交易方向"""
    BUY = "buy"
    SELL = "sell"


class DataSource(str, Enum):
    """数据来源"""
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    BITGET = "bitget"
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"


class KlineInterval(str, Enum):
    """K线周期"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


class TradeEvent(BaseModel):
    """交易事件模型"""

    symbol: str = Field(..., description="交易对符号")
    price: Decimal = Field(..., description="成交价格")
    quantity: Decimal = Field(..., description="成交数量")
    side: TradeSide = Field(..., description="交易方向")
    timestamp: datetime = Field(..., description="成交时间")
    source: DataSource = Field(..., description="数据来源")
    trade_id: Optional[str] = Field(None, description="交易ID")
    market_type: MarketType = Field(default=MarketType.SPOT, description="市场类型")

    # 链上交易特有字段
    tx_hash: Optional[str] = Field(None, description="交易哈希（链上）")
    block_number: Optional[int] = Field(None, description="区块高度（链上）")
    sender: Optional[str] = Field(None, description="发送方地址（链上）")
    receiver: Optional[str] = Field(None, description="接收方地址（链上）")

    model_config = {"json_encoders": {Decimal: str}}


class TickerEvent(BaseModel):
    """行情事件模型"""

    symbol: str = Field(..., description="交易对符号")
    price: Decimal = Field(..., description="最新价格")
    bid: Optional[Decimal] = Field(None, description="买一价")
    ask: Optional[Decimal] = Field(None, description="卖一价")
    bid_volume: Optional[Decimal] = Field(None, description="买一量")
    ask_volume: Optional[Decimal] = Field(None, description="卖一量")
    volume_24h: Optional[Decimal] = Field(None, description="24小时成交量")
    change_24h: Optional[Decimal] = Field(None, description="24小时涨跌额")
    change_24h_percent: Optional[Decimal] = Field(None, description="24小时涨跌幅%")
    timestamp: datetime = Field(..., description="时间戳")
    source: DataSource = Field(..., description="数据来源")
    market_type: MarketType = Field(default=MarketType.SPOT, description="市场类型")

    model_config = {"json_encoders": {Decimal: str}}


class KlineEvent(BaseModel):
    """K线事件模型"""

    symbol: str = Field(..., description="交易对符号")
    interval: KlineInterval = Field(..., description="周期")
    open: Decimal = Field(..., description="开盘价")
    high: Decimal = Field(..., description="最高价")
    low: Decimal = Field(..., description="最低价")
    close: Decimal = Field(..., description="收盘价")
    volume: Decimal = Field(..., description="成交量")
    amount: Optional[Decimal] = Field(None, description="成交额")
    timestamp: datetime = Field(..., description="K线时间")
    source: DataSource = Field(..., description="数据来源")
    market_type: MarketType = Field(default=MarketType.SPOT, description="市场类型")
    trade_count: Optional[int] = Field(None, description="成交笔数")

    model_config = {"json_encoders": {Decimal: str}}


class OrderBookLevel(BaseModel):
    """订单簿档位"""

    price: Decimal = Field(..., description="价格")
    volume: Decimal = Field(..., description="数量")

    model_config = {"json_encoders": {Decimal: str}}


class OrderBookEvent(BaseModel):
    """订单簿事件模型"""

    symbol: str = Field(..., description="交易对符号")
    bids: List[OrderBookLevel] = Field(default_factory=list, description="买单")
    asks: List[OrderBookLevel] = Field(default_factory=list, description="卖单")
    timestamp: datetime = Field(..., description="时间戳")
    source: DataSource = Field(..., description="数据来源")
    market_type: MarketType = Field(default=MarketType.SPOT, description="市场类型")


class BlockEvent(BaseModel):
    """区块事件模型"""

    chain: str = Field(..., description="链名称")
    block_number: int = Field(..., description="区块高度")
    block_hash: str = Field(..., description="区块哈希")
    timestamp: datetime = Field(..., description="区块时间戳")
    gas_used: int = Field(..., description="Gas使用量")
    gas_limit: int = Field(..., description="Gas限制")
    tx_count: int = Field(..., description="交易数量")
    parent_hash: str = Field(..., description="父区块哈希")
    miner: Optional[str] = Field(None, description="矿工地址")


class TransactionEvent(BaseModel):
    """交易事件模型（链上）"""

    chain: str = Field(..., description="链名称")
    tx_hash: str = Field(..., description="交易哈希")
    block_number: int = Field(..., description="区块高度")
    timestamp: datetime = Field(..., description="时间戳")
    from_address: str = Field(..., description="发送方")
    to_address: Optional[str] = Field(None, description="接收方")
    value: Decimal = Field(default=Decimal("0"), description="转账金额")
    gas_price: Optional[int] = Field(None, description="Gas价格")
    gas_used: Optional[int] = Field(None, description="Gas使用量")
    status: Optional[bool] = Field(None, description="交易状态")
    input_data: Optional[str] = Field(None, description="输入数据")

    model_config = {"json_encoders": {Decimal: str}}


class LogEvent(BaseModel):
    """日志事件模型（合约事件）"""

    chain: str = Field(..., description="链名称")
    tx_hash: str = Field(..., description="交易哈希")
    block_number: int = Field(..., description="区块高度")
    log_index: int = Field(..., description="日志索引")
    address: str = Field(..., description="合约地址")
    topics: List[str] = Field(default_factory=list, description="事件主题")
    data: str = Field(..., description="事件数据")
    timestamp: datetime = Field(..., description="时间戳")
    decoded: Optional[Dict[str, Any]] = Field(None, description="解码后的数据")


class AlertRule(BaseModel):
    """告警规则模型"""

    id: Optional[int] = Field(None, description="规则ID")
    name: str = Field(..., description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    rule_type: str = Field(..., description="规则类型")
    condition_config: Dict[str, Any] = Field(..., description="条件配置")
    severity: str = Field(default="warning", description="严重程度")
    is_active: bool = Field(default=True, description="是否启用")
    created_by: Optional[int] = Field(None, description="创建者ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class Alert(BaseModel):
    """告警记录模型"""

    id: Optional[int] = Field(None, description="告警ID")
    rule_id: int = Field(..., description="规则ID")
    severity: str = Field(..., description="严重程度")
    message: str = Field(..., description="告警消息")
    data: Dict[str, Any] = Field(default_factory=dict, description="触发数据")
    status: str = Field(default="active", description="状态")
    acknowledged_by: Optional[int] = Field(None, description="确认人ID")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    created_at: Optional[datetime] = Field(None, description="创建时间")
