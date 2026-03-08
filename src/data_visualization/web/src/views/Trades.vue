<template>
  <div class="trades">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时成交流</span>
              <el-select v-model="selectedSymbol" placeholder="选择交易对" style="width: 150px;">
                <el-option label="BTC/USDT" value="BTCUSDT" />
                <el-option label="ETH/USDT" value="ETHUSDT" />
                <el-option label="BNB/USDT" value="BNBUSDT" />
              </el-select>
            </div>
          </template>
          <div class="trade-flow">
            <el-timeline>
              <el-timeline-item
                v-for="trade in trades"
                :key="trade.id"
                :type="trade.side === 'buy' ? 'success' : 'danger'"
                :timestamp="trade.time"
              >
                <div class="trade-item">
                  <span class="trade-symbol">{{ trade.symbol }}</span>
                  <span :class="['trade-side', trade.side]">{{ trade.side.toUpperCase() }}</span>
                  <span class="trade-price">${{ trade.price }}</span>
                  <span class="trade-amount">{{ trade.amount }}</span>
                  <span class="trade-total">${{ (trade.price * trade.amount).toFixed(2) }}</span>
                  <el-tag size="small">{{ trade.source }}</el-tag>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>交易统计</span>
          </template>
          <div class="stats">
            <div class="stat-item">
              <div class="stat-label">24H成交量</div>
              <div class="stat-value">$2.34B</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">24H成交笔数</div>
              <div class="stat-value">1,234,567</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">大单数量(>100K)</div>
              <div class="stat-value">234</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">买卖比</div>
              <div class="stat-value">1.23</div>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>交易所分布</span>
          </template>
          <div class="exchange-distribution">
            <div class="exchange-item">
              <span class="exchange-name">Binance</span>
              <el-progress :percentage="45" color="#409EFF" />
            </div>
            <div class="exchange-item">
              <span class="exchange-name">OKX</span>
              <el-progress :percentage="25" color="#67C23A" />
            </div>
            <div class="exchange-item">
              <span class="exchange-name">Bybit</span>
              <el-progress :percentage="20" color="#E6A23C" />
            </div>
            <div class="exchange-item">
              <span class="exchange-name">Bitget</span>
              <el-progress :percentage="10" color="#F56C6C" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedSymbol = ref('BTCUSDT')

const trades = ref([
  { id: 1, symbol: 'BTC/USDT', side: 'buy', price: 45234.50, amount: 0.5, source: 'Binance', time: '10:23:45' },
  { id: 2, symbol: 'BTC/USDT', side: 'sell', price: 45230.00, amount: 1.2, source: 'OKX', time: '10:23:42' },
  { id: 3, symbol: 'ETH/USDT', side: 'buy', price: 2890.20, amount: 2.3, source: 'Bybit', time: '10:23:38' },
  { id: 4, symbol: 'ETH/USDT', side: 'sell', price: 2891.00, amount: 0.8, source: 'Bitget', time: '10:23:35' },
  { id: 5, symbol: 'BTC/USDT', side: 'buy', price: 45235.00, amount: 0.3, source: 'Binance', time: '10:23:30' },
  { id: 6, symbol: 'SOL/USDT', side: 'sell', price: 98.50, amount: 100, source: 'OKX', time: '10:23:28' },
])
</script>

<style scoped>
.trades {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trade-flow {
  max-height: 600px;
  overflow-y: auto;
}

.trade-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 5px 0;
}

.trade-symbol {
  font-weight: bold;
  width: 100px;
}

.trade-side {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.trade-side.buy {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.trade-side.sell {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

.trade-price {
  font-weight: bold;
  width: 100px;
}

.trade-amount {
  width: 80px;
}

.trade-total {
  width: 100px;
  color: #606266;
}

.stats {
  padding: 10px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.exchange-distribution {
  padding: 10px 0;
}

.exchange-item {
  margin-bottom: 15px;
}

.exchange-name {
  display: block;
  margin-bottom: 5px;
  color: #606266;
}
</style>
