# OpenDune - 实时加密数据分析平台

## 项目简介

OpenDune 是一个高性能的实时加密货币数据分析平台，同时支持链上数据（EVM兼容链）和中心化交易所数据（币安、OKX等）的采集、处理、存储和分析。

## 核心特性

- **多源数据采集**：支持主流EVM链（Ethereum、BSC、Polygon等）和中心化交易所
- **实时流处理**：基于 Apache Flink 的毫秒级数据处理
- **多存储引擎**：MySQL（元数据）、Doris（OLAP分析）、TDengine（时序数据）
- **事件驱动架构**：基于 Kafka 的消息驱动，支持水平扩展
- **高可用设计**：多实例部署、自动故障转移、熔断降级
- **模块化设计**：各组件松耦合，可独立部署和扩展

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据采集层 (Data Collection)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Ethereum    │  │    BSC       │  │   Polygon    │  │   其他EVM    │    │
│  │  Web3.py     │  │  Web3.py     │  │  Web3.py     │  │  Web3.py     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │            │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐    │
│  │    币安      │  │    OKX       │  │   Bybit      │  │  其他CEX     │    │
│  │   CCXT       │  │   CCXT       │  │   CCXT       │  │   CCXT       │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │                 │
          └─────────────────┴─────────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            消息队列层 (Message Queue)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Apache Kafka                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │ onchain.raw │  │  cex.ticker │  │ cex.trades  │  │onchain.logs│ │   │
│  │  │onchain.tx   │  │  cex.order  │  │ cex.kline   │  │onchain.event│ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          实时处理层 (Stream Processing)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Apache Flink Cluster                           │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │ 数据清洗    │  │ 指标计算    │  │ 异常检测    │  │ 数据聚合   │ │   │
│  │  │ ETL Job     │  │ Metrics Job │  │ Anomaly Job │  │ Agg Job    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │ 价格聚合    │  │ 交易量统计  │  │ 告警触发    │                 │   │
│  │  │ Price Agg   │  │ Volume Stats│  │ Alert Job   │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据存储层 (Data Storage)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    MySQL        │  │     Doris       │  │   TDengine      │             │
│  │                 │  │                 │  │                 │             │
│  │  元数据管理     │  │  OLAP分析       │  │  时序数据       │             │
│  │  用户数据       │  │  复杂查询       │  │  K线数据        │             │
│  │  配置信息       │  │  报表统计       │  │  指标数据       │             │
│  │  告警规则       │  │  多维分析       │  │  交易流数据     │             │
│  │                 │  │                 │  │                 │             │
│  │  表:            │  │  表:            │  │  超级表:        │             │
│  │  - users        │  │  - trade_stats  │  │  - kline_1m     │             │
│  │  - chains       │  │  - market_depth │  │  - kline_5m     │             │
│  │  - tokens       │  │  - price_analytics│  - tick_data    │             │
│  │  - alerts       │  │  - volume_report│  │  - indicators   │             │
│  │  - configs      │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Redis (Cache Layer)                            │   │
│  │  - 热点数据缓存                                                     │   │
│  │  - 会话管理                                                         │   │
│  │  - 实时指标缓存                                                     │   │
│  │  - 分布式锁                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ClickHouse (可选扩展)                            │   │
│  │  - 日志存储                                                         │   │
│  │  - 审计数据                                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           数据服务层 (Data Service)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      API Gateway (Kong/Nginx)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                                 ▼                                     │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │ │
│  │  │  REST API   │  │ WebSocket   │  │  GraphQL    │  │  gRPC      │  │ │
│  │  │  (FastAPI)  │  │  实时推送   │  │  查询接口   │  │ 内部服务   │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │ │
│  │                                                                     │ │
│  │  核心服务:                                                          │ │
│  │  - MarketService: 行情数据查询                                      │ │
│  │  - TradeService: 交易数据分析                                       │ │
│  │  - AlertService: 告警管理服务                                       │ │
│  │  - UserService: 用户管理服务                                        │ │
│  │  - AnalyticsService: 高级分析                                       │ │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          数据展示层 (Visualization)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │   Grafana   │  │  自定义前端  │  │   Admin     │  │  Mobile App  │       │
│  │  (Dashboard)│  │  (React/Vue)│  │   Panel     │  │  (可选)      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术选型 | 用途 |
|------|---------|------|
| 数据采集 | Python, Web3.py, CCXT | 链上和交易所数据采集 |
| 消息队列 | Apache Kafka | 数据缓冲和分发 |
| 流处理 | Apache Flink | 实时数据处理 |
| 数据存储 | MySQL, Doris, TDengine | 多引擎存储 |
| 缓存 | Redis | 热点数据缓存 |
| API服务 | FastAPI, WebSocket | 数据服务接口 |
| 可视化 | Grafana, React | 数据展示 |
| 运维 | Docker, K8s, Prometheus | 容器化和监控 |

## 项目结构

```
opendune/
├── README.md                   # 项目说明
├── CLAUDE.md                   # 开发指南
├── requirements.txt            # Python依赖
├── docker-compose.yml          # 本地开发环境
├── Makefile                    # 常用命令
├── config/                     # 配置文件
│   ├── application.yml         # 主配置
│   ├── kafka/                  # Kafka配置
│   ├── flink/                  # Flink配置
│   └── log/                    # 日志配置
├── src/                        # 源代码
│   ├── common/                 # 公共组件
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── logger.py           # 日志工具
│   │   ├── exceptions.py       # 异常定义
│   │   ├── models.py           # 数据模型
│   │   ├── utils.py            # 工具函数
│   │   └── kafka_client.py     # Kafka客户端
│   │
│   ├── data_collection/        # 数据采集模块
│   │   ├── __init__.py
│   │   ├── base_collector.py   # 采集器基类
│   │   ├── onchain/            # 链上数据采集
│   │   │   ├── __init__.py
│   │   │   ├── eth_collector.py    # Ethereum采集器
│   │   │   ├── bsc_collector.py    # BSC采集器
│   │   │   ├── polygon_collector.py # Polygon采集器
│   │   │   └── contract_monitor.py # 合约监控
│   │   │
│   │   └── cex/                # 中心化交易所采集
│   │       ├── __init__.py
│   │       ├── binance_collector.py
│   │       ├── okx_collector.py
│   │       └── cex_manager.py  # CEX管理器
│   │
│   ├── data_processing/        # 数据处理模块 (Flink)
│   │   ├── __init__.py
│   │   ├── flink_jobs/         # Flink作业
│   │   │   ├── __init__.py
│   │   │   ├── etl_job.py      # 数据清洗
│   │   │   ├── metrics_job.py  # 指标计算
│   │   │   ├── aggregation_job.py  # 数据聚合
│   │   │   └── anomaly_detection.py  # 异常检测
│   │   │
│   │   └── processors/         # 处理器
│   │       ├── __init__.py
│   │       ├── price_processor.py
│   │       └── volume_processor.py
│   │
│   ├── data_storage/           # 数据存储模块
│   │   ├── __init__.py
│   │   ├── base_storage.py     # 存储基类
│   │   ├── mysql_client.py     # MySQL客户端
│   │   ├── doris_client.py     # Doris客户端
│   │   ├── tdengine_client.py  # TDengine客户端
│   │   ├── redis_client.py     # Redis客户端
│   │   └── migration/          # 数据库迁移
│   │       ├── mysql/
│   │       ├── doris/
│   │       └── tdengine/
│   │
│   ├── data_service/           # 数据服务模块
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI入口
│   │   ├── api/                # API路由
│   │   │   ├── __init__.py
│   │   │   ├── market.py       # 行情API
│   │   │   ├── trades.py       # 交易API
│   │   │   ├── alerts.py       # 告警API
│   │   │   └── analytics.py    # 分析API
│   │   │
│   │   ├── services/           # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── market_service.py
│   │   │   ├── trade_service.py
│   │   │   └── alert_service.py
│   │   │
│   │   ├── websocket/          # WebSocket服务
│   │   │   ├── __init__.py
│   │   │   └── ws_server.py
│   │   │
│   │   └── middleware/         # 中间件
│   │       ├── auth.py
│   │       ├── rate_limit.py
│   │       └── cors.py
│   │
│   ├── data_analysis/          # 数据分析模块
│   │   ├── __init__.py
│   │   ├── indicators/         # 技术指标
│   │   │   ├── __init__.py
│   │   │   ├── ma.py           # 移动平均线
│   │   │   ├── rsi.py          # RSI指标
│   │   │   ├── macd.py         # MACD指标
│   │   │   └── bollinger.py    # 布林带
│   │   │
│   │   ├── strategies/         # 策略分析
│   │   │   ├── __init__.py
│   │   │   └── base_strategy.py
│   │   │
│   │   └── alerts/             # 告警系统
│   │       ├── __init__.py
│   │       ├── alert_engine.py
│   │       └── rules.py
│   │
│   └── data_visualization/     # 数据展示模块
│       ├── __init__.py
│       ├── dashboards/         # Grafana仪表盘
│       └── web/                # Web前端（可选）
│
├── infrastructure/             # 基础设施
│   ├── docker/                 # Docker配置
│   │   ├── Dockerfile.app
│   │   ├── Dockerfile.flink
│   │   └── Dockerfile.kafka
│   │
│   ├── k8s/                    # Kubernetes配置
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── deployment/
│   │   └── service/
│   │
│   ├── terraform/              # 基础设施即代码
│   └── monitoring/             # 监控配置
│       ├── prometheus/
│       ├── grafana/
│       └── alertmanager/
│
├── tests/                      # 测试
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── scripts/                    # 脚本
│   ├── init_db.py              # 数据库初始化
│   ├── start_collector.py      # 启动采集器
│   ├── start_api.py            # 启动API服务
│   └── health_check.py         # 健康检查
│
└── docs/                       # 文档
    ├── architecture/           # 架构文档
    ├── api/                    # API文档
    └── deployment/             # 部署文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (前端开发)

### 本地开发环境启动

```bash
# 1. 克隆项目
git clone https://github.com/your-org/opendune.git
cd opendune

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动基础设施服务
docker-compose up -d kafka mysql doris tdengine redis

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动数据采集
python scripts/start_collector.py --mode onchain,cex

# 7. 启动API服务
python scripts/start_api.py
```

### 访问服务

- API文档: http://localhost:8000/docs
- Grafana: http://localhost:3000
- Kafka UI: http://localhost:8080

## 数据采集说明

### 链上数据采集

使用 Web3.py 连接 EVM 节点，支持：
- 区块数据监听
- 交易事件监听
- 合约事件解码
- 余额查询

### 中心化交易所采集

使用 CCXT 库统一接入：
- 行情数据（Ticker、K线）
- 交易数据（成交、订单簿）
- 账户数据（需要API Key）

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页: https://github.com/your-org/opendune
- 问题反馈: https://github.com/your-org/opendune/issues
- 邮箱: contact@opendune.io
