<template>
  <div class="market">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-select v-model="selectedExchange" placeholder="选择交易所" style="width: 150px; margin-right: 10px;">
              <el-option label="全部交易所" value="" />
              <el-option label="Binance" value="binance" />
              <el-option label="OKX" value="okx" />
              <el-option label="Bybit" value="bybit" />
              <el-option label="Bitget" value="bitget" />
            </el-select>
            <el-input
              v-model="searchSymbol"
              placeholder="搜索交易对"
              style="width: 200px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <div class="header-right">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">列表</el-radio-button>
              <el-radio-button label="chart">图表</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <!-- 列表视图 -->
      <el-table
        v-if="viewMode === 'list'"
        :data="filteredTickers"
        style="width: 100%"
        v-loading="marketStore.loading"
      >
        <el-table-column prop="symbol" label="交易对" width="150">
          <template #default="{ row }">
            <div class="symbol-cell">
              <span class="symbol-name">{{ row.symbol }}</span>
              <el-tag size="small" type="info">{{ row.source }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="最新价" width="150">
          <template #default="{ row }">
            <span class="price">${{ formatPrice(row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change_24h_percent" label="24H涨跌" width="120">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_24h_percent)">
              {{ formatChange(row.change_24h_percent) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume_24h" label="24H成交量" width="150">
          <template #default="{ row }">
            {{ formatVolume(row.volume_24h) }}
          </template>
        </el-table-column>
        <el-table-column prop="high_24h" label="24H最高" width="120">
          <template #default="{ row }">
            ${{ formatPrice(row.high_24h) }}
          </template>
        </el-table-column>
        <el-table-column prop="low_24h" label="24H最低" width="120">
          <template #default="{ row }">
            ${{ formatPrice(row.low_24h) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showKline(row)">K线</el-button>
            <el-button type="primary" link @click="showDepth(row)">深度</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 图表视图 -->
      <div v-else class="chart-view">
        <div class="chart-list">
          <el-card
            v-for="ticker in filteredTickers.slice(0, 6)"
            :key="ticker.symbol"
            class="chart-card"
            @click="showKline(ticker)"
          >
            <div class="mini-chart-header">
              <span class="symbol">{{ ticker.symbol }}</span>
              <span :class="getChangeClass(ticker.change_24h_percent)">
                {{ formatChange(ticker.change_24h_percent) }}
              </span>
            </div>
            <div class="mini-chart-price">${{ formatPrice(ticker.price) }}</div>
            <div class="mini-chart">
              <v-chart :option="getMiniChartOption(ticker)" autoresize />
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- K线图弹窗 -->
    <el-dialog
      v-model="klineDialogVisible"
      title="K线图表"
      width="80%"
      destroy-on-close
    >
      <div class="kline-chart">
        <v-chart :option="klineOption" autoresize style="height: 500px;" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, CandlestickChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useMarketStore } from '@/stores'

use([CanvasRenderer, LineChart, CandlestickChart, GridComponent, TooltipComponent])

const marketStore = useMarketStore()

const selectedExchange = ref('')
const searchSymbol = ref('')
const viewMode = ref('list')
const klineDialogVisible = ref(false)
const selectedTicker = ref<any>(null)

const filteredTickers = computed(() => {
  let result = marketStore.tickers

  if (selectedExchange.value) {
    result = result.filter(t => t.source === selectedExchange.value)
  }

  if (searchSymbol.value) {
    const search = searchSymbol.value.toUpperCase()
    result = result.filter(t => t.symbol.includes(search))
  }

  return result
})

const formatPrice = (price: number) => {
  return price?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 })
}

const formatVolume = (volume: number) => {
  if (!volume) return '-'
  if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`
  if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`
  if (volume >= 1e3) return `${(volume / 1e3).toFixed(2)}K`
  return volume.toFixed(2)
}

const formatChange = (change: number) => {
  if (!change) return '-'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
}

const getChangeClass = (change: number) => {
  if (!change) return ''
  return change >= 0 ? 'price-up' : 'price-down'
}

const getMiniChartOption = (ticker: any) => ({
  grid: { top: 5, bottom: 5, left: 0, right: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { type: 'value', show: false },
  series: [{
    type: 'line',
    smooth: true,
    data: [10, 12, 11, 13, 12, 14, 13, 15, 14, 16],
    lineStyle: {
      color: ticker.change_24h_percent >= 0 ? '#67C23A' : '#F56C6C',
      width: 2,
    },
    symbol: 'none',
    areaStyle: {
      color: ticker.change_24h_percent >= 0 ? 'rgba(103, 194, 58, 0.1)' : 'rgba(245, 108, 108, 0.1)',
    },
  }],
})

const klineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '3%', bottom: '10%', top: '10%' },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value', scale: true },
  dataZoom: [{ type: 'inside' }, { type: 'slider' }],
  series: [{
    type: 'candlestick',
    data: [
      [20, 34, 10, 38],
      [40, 35, 30, 50],
      [31, 38, 33, 44],
      [38, 15, 5, 42],
      [35, 25, 20, 45],
      [25, 32, 28, 36],
      [30, 35, 28, 40],
    ],
  }],
}))

const showKline = (ticker: any) => {
  selectedTicker.value = ticker
  klineDialogVisible.value = true
}

const showDepth = (ticker: any) => {
  // TODO: 显示深度图
}

onMounted(() => {
  marketStore.fetchTickers()
})
</script>

<style scoped>
.market {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.symbol-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.symbol-name {
  font-weight: 500;
}

.price {
  font-weight: bold;
}

.price-up {
  color: #67C23A;
}

.price-down {
  color: #F56C6C;
}

.chart-view {
  padding: 20px;
}

.chart-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.chart-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.chart-card:hover {
  transform: translateY(-2px);
}

.mini-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.mini-chart-header .symbol {
  font-weight: bold;
  font-size: 16px;
}

.mini-chart-price {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.mini-chart {
  height: 80px;
}

.kline-chart {
  width: 100%;
}
</style>
