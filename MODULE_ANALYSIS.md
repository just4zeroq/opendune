# OpenDune 模块功能分析与任务清单

## 项目概览

OpenDune 是一个实时加密货币数据分析平台，支持链上数据（EVM兼容链）和中心化交易所数据的采集、处理、存储、分析和展示。

---

## 一、数据采集层 (Data Collection)

### 1.1 链上数据采集 (On-Chain)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Alchemy采集器** | `src/data_collection/onchain/alchemy_collector.py` | 基于Alchemy API的链上数据采集，支持WebSocket实时订阅区块、交易、事件日志 | ✅ 已完成 | 90% |
| **多节点提供者** | `src/data_collection/onchain/multi_node_provider.py` | 多RPC节点故障转移、熔断保护、负载均衡 | ✅ 已完成 | 85% |
| **链管理器** | `src/data_collection/onchain/chain_manager.py` | 统一管理Ethereum、BSC、Polygon、Arbitrum、Base多链采集 | ✅ 已完成 | 80% |

**已完成功能：**
- [x] Alchemy WebSocket订阅新区块
- [x] Alchemy HTTP API查询区块/交易/日志
- [x] BSC公共节点轮询采集（Alchemy不支持BSC）
- [x] 多节点故障转移机制
- [x] 熔断器保护
- [x] 链上数据标准化模型

**待完成任务：**
- [ ] 合约事件ABI解码
- [ ] 代币转账追踪优化
- [ ] 链上数据确认数监控
- [ ] 更多链的支持（Optimism、Avalanche等）

---

### 1.2 中心化交易所采集 (CEX)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **币安采集器** | `src/data_collection/cex/binance_collector.py` | 币安现货/合约数据：Ticker、K线、成交、订单簿 | ✅ 已完成 | 85% |
| **OKX采集器** | `src/data_collection/cex/okx_collector.py` | OKX数据：行情、成交、K线 | ✅ 已完成 | 80% |
| **Bybit采集器** | `src/data_collection/cex/bybit_collector.py` | Bybit数据：行情、成交、K线 | ✅ 已完成 | 80% |
| **Bitget采集器** | `src/data_collection/cex/bitget_collector.py` | Bitget数据：行情、成交、K线 | ✅ 已完成 | 80% |
| **CEX管理器** | `src/data_collection/cex/cex_manager.py` | 统一管理多个交易所采集器 | ✅ 已完成 | 75% |

**已完成功能：**
- [x] CCXT统一接口封装
- [x] 实时Ticker数据采集
- [x] 实时成交数据(Trades)
- [x] K线数据(OHLCV)
- [x] 订单簿深度数据
- [x] 异步并发采集
- [x] 交易所API限流处理

**待完成任务：**
- [ ] WebSocket实时连接（当前使用轮询）
- [ ] 订单簿增量更新
- [ ] 资金费率采集（合约）
- [ ] 持仓数据采集
- [ ] 更细粒度的错误重试

---

## 二、消息队列层 (Message Queue)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Kafka生产者** | `src/common/kafka_client.py` | 异步Kafka消息生产者，支持批量发送、压缩、幂等性 | ✅ 已完成 | 85% |
| **Kafka消费者** | `src/common/kafka_client.py` | 消费者组管理、手动提交、背压控制 | ✅ 已完成 | 80% |

**已完成功能：**
- [x] 异步Kafka生产者
- [x] JSON序列化
- [x] LZ4压缩
- [x] 幂等性保证
- [x] 消费者组管理
- [x] 手动偏移量提交

**Topic设计：**
| Topic | 用途 | 分区数 | 状态 |
|-------|------|--------|------|
| onchain.blocks | 区块数据 | 6 | ✅ |
| onchain.transactions | 交易数据 | 6 | ✅ |
| onchain.logs | 事件日志 | 6 | ✅ |
| cex.ticker | 行情数据 | 6 | ✅ |
| cex.trades | 成交数据 | 12 | ✅ |
| cex.klines | K线数据 | 6 | ✅ |
| alerts | 告警消息 | 3 | ✅ |

**待完成任务：**
- [ ] Schema Registry集成（Avro/Protobuf）
- [ ] 死信队列(DLQ)
- [ ] 消息追踪(Msg Tracing)

---

## 三、实时处理层 (Stream Processing)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Flink ETL作业** | `src/data_processing/flink_jobs/etl_job.py` (待创建) | 数据清洗、格式转换、标准化 | ⏳ 待开发 | 0% |
| **Flink指标计算** | `src/data_processing/flink_jobs/metrics_job.py` (待创建) | 实时指标计算：价格聚合、成交量统计 | ⏳ 待开发 | 0% |
| **Flink聚合作业** | `src/data_processing/flink_jobs/aggregation_job.py` (待创建) | 窗口聚合：分钟/小时/日K线生成 | ⏳ 待开发 | 0% |
| **异常检测作业** | `src/data_processing/flink_jobs/anomaly_detection.py` (待创建) | 异常交易检测、价格波动预警 | ⏳ 待开发 | 0% |

**待完成任务：**
- [ ] PyFlink环境搭建
- [ ] Kafka Source连接器
- [ ] 多Sink输出（Doris/TDengine/Redis）
- [ ] 事件时间处理和水印
- [ ] Checkpoint状态管理
- [ ] 窗口聚合逻辑（Tumbling/Sliding/Session）
- [ ] 异常检测算法集成

---

## 四、数据存储层 (Data Storage)

### 4.1 MySQL - 元数据存储

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **MySQL客户端** | `src/data_storage/mysql_client.py` | 异步MySQL连接池、CRUD操作 | ✅ 已完成 | 80% |

**已完成功能：**
- [x] 异步连接池
- [x] SQL执行和查询
- [x] 事务支持

**数据表：**
| 表名 | 用途 | 状态 |
|------|------|------|
| chains | 区块链信息 | ✅ 已设计 |
| tokens | 代币信息 | ✅ 已设计 |
| trading_pairs | 交易对信息 | ✅ 已设计 |
| alert_rules | 告警规则 | ✅ 已设计 |
| alerts | 告警记录 | ✅ 已设计 |
| system_configs | 系统配置 | ✅ 已设计 |

---

### 4.2 TDengine - 时序数据存储

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **TDengine客户端** | `src/data_storage/tdengine_client.py` | 时序数据库连接、超级表管理 | ✅ 已完成 | 75% |

**已完成功能：**
- [x] 数据库连接
- [x] 超级表创建
- [x] K线数据写入
- [x] Tick数据写入

**超级表设计：**
| 超级表 | 用途 | 状态 |
|--------|------|------|
| kline | K线数据（开高低收成交量） | ✅ 已设计 |
| tick | Tick成交数据 | ✅ 已设计 |
| indicator | 技术指标数据 | ✅ 已设计 |

---

### 4.3 Doris - OLAP分析存储

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Doris客户端** | `src/data_storage/doris_client.py` | OLAP分析查询 | ✅ 已完成 | 70% |

**数据表：**
| 表名 | 用途 | 状态 |
|------|------|------|
| trade_stats | 交易统计报表 | ✅ 已设计 |
| market_depth | 市场深度分析 | ✅ 已设计 |
| price_analytics | 价格分析 | 📝 待创建 |
| volume_report | 成交量报表 | 📝 待创建 |

---

### 4.4 Redis - 缓存层

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Redis客户端** | `src/data_storage/redis_client.py` | 缓存、分布式锁、Pub/Sub | ✅ 已完成 | 80% |

**已完成功能：**
- [x] 异步Redis连接
- [x] 键值存储/读取
- [x] JSON序列化
- [x] TTL过期设置

**缓存策略：**
| 数据类型 | 缓存Key格式 | TTL |
|----------|-------------|-----|
| 行情数据 | `ticker:{exchange}:{symbol}` | 5s |
| 订单簿 | `orderbook:{exchange}:{symbol}` | 3s |
| K线数据 | `klines:{symbol}:{interval}` | 60s |
| 热点数据 | 根据访问频率动态调整 | - |

---

## 五、数据服务层 (Data Service)

### 5.1 API服务

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **FastAPI主应用** | `src/data_service/main.py` | FastAPI应用入口、生命周期管理 | ✅ 已完成 | 85% |
| **行情API** | `src/data_service/api/market.py` | Ticker、K线、深度、交易所列表 | ✅ 已完成 | 80% |
| **交易API** | `src/data_service/api/trades.py` | 成交记录、交易统计、成交量分析 | ✅ 已完成 | 75% |
| **告警API** | `src/data_service/api/alerts.py` | 告警规则CRUD、告警历史 | ✅ 已完成 | 75% |
| **分析API** | `src/data_service/api/analytics.py` | 技术指标、趋势分析、相关性、流动性 | ✅ 已完成 | 60% |

**已完成功能：**
- [x] RESTful API设计
- [x] 自动Swagger文档
- [x] CORS跨域支持
- [x] Pydantic数据验证
- [x] 异步路由处理

**待完成任务：**
- [ ] JWT认证中间件
- [ ] 速率限制（Rate Limiting）
- [ ] API版本控制
- [ ] 请求/响应日志
- [ ] WebSocket实时推送
- [ ] GraphQL接口

---

### 5.2 业务服务

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **行情服务** | `src/data_service/services/market_service.py` | 行情数据查询、缓存管理 | ✅ 已完成 | 70% |
| **交易服务** | `src/data_service/services/trade_service.py` | 成交数据查询、统计分析 | ✅ 已完成 | 65% |
| **告警服务** | `src/data_service/services/alert_service.py` | 告警规则管理、告警触发 | ✅ 已完成 | 60% |

**待完成任务：**
- [ ] 复杂查询优化
- [ ] 数据聚合计算
- [ ] 缓存穿透/击穿防护

---

## 六、数据分析层 (Data Analysis)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **技术指标** | `src/data_analysis/indicators/` (待创建) | MA、EMA、RSI、MACD、布林带等 | ⏳ 待开发 | 0% |
| **策略分析** | `src/data_analysis/strategies/` (待创建) | 交易策略回测、信号生成 | ⏳ 待开发 | 0% |
| **告警引擎** | `src/data_analysis/alerts/` (待创建) | 实时告警检测、规则匹配 | ⏳ 待开发 | 0% |

**待完成指标：**
- [ ] 移动平均线（SMA/EMA/WMA）
- [ ] RSI相对强弱指数
- [ ] MACD指标
- [ ] 布林带（Bollinger Bands）
- [ ] 成交量指标（OBV/VWAP）
- [ ] 波动率指标（ATR）

---

## 七、数据展示层 (Visualization)

### 7.1 Vue前端

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **项目配置** | `src/data_visualization/web/` | Vue3 + Vite + TypeScript + Element Plus | ✅ 已完成 | 90% |
| **布局组件** | `src/components/Layout.vue` | 侧边栏导航、顶部Header | ✅ 已完成 | 85% |
| **数据大盘** | `src/views/Dashboard.vue` | 统计卡片、价格走势、交易所占比、实时成交、告警 | ✅ 已完成 | 80% |
| **行情页面** | `src/views/Market.vue` | 行情列表、K线图、深度图 | ✅ 已完成 | 75% |
| **交易页面** | `src/views/Trades.vue` | 实时成交流、交易统计、交易所分布 | ✅ 已完成 | 75% |
| **链上页面** | `src/views/OnChain.vue` | 链上概览、最新区块、大额转账 | ✅ 已完成 | 75% |
| **告警页面** | `src/views/Alerts.vue` | 告警规则管理、告警历史 | ✅ 已完成 | 75% |
| **分析页面** | `src/views/Analytics.vue` | 技术指标、趋势分析、相关性、流动性 | ✅ 已完成 | 70% |
| **状态管理** | `src/stores/index.ts` | Pinia状态管理 | ✅ 已完成 | 70% |
| **API封装** | `src/api/` | Axios封装、API模块 | ✅ 已完成 | 75% |

**已完成功能：**
- [x] Vue 3 Composition API
- [x] Element Plus组件库
- [x] ECharts图表集成
- [x] Pinia状态管理
- [x] Vue Router路由
- [x] 响应式布局

**待完成任务：**
- [ ] WebSocket实时数据推送
- [ ] 深色模式主题
- [ ] 数据导出功能
- [ ] 移动端适配优化

---

### 7.2 Grafana仪表盘

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| 价格监控面板 | 多交易对价格对比 | 📝 待配置 |
| 交易量面板 | 成交量趋势、分布 | 📝 待配置 |
| 链上数据面板 | 区块、Gas、TPS监控 | 📝 待配置 |
| 告警面板 | 告警统计、趋势 | 📝 待配置 |
| 系统监控面板 | 服务健康状态 | 📝 待配置 |

---

## 八、基础设施 (Infrastructure)

### 8.1 Docker部署

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **Dockerfile** | `infrastructure/docker/Dockerfile.app` | Python应用镜像 | ✅ 已完成 | 80% |
| **Compose配置** | `docker-compose.yml` | 全栈开发环境 | ✅ 已完成 | 85% |

**已完成功能：**
- [x] 应用Dockerfile
- [x] Docker Compose编排
- [x] Kafka + Zookeeper
- [x] MySQL
- [x] TDengine
- [x] Redis
- [x] Flink (JobManager/TaskManager)
- [x] Grafana
- [x] Prometheus

---

### 8.2 Kubernetes (待开发)

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| Namespace配置 | 命名空间隔离 | 📝 待创建 |
| ConfigMap | 配置管理 | 📝 待创建 |
| Secret | 密钥管理 | 📝 待创建 |
| Deployment | 应用部署 | 📝 待创建 |
| Service | 服务暴露 | 📝 待创建 |
| Ingress | 流量入口 | 📝 待创建 |
| HPA | 自动扩缩容 | 📝 待创建 |

---

## 九、监控与运维

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| **Prometheus** | 指标采集、时序存储 | ✅ Docker配置 |
| **Grafana** | 可视化仪表盘 | ✅ Docker配置 |
| **结构化日志** | JSON格式日志、链路追踪 | ✅ 已实现 |
| **健康检查** | 服务健康状态端点 | 📝 待完善 |
| **告警通知** | 钉钉/飞书/邮件通知 | 📝 待开发 |

---

## 十、公共组件 (Common)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **配置管理** | `src/common/config.py` | Pydantic Settings环境配置 | ✅ 已完成 | 90% |
| **日志工具** | `src/common/logger.py` | Structlog结构化日志 | ✅ 已完成 | 90% |
| **异常定义** | `src/common/exceptions.py` | 自定义异常类 | ✅ 已完成 | 90% |
| **数据模型** | `src/common/models.py` | Pydantic数据模型 | ✅ 已完成 | 85% |
| **Kafka客户端** | `src/common/kafka_client.py` | 生产者/消费者封装 | ✅ 已完成 | 85% |

---

## 十一、脚本工具 (Scripts)

| 模块 | 文件路径 | 功能描述 | 状态 | 完成度 |
|------|----------|----------|------|--------|
| **数据库初始化** | `scripts/init_db.py` | MySQL/TDengine表结构初始化 | ✅ 已完成 | 80% |
| **启动采集器** | `scripts/start_collector.py` | 统一启动链上+CEX采集 | ✅ 已完成 | 80% |
| **启动API** | `scripts/start_api.py` | FastAPI服务启动 | ✅ 已完成 | 85% |
| **健康检查** | `scripts/health_check.py` (待创建) | 服务健康状态检查 | ⏳ 待开发 | 0% |

---

## 整体进度统计

### 按模块统计

| 层级 | 模块数 | 已完成 | 进行中 | 待开发 | 完成率 |
|------|--------|--------|--------|--------|--------|
| 数据采集 | 8 | 7 | 1 | 0 | 88% |
| 消息队列 | 2 | 2 | 0 | 0 | 100% |
| 实时处理 | 4 | 0 | 0 | 4 | 0% |
| 数据存储 | 4 | 4 | 0 | 0 | 100% |
| 数据服务 | 7 | 7 | 0 | 0 | 100% |
| 数据分析 | 3 | 0 | 0 | 3 | 0% |
| 数据展示 | 10 | 10 | 0 | 0 | 100% |
| 基础设施 | 2 | 2 | 0 | 0 | 100% |
| **总计** | **40** | **32** | **1** | **7** | **80%** |

### 关键路径

**第一阶段（已完成）：**
- ✅ 基础架构搭建
- ✅ 数据采集模块
- ✅ 消息队列集成
- ✅ 数据存储客户端
- ✅ API服务框架
- ✅ Vue前端基础

**第二阶段（待开发）：**
- ⏳ Flink实时处理作业
- ⏳ 数据分析指标计算
- ⏳ 告警引擎
- ⏳ WebSocket实时推送

**第三阶段（规划中）：**
- 📋 Kubernetes部署
- 📋 Grafana仪表盘配置
- 📋 性能优化
- 📋 监控告警完善

---

## 使用说明

### 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/just4zeroq/opendune.git
cd opendune

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入API Key

# 3. 启动基础设施
make dev-up

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动数据采集
python scripts/start_collector.py

# 6. 启动API服务
python scripts/start_api.py

# 7. 启动前端
cd src/data_visualization/web && npm install && npm run dev
```

### 访问地址

- API文档: http://localhost:8000/docs
- Vue前端: http://localhost:3000
- Kafka UI: http://localhost:8080
- Grafana: http://localhost:3000
