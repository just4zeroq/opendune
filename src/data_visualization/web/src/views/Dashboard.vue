<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409EFF;">
            <el-icon size="30"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">$2.45T</div>
            <div class="stat-label">24H 总成交量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67C23A;">
            <el-icon size="30"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">12,456</div>
            <div class="stat-label">活跃交易对</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #E6A23C;">
            <el-icon size="30"><Link /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">1,234</div>
            <div class="stat-label">链上交易/分钟</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #F56C6C;">
            <el-icon size="30"><Bell /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">8</div>
            <div class="stat-label">活跃告警</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>价格走势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="1H" />
                <el-radio-button label="24H" />
                <el-radio-button label="7D" />
                <el-radio-button label="30D" />
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="priceChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>交易所占比</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart class="chart" :option="exchangeChartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时交易和告警 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时成交</span>
            </div>
          </template>
          <el-table :data="recentTrades" style="width: 100%" height="300">
            <el-table-column prop="symbol" label="交易对" width="100" />
            <el-table-column prop="price" label="价格" width="120">
              <template #default="{ row }">
                <span :class="row.side === 'buy' ? 'price-up' : 'price-down'">
                  {{ row.price }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="120" />
            <el-table-column prop="source" label="来源" width="100" />
            <el-table-column prop="time" label="时间" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最新告警</span>
              <el-button type="primary" link>查看全部</el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="alert in recentAlerts"
              :key="alert.id"
              :type="alert.severity === 'critical' ? 'danger' : alert.severity === 'warning' ? 'warning' : 'info'"
              :timestamp="alert.time"
            >
              <div class="alert-item">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-desc">{{ alert.description }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { TrendCharts, DataLine, Link, Bell } from '@element-plus/icons-vue'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
])

const timeRange = ref('24H')

// 模拟数据
const priceChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['BTC', 'ETH'] },
  xAxis: {
    type: 'category',
    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'BTC',
      type: 'line',
      smooth: true,
      data: [42000, 43500, 42800, 44500, 43800, 45200, 44800],
    },
    {
      name: 'ETH',
      type: 'line',
      smooth: true,
      data: [2800, 2850, 2820, 2900, 2880, 2950, 2920],
    },
  ],
}))

const exchangeChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: '0%' },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 45, name: 'Binance' },
        { value: 25, name: 'OKX' },
        { value: 20, name: 'Bybit' },
        { value: 10, name: 'Bitget' },
      ],
    },
  ],
}))

const recentTrades = ref([
  { symbol: 'BTC/USDT', price: '45,234.50', quantity: '0.5', side: 'buy', source: 'Binance', time: '10:23:45' },
  { symbol: 'ETH/USDT', price: '2,890.20', quantity: '2.3', side: 'sell', source: 'OKX', time: '10:23:42' },
  { symbol: 'BTC/USDT', price: '45,230.00', quantity: '1.2', side: 'sell', source: 'Bybit', time: '10:23:38' },
  { symbol: 'SOL/USDT', price: '98.50', quantity: '100', side: 'buy', source: 'Binance', time: '10:23:35' },
  { symbol: 'ETH/USDT', price: '2,891.00', quantity: '0.8', side: 'buy', source: 'Bitget', time: '10:23:30' },
])

const recentAlerts = ref([
  { id: 1, title: 'BTC价格突破45000', description: 'Bitcoin价格突破关键阻力位', severity: 'warning', time: '10:20:00' },
  { id: 2, title: '交易量异常', description: 'ETH/USDT交易量超过平均值300%', severity: 'critical', time: '10:15:00' },
  { id: 3, title: '链上大额转账', description: '检测到1000 BTC大额转账', severity: 'info', time: '10:10:00' },
])
</script>

<style scoped>
.dashboard {
  padding-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 350px;
}

.chart {
  width: 100%;
  height: 100%;
}

.price-up {
  color: #67C23A;
}

.price-down {
  color: #F56C6C;
}

.alert-item {
  padding: 5px 0;
}

.alert-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.alert-desc {
  font-size: 12px;
  color: #606266;
}
</style>
