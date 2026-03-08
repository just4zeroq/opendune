# 数据分析模块 - 待开发任务清单

> 状态: ⏳ 待开发
> 优先级: 🔴 高
> 依赖: 数据源 (TDengine, MySQL)

---

## 技术指标计算 `src/data_analysis/indicators/`

### 1. 移动平均线 (MA)
**文件**: `ma.py`

- [ ] 简单移动平均 (SMA)
  - [ ] SMA7 计算
  - [ ] SMA25 计算
  - [ ] SMA99 计算
  - [ ] 通用SMA(n)函数

- [ ] 指数移动平均 (EMA)
  - [ ] EMA12 计算
  - [ ] EMA26 计算
  - [ ] 通用EMA(n)函数

- [ ] 加权移动平均 (WMA)
  - [ ] 通用WMA(n)函数

---

### 2. RSI指标
**文件**: `rsi.py`

- [ ] RSI计算
  - [ ] RSI14 (标准周期)
  - [ ] RSI7 (短周期)
  - [ ] RSI21 (长周期)
- [ ] 超买超卖判断
  - [ ] >70 超买
  - [ ] <30 超卖
- [ ] RSI背离检测
  - [ ] 顶背离
  - [ ] 底背离

---

### 3. MACD指标
**文件**: `macd.py`

- [ ] DIF计算
  - [ ] DIF = EMA12 - EMA26
- [ ] DEA计算 (Signal Line)
  - [ ] DEA = EMA9(DIF)
- [ ] MACD柱 (Histogram)
  - [ ] MACD = (DIF - DEA) * 2
- [ ] 金叉死叉检测
  - [ ] 金叉: DIF上穿DEA
  - [ ] 死叉: DIF下穿DEA

---

### 4. 布林带 (Bollinger Bands)
**文件**: `bollinger.py`

- [ ] 中轨计算
  - [ ] Middle = SMA20
- [ ] 标准差计算
  - [ ] STD20
- [ ] 上轨计算
  - [ ] Upper = Middle + 2 * STD
- [ ] 下轨计算
  - [ ] Lower = Middle - 2 * STD
- [ ] 带宽计算 (Bandwidth)
- [ ] %B指标计算

---

### 5. 成交量指标

#### OBV (On Balance Volume)
**文件**: `obv.py`
- [ ] OBV计算
  - [ ] 涨: OBV = OBV前 + 成交量
  - [ ] 跌: OBV = OBV前 - 成交量

#### VWAP (Volume Weighted Average Price)
**文件**: `vwap.py`
- [ ] VWAP计算
  - [ ] VWAP = Σ(价格 * 成交量) / Σ成交量
- [ ] 标准差带

---

### 6. 波动率指标

#### ATR (Average True Range)
**文件**: `atr.py`
- [ ] TR (True Range)计算
  - [ ] TR = max(High-Low, |High-Close前|, |Low-Close前|)
- [ ] ATR14计算
  - [ ] ATR = SMA14(TR)

---

### 7. 其他常用指标

- [ ] KDJ随机指标
- [ ] CCI商品通道指标
- [ ] Williams %R
- [ ] Stochastic Oscillator
- [ ] ADX趋势强度指标
- [ ] SAR抛物线转向

---

## 策略分析 `src/data_analysis/strategies/`

### 基础框架
**文件**: `base_strategy.py`
- [ ] 策略基类定义
- [ ] 信号生成接口
- [ ] 回测框架接口
- [ ] 参数优化接口

### 经典策略实现

#### 1. 双均线策略
**文件**: `ma_cross_strategy.py`
- [ ] 金叉买入信号
- [ ] 死叉卖出信号
- [ ] 参数优化 (MA5/MA10, MA10/MA20等)

#### 2. MACD策略
**文件**: `macd_strategy.py`
- [ ] MACD金叉买入
- [ ] MACD死叉卖出
- [ ] 零轴穿越信号

#### 3. 布林带策略
**文件**: `bollinger_strategy.py`
- [ ] 下轨反弹买入
- [ ] 上轨回落卖出
- [ ] 突破策略

#### 4. RSI策略
**文件**: `rsi_strategy.py`
- [ ] 超卖(<30)买入
- [ ] 超买(>70)卖出

#### 5. 多因子策略
**文件**: `multi_factor_strategy.py`
- [ ] 多指标综合评分
- [ ] 权重配置
- [ ] 动态调整

---

## 告警引擎 `src/data_analysis/alerts/`

### 告警引擎核心
**文件**: `alert_engine.py`

#### 规则引擎
- [ ] 规则解析器
  - [ ] 条件表达式解析
  - [ ] 运算符支持 (>, <, =, >=, <=, !=)
  - [ ] 逻辑运算符 (AND, OR, NOT)
- [ ] 规则匹配器
  - [ ] 实时数据匹配
  - [ ] 历史数据对比
  - [ ] 多条件组合匹配

#### 触发机制
- [ ] 实时触发
  - [ ] 每秒钟检查一次
- [ ] 周期触发
  - [ ] 分钟级
  - [ ] 小时级
- [ ] 防抖处理
  - [ ] 同一规则冷却期 (如5分钟内不重复触发)

#### 告警级别
- [ ] INFO (信息)
- [ ] WARNING (警告)
- [ ] CRITICAL (严重)

---

### 告警规则管理
**文件**: `rules.py`

#### 规则类型
- [ ] 价格规则
  - [ ] 价格突破
  - [ ] 价格跌破
  - [ ] 价格涨跌幅
- [ ] 成交量规则
  - [ ] 成交量突增
  - [ ] 成交量萎缩
- [ ] 指标规则
  - [ ] RSI超买超卖
  - [ ] MACD金叉死叉
  - [ ] 布林带突破
- [ ] 链上规则
  - [ ] 大额转账
  - [ ] 合约异常
- [ ] 自定义规则
  - [ ] 多条件组合
  - [ ] 复杂表达式

#### 规则配置
```json
{
  "name": "BTC价格突破",
  "type": "price",
  "symbol": "BTCUSDT",
  "condition": {
    "field": "price",
    "operator": ">",
    "value": 50000
  },
  "severity": "warning",
  "cooldown": 300
}
```

---

### 告警通知
**文件**: `notifiers/`

#### 通知渠道
- [ ] Webhook通知
  - [ ] HTTP POST请求
  - [ ] 自定义Header
  - [ ] 重试机制
- [ ] 邮件通知
  - [ ] SMTP配置
  - [ ] 邮件模板
- [ ] 短信通知 (可选)
- [ ] 钉钉/飞书/企业微信
  - [ ] 群机器人
  - [ ] 消息模板

#### 通知模板
- [ ] 告警标题模板
- [ ] 告警内容模板
- [ ] Markdown格式支持

---

## 数据服务集成

### 指标计算服务接口
**API端点**: `/api/v1/analytics/indicators/{symbol}`

- [ ] 实时指标计算
- [ ] 历史指标查询
- [ ] 批量指标计算

### 告警API集成
- [ ] 创建告警规则
- [ ] 更新告警规则
- [ ] 删除告警规则
- [ ] 查询告警历史

---

## 数据存储设计

### 指标数据表 (TDengine)
```sql
CREATE STABLE indicator (
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
  interval BINARY(10),
  exchange BINARY(20)
);
```

---

## 性能优化

### 计算优化
- [ ] 向量化计算 (NumPy/Pandas)
- [ ] 缓存中间结果
- [ ] 增量计算

### 存储优化
- [ ] 批量写入
- [ ] 预聚合
- [ ] 数据分区

---

## 测试

### 指标测试
- [ ] 与TradingView对比验证
- [ ] 边界条件测试
- [ ] 性能测试

### 告警测试
- [ ] 规则匹配测试
- [ ] 触发条件测试
- [ ] 通知送达测试

---

## 依赖项

```python
# requirements.txt 添加
numpy==1.26.3
pandas==2.1.4
scipy==1.11.4
ta-lib==0.4.28
```

---

## 注意事项

1. **精度问题**: 金融计算注意浮点数精度
2. **实时性**: 指标计算延迟控制在秒级
3. **回测**: 策略需要历史数据回测验证
4. **风险控制**: 策略信号仅供参考，需结合实际风控
