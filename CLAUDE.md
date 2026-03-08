# OpenDune 开发指南

## 概述

本文档是 OpenDune 项目的开发规范和技术指南，旨在帮助开发者快速理解和参与项目开发。

## 项目目标

构建一个高性能、高可用、可扩展的实时加密货币数据分析平台，实现：
- 多源数据（链上+交易所）实时采集
- 毫秒级数据处理和指标计算
- 多维度数据存储和分析
- 灵活的告警和分析能力

## 开发原则

1. **模块化设计**：每个模块职责单一，接口清晰
2. **事件驱动**：基于消息队列的异步通信
3. **配置化**：环境相关配置外置，支持多环境切换
4. **可观测性**：完善的日志、监控、链路追踪
5. **高可用**：故障自动恢复，数据不丢失
6. **可测试性**：单元测试覆盖率 > 80%

## 技术选型说明

### 为什么选这些技术？

| 技术 | 选型理由 |
|------|---------|
| **Python** | 丰富的数据/区块链库，开发效率高，适合数据密集型任务 |
| **Kafka** | 高吞吐、低延迟，支持数据回溯，生态系统成熟 |
| **Flink** | 真正的流处理（非微批），毫秒级延迟，状态管理完善 |
| **MySQL** | 关系型数据存储，支持事务，生态成熟 |
| **Doris** | 高性能OLAP，支持实时导入，兼容MySQL协议 |
| **TDengine** | 专为时序数据优化，高性能写入和查询 |
| **FastAPI** | 高性能异步框架，自动生成文档，类型提示支持 |
| **Redis** | 缓存和分布式锁，高性能内存数据库 |

## 项目结构详解

### 1. common/ - 公共组件

所有模块共享的基础组件：

```python
# config.py - 配置管理
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    kafka_brokers: str = "localhost:9092"
    mysql_url: str = "mysql://user:pass@localhost/db"
    # ... 其他配置

settings = Settings()

# logger.py - 结构化日志
import structlog

logger = structlog.get_logger()
logger.info("event_processed", event_id="123", latency_ms=10)

# models.py - 数据模型
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class TradeEvent(BaseModel):
    symbol: str
    price: Decimal
    quantity: Decimal
    timestamp: datetime
    source: str  # "binance", "ethereum", etc.
```

### 2. data_collection/ - 数据采集

#### 链上数据采集

```python
# onchain/eth_collector.py
from web3 import Web3
from typing import AsyncIterator
import asyncio

class EthereumCollector:
    """Ethereum 数据采集器"""

    def __init__(self, rpc_url: str, kafka_producer):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.producer = kafka_producer
        self.running = False

    async def start(self):
        """启动采集"""
        self.running = True
        # 创建区块过滤器
        block_filter = self.w3.eth.filter('latest')

        while self.running:
            try:
                for block_hash in block_filter.get_new_entries():
                    block = self.w3.eth.get_block(block_hash, full_transactions=True)
                    await self._process_block(block)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("eth_collection_error", error=str(e))
                await asyncio.sleep(5)

    async def _process_block(self, block: dict):
        """处理区块数据"""
        event = {
            "chain": "ethereum",
            "block_number": block.number,
            "block_hash": block.hash.hex(),
            "timestamp": block.timestamp,
            "transactions": [tx.hex() for tx in block.transactions],
            "gas_used": block.gasUsed,
        }
        await self.producer.send("onchain.raw", event)
```

#### 中心化交易所采集

```python
# cex/binance_collector.py
import ccxt.async_support as ccxt
from typing import List

class BinanceCollector:
    """币安数据采集器"""

    def __init__(self, api_key: str = None, secret: str = None):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # or 'future'
            }
        })
        self.symbols: List[str] = []

    async def subscribe_ticker(self, symbols: List[str]):
        """订阅行情数据"""
        self.symbols = symbols

        while True:
            try:
                for symbol in symbols:
                    ticker = await self.exchange.fetch_ticker(symbol)
                    await self._publish_ticker(ticker)
                await asyncio.sleep(1)  # 根据需求调整频率
            except Exception as e:
                logger.error("binance_ticker_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)

    async def subscribe_trades(self, symbols: List[str]):
        """订阅成交数据"""
        for symbol in symbols:
            asyncio.create_task(self._trade_watcher(symbol))

    async def _trade_watcher(self, symbol: str):
        """交易数据监听器"""
        while True:
            try:
                trades = await self.exchange.fetch_trades(symbol, limit=100)
                for trade in trades:
                    await self._publish_trade(trade)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error("trade_watch_error", symbol=symbol, error=str(e))
                await asyncio.sleep(5)
```

### 3. data_processing/ - 数据处理

#### Flink 作业设计

```python
# flink_jobs/metrics_job.py
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.common.typeinfo import Types

class MetricsJob:
    """实时指标计算作业"""

    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.table_env = StreamTableEnvironment.create(self.env)

    def define_pipeline(self):
        """定义处理流程"""

        # 1. 从Kafka读取数据
        self.table_env.execute_sql("""
            CREATE TABLE trade_source (
                symbol STRING,
                price DECIMAL(18, 8),
                quantity DECIMAL(18, 8),
                timestamp TIMESTAMP(3),
                source STRING,
                WATERMARK FOR timestamp AS timestamp - INTERVAL '5' SECOND
            ) WITH (
                'connector' = 'kafka',
                'topic' = 'cex.trades',
                'properties.bootstrap.servers' = 'localhost:9092',
                'format' = 'json'
            )
        """)

        # 2. 计算实时指标
        self.table_env.execute_sql("""
            CREATE TABLE metrics_sink (
                symbol STRING,
                window_start TIMESTAMP(3),
                window_end TIMESTAMP(3),
                avg_price DECIMAL(18, 8),
                total_volume DECIMAL(18, 8),
                trade_count BIGINT,
                PRIMARY KEY (symbol, window_start) NOT ENFORCED
            ) WITH (
                'connector' = 'jdbc',
                'url' = 'jdbc:mysql://localhost:9030/analytics',
                'table-name' = 'trade_metrics',
                'username' = 'root',
                'password' = ''
            )
        """)

        # 3. 执行聚合计算
        self.table_env.execute_sql("""
            INSERT INTO metrics_sink
            SELECT
                symbol,
                TUMBLE_START(timestamp, INTERVAL '1' MINUTE) as window_start,
                TUMBLE_END(timestamp, INTERVAL '1' MINUTE) as window_end,
                AVG(price) as avg_price,
                SUM(price * quantity) as total_volume,
                COUNT(*) as trade_count
            FROM trade_source
            GROUP BY
                symbol,
                TUMBLE(timestamp, INTERVAL '1' MINUTE)
        """)

    def run(self):
        """启动作业"""
        self.define_pipeline()
        self.env.execute("Trade Metrics Job")
```

### 4. data_storage/ - 数据存储

#### 多存储引擎客户端

```python
# base_storage.py
from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseStorage(ABC):
    """存储客户端基类"""

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def write(self, table: str, data: Dict[str, Any]):
        pass

    @abstractmethod
    async def query(self, sql: str, params: tuple = None) -> List[Dict]:
        pass


# tdengine_client.py
import taos
from typing import List, Dict, Any

class TDengineClient(BaseStorage):
    """TDengine 时序数据库客户端"""

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None

    async def connect(self):
        self.conn = taos.connect(**self.conn_params)

    async def write_kline(self, symbol: str, interval: str, data: Dict):
        """写入K线数据"""
        sql = f"""
            INSERT INTO kline_{interval}_{symbol}
            (ts, open, high, low, close, volume, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (
            data['timestamp'],
            data['open'],
            data['high'],
            data['low'],
            data['close'],
            data['volume'],
            data['amount']
        ))
        cursor.close()

    async def query_recent(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """查询最近数据"""
        sql = f"""
            SELECT * FROM kline_{interval}_{symbol}
            ORDER BY ts DESC
            LIMIT {limit}
        """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results
```

### 5. data_service/ - 数据服务

#### FastAPI 服务

```python
# main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await init_connections()
    yield
    # 关闭时清理
    await close_connections()

app = FastAPI(
    title="OpenDune API",
    description="实时加密数据分析平台 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from api import market, trades, alerts, analytics
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# WebSocket 实时推送
@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 订阅Kafka实时数据并推送
            data = await get_realtime_data()
            await websocket.send_json(data)
    except Exception as e:
        await websocket.close()

# api/market.py
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime
from services.market_service import MarketService

router = APIRouter()
market_service = MarketService()

@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """获取最新行情"""
    return await market_service.get_ticker(symbol)

@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query("1m", regex="^(1m|5m|15m|1h|4h|1d)$"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """获取K线数据"""
    return await market_service.get_klines(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )

@router.get("/depth/{symbol}")
async def get_order_book(symbol: str, limit: int = Query(20, ge=1, le=100)):
    """获取订单簿深度"""
    return await market_service.get_order_book(symbol, limit)
```

### 6. data_analysis/ - 数据分析

#### 技术指标计算

```python
# indicators/ma.py
import numpy as np
from typing import List
from decimal import Decimal

class MovingAverage:
    """移动平均线"""

    @staticmethod
    def sma(prices: List[Decimal], period: int) -> List[Decimal]:
        """简单移动平均"""
        prices = [float(p) for p in prices]
        result = []
        for i in range(len(prices)):
            if i < period - 1:
                result.append(None)
            else:
                result.append(Decimal(str(np.mean(prices[i-period+1:i+1]))))
        return result

    @staticmethod
    def ema(prices: List[Decimal], period: int) -> List[Decimal]:
        """指数移动平均"""
        prices = [float(p) for p in prices]
        multiplier = 2 / (period + 1)
        ema = [prices[0]]

        for price in prices[1:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return [Decimal(str(e)) for e in ema]


# alerts/alert_engine.py
from typing import List, Callable
import asyncio

class AlertEngine:
    """告警引擎"""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.handlers: List[Callable] = []

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)

    def add_handler(self, handler: Callable):
        """添加告警处理器"""
        self.handlers.append(handler)

    async def evaluate(self, data: dict):
        """评估数据是否触发告警"""
        for rule in self.rules:
            if rule.evaluate(data):
                alert = Alert(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.message.format(**data),
                    data=data,
                    timestamp=datetime.utcnow()
                )
                await self._trigger_alert(alert)

    async def _trigger_alert(self, alert: Alert):
        """触发告警"""
        # 保存到数据库
        await save_alert(alert)

        # 执行处理器
        for handler in self.handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error("alert_handler_error", handler=handler.__name__, error=str(e))

class AlertRule:
    """告警规则"""

    def __init__(self, id: str, name: str, condition: Callable, severity: str, message: str):
        self.id = id
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message = message

    def evaluate(self, data: dict) -> bool:
        return self.condition(data)
```

## 高可用设计

### 1. 数据采集高可用

```python
# 采集器健康检查和自动重启
import asyncio
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class HealthMonitor:
    """健康监控器"""

    def __init__(self, collectors: List[BaseCollector]):
        self.collectors = collectors
        self.health_status = {}

    async def start_monitoring(self):
        """启动健康检查"""
        while True:
            for collector in self.collectors:
                status = await self._check_health(collector)
                self.health_status[collector.name] = status

                if status == HealthStatus.UNHEALTHY:
                    logger.error("collector_unhealthy", collector=collector.name)
                    await self._restart_collector(collector)

            await asyncio.sleep(30)  # 每30秒检查一次

    async def _check_health(self, collector: BaseCollector) -> HealthStatus:
        """检查采集器健康状态"""
        try:
            # 检查最后数据接收时间
            last_received = collector.last_received_time
            if datetime.utcnow() - last_received > timedelta(minutes=5):
                return HealthStatus.UNHEALTHY

            # 检查错误率
            error_rate = collector.get_error_rate(window_minutes=5)
            if error_rate > 0.5:  # 错误率超过50%
                return HealthStatus.UNHEALTHY
            elif error_rate > 0.1:
                return HealthStatus.DEGRADED

            return HealthStatus.HEALTHY
        except Exception as e:
            logger.error("health_check_error", collector=collector.name, error=str(e))
            return HealthStatus.UNHEALTHY
```

### 2. 消息队列高可用

```python
# Kafka生产者配置（高可用）
from aiokafka import AIOKafkaProducer

async def create_kafka_producer():
    return AIOKafkaProducer(
        bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # 高可用配置
        acks='all',                    # 所有副本确认后才算成功
        retries=3,                     # 失败重试次数
        retry_backoff_ms=1000,         # 重试间隔
        max_in_flight_requests_per_connection=5,
        enable_idempotence=True,       # 幂等性，防止重复发送
        compression_type='lz4',        # 压缩
    )

# 消费者组配置
async def create_kafka_consumer(group_id: str, topics: List[str]):
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=['kafka1:9092', 'kafka2:9092', 'kafka3:9092'],
        group_id=group_id,
        auto_offset_reset='earliest',
        enable_auto_commit=False,      # 手动提交，确保处理完成后再提交
        max_poll_records=500,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
    )
```

### 3. 熔断降级机制

```python
# circuit_breaker.py
import time
from enum import Enum
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"       # 正常
    OPEN = "open"          # 熔断
    HALF_OPEN = "half_open"  # 半开

class CircuitBreaker:
    """熔断器"""

    def __init__(self, failure_threshold=5, recovery_timeout=60, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0

    def call(self, func, *args, **kwargs):
        """执行函数，带熔断保护"""

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerOpen("Circuit breaker half-open limit reached")
            self.half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """成功处理"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _on_failure(self):
        """失败处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# 使用装饰器
def circuit_breaker_decorator(cb: CircuitBreaker):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
```

## 数据库设计

### MySQL 元数据表

```sql
-- 链信息表
CREATE TABLE chains (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain_id INT NOT NULL COMMENT '链ID',
    name VARCHAR(50) NOT NULL COMMENT '链名称',
    symbol VARCHAR(20) NOT NULL COMMENT '代币符号',
    rpc_urls JSON COMMENT 'RPC节点列表',
    explorer_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_chain_id (chain_id)
) ENGINE=InnoDB COMMENT='区块链信息表';

-- 代币信息表
CREATE TABLE tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chain_id INT NOT NULL,
    address VARCHAR(42) NOT NULL COMMENT '合约地址',
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    decimals INT DEFAULT 18,
    is_native BOOLEAN DEFAULT FALSE COMMENT '是否原生代币',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chain_id) REFERENCES chains(chain_id),
    UNIQUE KEY uk_chain_token (chain_id, address)
) ENGINE=InnoDB COMMENT='代币信息表';

-- 告警规则表
CREATE TABLE alert_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type ENUM('price', 'volume', 'custom') NOT NULL,
    condition_config JSON NOT NULL COMMENT '条件配置JSON',
    severity ENUM('info', 'warning', 'critical') DEFAULT 'warning',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='告警规则表';

-- 告警记录表
CREATE TABLE alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_id INT NOT NULL,
    severity ENUM('info', 'warning', 'critical'),
    message TEXT,
    data JSON COMMENT '触发时的数据快照',
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    acknowledged_by INT,
    acknowledged_at TIMESTAMP NULL,
    resolved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='告警记录表';
```

### TDengine 时序数据表

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS crypto KEEP 365 DAYS 10 BLOCKS 6;

-- K线数据超级表
CREATE STABLE IF NOT EXISTS crypto.kline (
    ts TIMESTAMP,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    amount DOUBLE,
    trade_count INT
) TAGS (
    symbol BINARY(50),
    interval VARCHAR(10),
    exchange VARCHAR(20),
    market_type VARCHAR(10)
);

-- 创建子表示例（自动创建）
-- crypto.kline_1m_BTCUSDT_binance_spot
-- crypto.kline_5m_ETHUSDT_binance_spot

-- 实时tick数据超级表
CREATE STABLE IF NOT EXISTS crypto.tick (
    ts TIMESTAMP,
    price DOUBLE,
    volume DOUBLE,
    side TINYINT COMMENT '1=buy, -1=sell',
    order_id NCHAR(64),
    buyer_order_id NCHAR(64),
    seller_order_id NCHAR(64)
) TAGS (
    symbol BINARY(50),
    exchange VARCHAR(20),
    market_type VARCHAR(10)
);

-- 技术指标超级表
CREATE STABLE IF NOT EXISTS crypto.indicator (
    ts TIMESTAMP,
    sma_7 DOUBLE,
    sma_25 DOUBLE,
    sma_99 DOUBLE,
    ema_12 DOUBLE,
    ema_26 DOUBLE,
    rsi_14 DOUBLE,
    macd DOUBLE,
    macd_signal DOUBLE,
    macd_histogram DOUBLE,
    bollinger_upper DOUBLE,
    bollinger_middle DOUBLE,
    bollinger_lower DOUBLE
) TAGS (
    symbol BINARY(50),
    interval VARCHAR(10),
    exchange VARCHAR(20)
);
```

### Doris OLAP表

```sql
-- 交易统计表
CREATE TABLE IF NOT EXISTS trade_stats (
    stat_date DATE,
    stat_hour INT,
    exchange VARCHAR(50),
    symbol VARCHAR(50),
    market_type VARCHAR(20),

    -- 成交量统计
    total_volume DECIMAL(38, 18),
    total_amount DECIMAL(38, 18),
    trade_count BIGINT,

    -- 价格统计
    open_price DECIMAL(38, 18),
    high_price DECIMAL(38, 18),
    low_price DECIMAL(38, 18),
    close_price DECIMAL(38, 18),

    -- 买卖统计
    buy_volume DECIMAL(38, 18),
    sell_volume DECIMAL(38, 18),
    buy_amount DECIMAL(38, 18),
    sell_amount DECIMAL(38, 18),

    -- 波动率
    price_change DECIMAL(38, 18),
    price_change_pct DECIMAL(10, 4),
    volatility DECIMAL(10, 4),

    -- 聚合维度
    dt DATETIME,

    UNIQUE KEY(stat_date, stat_hour, exchange, symbol)
)
DISTRIBUTED BY HASH(exchange, symbol) BUCKETS 32
PROPERTIES (
    "replication_num" = "3",
    "enable_unique_key_merge_on_write" = "true"
);

-- 市场深度分析表
CREATE TABLE IF NOT EXISTS market_depth (
    ts DATETIME,
    exchange VARCHAR(50),
    symbol VARCHAR(50),

    bid_price_l1 DECIMAL(38, 18),
    bid_volume_l1 DECIMAL(38, 18),
    ask_price_l1 DECIMAL(38, 18),
    ask_volume_l1 DECIMAL(38, 18),

    bid_price_l5 DECIMAL(38, 18),
    bid_volume_l5 DECIMAL(38, 18),
    ask_price_l5 DECIMAL(38, 18),
    ask_volume_l5 DECIMAL(38, 18),

    spread DECIMAL(38, 18),
    spread_bps DECIMAL(10, 4),
    mid_price DECIMAL(38, 18),

    bid_depth_ratio DECIMAL(10, 4),
    liquidity_score DECIMAL(10, 4)
)
DUPLICATE KEY(ts, exchange, symbol)
DISTRIBUTED BY HASH(exchange, symbol) BUCKETS 16
PROPERTIES ("replication_num" = "3");
```

## 开发规范

### 代码风格

1. **使用 Black 格式化代码**
```bash
black src/ tests/ --line-length 100
```

2. **类型注解**
```python
from typing import Optional, List, Dict, Any
from decimal import Decimal

def process_trade(
    symbol: str,
    price: Decimal,
    quantity: Decimal,
    metadata: Optional[Dict[str, Any]] = None
) -> TradeResult:
    ...
```

3. **文档字符串**
```python
def calculate_rsi(prices: List[Decimal], period: int = 14) -> Decimal:
    """
    计算RSI指标

    Args:
        prices: 价格列表，按时间顺序排列
        period: RSI计算周期，默认14

    Returns:
        RSI值，范围0-100

    Raises:
        ValueError: 价格数据不足时抛出

    Example:
        >>> prices = [Decimal('100'), Decimal('101'), Decimal('99')]
        >>> rsi = calculate_rsi(prices, period=2)
    """
    ...
```

### 错误处理

```python
from contextlib import asynccontextmanager

class DataCollectionError(Exception):
    """数据采集异常基类"""
    pass

class ExchangeAPIError(DataCollectionError):
    """交易所API异常"""
    def __init__(self, exchange: str, status_code: int, message: str):
        self.exchange = exchange
        self.status_code = status_code
        super().__init__(f"{exchange} API error {status_code}: {message}")

# 使用装饰器统一处理异常
def handle_errors(fallback_value=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ExchangeAPIError as e:
                logger.error("exchange_api_error",
                           exchange=e.exchange,
                           status_code=e.status_code,
                           error=str(e))
                return fallback_value
            except Exception as e:
                logger.exception("unexpected_error", func=func.__name__)
                return fallback_value
        return wrapper
    return decorator
```

### 日志规范

```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 使用示例
logger = structlog.get_logger()

# 好的日志
logger.info(
    "trade_processed",
    symbol="BTCUSDT",
    price=45000.50,
    quantity=1.5,
    latency_ms=12.5,
    source="binance"
)

# 避免
logger.info(f"Trade processed: {symbol} at {price}")  # 不要f-string
```

## 测试规范

### 单元测试

```python
# tests/unit/test_indicators.py
import pytest
from decimal import Decimal
from src.data_analysis.indicators.ma import MovingAverage

class TestMovingAverage:
    def test_sma_calculation(self):
        prices = [Decimal('10'), Decimal('20'), Decimal('30'), Decimal('40')]
        result = MovingAverage.sma(prices, period=3)

        assert result[0] is None
        assert result[1] is None
        assert result[2] == Decimal('20')
        assert result[3] == Decimal('30')

    def test_sma_with_insufficient_data(self):
        prices = [Decimal('10')]
        result = MovingAverage.sma(prices, period=3)
        assert result[0] is None

    @pytest.mark.asyncio
    async def test_collector_start_stop(self):
        collector = MockCollector()
        task = asyncio.create_task(collector.start())

        await asyncio.sleep(0.1)
        await collector.stop()

        assert collector.started is True
        assert collector.stopped is True
```

### 集成测试

```python
# tests/integration/test_kafka_flow.py
import pytest
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope="module")
def kafka():
    with KafkaContainer("confluentinc/cp-kafka:latest") as kafka:
        yield kafka.get_bootstrap_server()

@pytest.mark.asyncio
async def test_produce_consume(kafka):
    producer = await create_kafka_producer([kafka])
    consumer = await create_kafka_consumer([kafka], "test-group", ["test-topic"])

    # 发送消息
    await producer.send("test-topic", {"key": "value"})
    await producer.flush()

    # 消费消息
    msg = await consumer.getone()
    data = json.loads(msg.value)

    assert data["key"] == "value"
```

## 部署指南

### Docker Compose 开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  # MySQL
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: opendune
    volumes:
      - mysql_data:/var/lib/mysql

  # TDengine
  tdengine:
    image: tdengine/tdengine:latest
    ports:
      - "6030:6030"
      - "6041:6041"
    volumes:
      - tdengine_data:/var/lib/taos

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Flink
  jobmanager:
    image: flink:latest
    ports:
      - "8081:8081"
    command: jobmanager
    environment:
      - JOB_MANAGER_RPC_ADDRESS=jobmanager

  taskmanager:
    image: flink:latest
    depends_on:
      - jobmanager
    command: taskmanager
    environment:
      - JOB_MANAGER_RPC_ADDRESS=jobmanager

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./infrastructure/monitoring/grafana:/etc/grafana/provisioning

volumes:
  mysql_data:
  tdengine_data:
```

### 生产环境 K8s 部署

```yaml
# infrastructure/k8s/deployment/collector.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onchain-collector
  namespace: opendune
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onchain-collector
  template:
    metadata:
      labels:
        app: onchain-collector
    spec:
      containers:
      - name: collector
        image: opendune/collector:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: opendune-config
              key: kafka.brokers
        - name: ETC_RPC_URL
          valueFrom:
            secretKeyRef:
              name: opendune-secrets
              key: eth.rpc.url
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 常用命令

```bash
# 启动开发环境
make dev-up

# 运行测试
make test
make test-coverage

# 代码格式化
make format

# 类型检查
make type-check

# 构建镜像
make build-image

# 部署到K8s
make k8s-deploy

# 查看日志
make logs SERVICE=collector

# 数据库迁移
make migrate
make migrate-rollback
```

## 性能优化建议

1. **Kafka调优**
   - 分区数 = max(期望吞吐量 / 单分区吞吐量, 消费者实例数)
   - 批量发送：linger.ms=10, batch.size=16384

2. **Flink调优**
   - 合理设置并行度
   - 启用检查点：checkpoint间隔根据延迟要求设置
   - 使用RocksDB状态后端

3. **数据库调优**
   - TDengine：根据数据量调整cache和blocks
   - Doris：合理设置分桶数
   - 建立合适的索引

4. **Python代码优化**
   - 使用asyncio进行IO密集型操作
   - 使用ujson替代json
   - 使用lru_cache缓存热点数据

## 安全考虑

1. **API Key管理**
   - 使用K8s Secrets或Vault
   - 定期轮换
   - 最小权限原则

2. **数据加密**
   - 传输层使用TLS
   - 敏感数据加密存储

3. **访问控制**
   - API认证（JWT）
   - 速率限制
   - IP白名单

4. **审计日志**
   - 记录所有重要操作
   - 日志保留策略

## 链上数据采集方案

**已确认方案：Alchemy**

我们使用 Alchemy 作为链上数据采集的主要方案，理由如下：

1. **稳定性**：99.9%+ 的可用性保证，全球分布式节点
2. **功能丰富**：支持 WebSocket、Webhooks、NFT API、Trace API 等
3. **多链支持**：Ethereum、Polygon、Arbitrum、Optimism、Base 等主流链
4. **免费额度充足**：开发阶段免费版足够使用
5. **开发者友好**：完善的文档和SDK支持

### Alchemy 配置

```python
# 支持的链和网络配置
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
    "bsc": {
        # BSC 使用其他节点，Alchemy 不直接支持
        "mainnet": "https://bsc-dataseed.binance.org",
        "testnet": "https://data-seed-prebsc-1-s1.binance.org:8545"
    }
}

# Alchemy 采集器示例
from alchemy import Alchemy

class AlchemyCollector:
    """Alchemy 链上数据采集器"""

    def __init__(self, api_key: str, network: str = "eth-mainnet"):
        self.alchemy = Alchemy(api_key=api_key, network=network)
        self.ws_url = f"wss://{network}.g.alchemy.com/v2/{api_key}"
        self.http_url = f"https://{network}.g.alchemy.com/v2/{api_key}"

    async def subscribe_blocks(self, callback):
        """订阅新区块"""
        import websockets
        import json

        async with websockets.connect(self.ws_url) as ws:
            # 订阅新区块
            subscribe_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_subscribe",
                "params": ["newHeads"]
            }
            await ws.send(json.dumps(subscribe_msg))

            while True:
                message = await ws.recv()
                data = json.loads(message)
                if "params" in data:
                    await callback(data["params"]["result"])

    async def get_block_with_txs(self, block_number: int) -> dict:
        """获取完整区块数据（含交易）"""
        return await self.alchemy.core.get_block(block_number, full_tx=True)

    async def get_logs(self, from_block: int, to_block: int, address: str = None) -> list:
        """获取事件日志"""
        params = {
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
        }
        if address:
            params["address"] = address
        return await self.alchemy.core.get_logs(params)

    async def get_token_transfers(
        self,
        from_block: str = "latest",
        to_block: str = "latest",
        contract_address: str = None,
        from_address: str = None,
        to_address: str = None
    ) -> list:
        """获取代币转账记录（Alchemy 特有 API）"""
        return await self.alchemy.core.get_asset_transfers({
            "fromBlock": from_block,
            "toBlock": to_block,
            "contractAddresses": [contract_address] if contract_address else None,
            "fromAddress": from_address,
            "toAddress": to_address,
            "category": ["erc20", "erc721", "erc1155"]
        })
```

### 备用方案

虽然 Alchemy 是主要方案，但建议配置备用节点以防万一：

```python
# 多节点故障转移
class MultiNodeProvider:
    """多节点故障转移提供者"""

    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.current_index = 0
        self.circuit_breakers = {url: CircuitBreaker() for url in endpoints}

    async def call(self, method: str, params: list = None) -> dict:
        """调用RPC方法，自动故障转移"""
        attempts = 0
        max_attempts = len(self.endpoints)

        while attempts < max_attempts:
            endpoint = self.endpoints[self.current_index]
            cb = self.circuit_breakers[endpoint]

            try:
                if cb.state == CircuitState.OPEN:
                    raise CircuitBreakerOpen(f"Circuit open for {endpoint}")

                result = await self._rpc_call(endpoint, method, params)
                cb._on_success()
                return result

            except Exception as e:
                cb._on_failure()
                logger.warning("rpc_call_failed",
                             endpoint=endpoint,
                             method=method,
                             error=str(e))
                self.current_index = (self.current_index + 1) % len(self.endpoints)
                attempts += 1

        raise Exception("All RPC endpoints failed")
```
