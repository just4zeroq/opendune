# 实时处理模块 (Flink) - 待开发任务清单

> 状态: ⏳ 待开发
> 优先级: 🔴 高
> 依赖: Kafka, PyFlink

---

## 环境搭建

### PyFlink安装
- [ ] 安装Apache Flink (版本1.18+)
- [ ] 安装PyFlink依赖
- [ ] 配置Python环境
- [ ] 验证安装

### 开发环境
- [ ] 本地Flink集群配置
- [ ] Flink Web UI访问配置
- [ ] 与Docker Compose集成
- [ ] 调试环境配置

---

## Flink作业开发

### 1. ETL数据清洗作业 `src/data_processing/flink_jobs/etl_job.py`

#### 数据摄取
- [ ] Kafka Source连接器配置
  - [ ] 消费 onchain.blocks Topic
  - [ ] 消费 onchain.transactions Topic
  - [ ] 消费 cex.ticker Topic
  - [ ] 消费 cex.trades Topic
  - [ ] 消费 cex.klines Topic

#### 数据清洗
- [ ] 数据格式验证
- [ ] 缺失值处理
- [ ] 异常值过滤
- [ ] 数据类型转换
- [ ] 时间戳标准化 (UTC)

#### 数据标准化
- [ ] 统一数据Schema
- [ ] 字段命名规范化
- [ ] 价格精度统一
- [ ] 符号格式统一 (BTC/USDT -> BTCUSDT)

#### 数据输出
- [ ] 清洗后数据写入 Kafka Topic: processed.data
- [ ] 错误数据写入 Kafka Topic: error.data

---

### 2. 指标计算作业 `src/data_processing/flink_jobs/metrics_job.py`

#### 实时价格指标
- [ ] 最新价格计算
  - [ ] 多交易所价格聚合
  - [ ] 加权平均价格 (VWAP)
  - [ ] 价格偏差检测

#### 成交量指标
- [ ] 实时成交量统计
  - [ ] 分交易所成交量
  - [ ] 买卖方向成交量
  - [ ] 累计成交量

#### 波动率指标
- [ ] 实时价格波动计算
  - [ ] 分钟级波动率
  - [ ] 5分钟波动率
  - [ ] 异常波动检测

#### 流动性指标
- [ ] 买卖价差计算
  - [ ] 最优买卖价差
  - [ ] 加权平均价差
- [ ] 订单簿深度指标

#### 输出存储
- [ ] 实时指标写入 Redis
- [ ] 历史指标写入 TDengine
- [ ] 聚合指标写入 Doris

---

### 3. K线聚合作业 `src/data_processing/flink_jobs/aggregation_job.py`

#### 时间窗口配置
- [ ] Tumbling Window (滚动窗口)
  - [ ] 1分钟K线
  - [ ] 5分钟K线
  - [ ] 15分钟K线
  - [ ] 1小时K线
  - [ ] 4小时K线
  - [ ] 1日K线

- [ ] Sliding Window (滑动窗口)
  - [ ] 实时均线计算窗口

#### K线计算逻辑
- [ ] Open (开盘价)
  - [ ] 窗口第一条成交价格
- [ ] High (最高价)
  - [ ] 窗口内最高成交价格
- [ ] Low (最低价)
  - [ ] 窗口内最低成交价格
- [ ] Close (收盘价)
  - [ ] 窗口最后一条成交价格
- [ ] Volume (成交量)
  - [ ] 窗口内成交量求和
- [ ] Amount (成交额)
  - [ ] 窗口内成交额求和

#### 多数据源聚合
- [ ] 多交易所价格聚合
  - [ ] 按成交量加权
  - [ ] 简单平均
- [ ] 链上交易数据聚合

#### 输出
- [ ] 写入 TDengine kline 超级表
- [ ] 写入 Redis 缓存
- [ ] 写入 Kafka Topic: aggregated.klines

---

### 4. 异常检测作业 `src/data_processing/flink_jobs/anomaly_detection.py`

#### 价格异常检测
- [ ] 价格跳变检测
  - [ ] 1分钟内涨跌超过5%
  - [ ] 5分钟内涨跌超过10%
- [ ] 价格与均值偏差检测
  - [ ] 偏离MA20超过2个标准差
- [ ] 多交易所价格背离检测
  - [ ] 价差超过1%

#### 成交量异常检测
- [ ] 成交量突增检测
  - [ ] 超过历史均值3倍
- [ ] 买卖失衡检测
  - [ ] 买单/卖单比例异常

#### 链上异常检测
- [ ] 大额转账检测
  - [ ] 超过阈值警报
- [ ] 合约异常调用检测
  - [ ] 未知函数调用
- [ ] Gas价格异常
  - [ ] 突然飙升检测

#### 告警触发
- [ ] 写入 Kafka Topic: alerts
- [ ] 调用告警服务API
- [ ] 记录检测日志

---

## 高级功能

### 状态管理
- [ ] Checkpoint配置
  - [ ] 间隔: 60秒
  - [ ] 状态后端: RocksDB
  - [ ] 增量Checkpoint
- [ ] Savepoint管理
  - [ ] 手动触发
  - [ ] 自动定时触发
- [ ] 状态恢复

### 时间语义
- [ ] 事件时间 (Event Time)
  - [ ] 水印生成策略
  - [ ] 允许延迟: 5秒
- [ ] 处理时间 (Processing Time)
  - [ ] 用于非关键指标
- [ ] 摄取时间 (Ingestion Time)

### 性能优化
- [ ] 并行度调优
  - [ ] 根据Topic分区设置
- [ ] 缓冲区配置
- [ ] 网络缓冲区调优
- [ ] JVM参数优化

### 监控集成
- [ ] Flink Metrics接入Prometheus
- [ ] 自定义指标定义
  - [ ] 每秒处理记录数
  - [ ] 延迟时间
  - [ ] 错误率
- [ ] Grafana仪表盘配置

---

## 接口与集成

### 与Kafka集成
```
Source: Kafka Topics
  -> Flink Processing
    -> Sink: TDengine / Redis / Doris / Kafka
```

### 与存储集成
- [ ] TDengine Sink连接器
- [ ] Redis Sink连接器
- [ ] Doris Sink连接器 (JDBC)

---

## 测试

### 单元测试
- [ ] 窗口函数测试
- [ ] 聚合逻辑测试
- [ ] 异常检测算法测试

### 集成测试
- [ ] 端到端数据流测试
- [ ] Checkpoint恢复测试
- [ ] 故障恢复测试

### 性能测试
- [ ] 吞吐量测试
  - [ ] 目标: 10万条/秒
- [ ] 延迟测试
  - [ ] 目标: P99 < 1秒
- [ ] 背压测试

---

## 部署

### 集群配置
- [ ] JobManager HA配置
- [ ] TaskManager资源分配
- [ ] 网络配置

### 提交作业
- [ ] 命令行提交脚本
- [ ] REST API提交
- [ ] 自动重启策略

---

## 关键指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 吞吐量 | > 100,000 条/秒 | 处理能力 |
| 端到端延迟 | < 1秒 (P99) | 实时性 |
| Checkpoint时间 | < 30秒 | 状态保存 |
| 可用性 | 99.9% | 服务稳定性 |

---

## 依赖项

```python
# requirements.txt 添加
apache-flink==1.18.0
```

---

## 注意事项

1. **内存配置**: TaskManager内存建议 4GB+
2. **网络**: 确保Kafka与Flink网络互通
3. **时间同步**: 服务器时间必须同步 (NTP)
4. **监控**: 必须配置监控告警
5. **测试**: 生产部署前充分测试
