<template>
  <div class="analytics">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>技术指标</span>
              <el-select v-model="selectedSymbol" style="width: 150px;">
                <el-option label="BTC/USDT" value="BTCUSDT" />
                <el-option label="ETH/USDT" value="ETHUSDT" />
                <el-option label="BNB/USDT" value="BNBUSDT" />
              </el-select>
            </div>
          </template>
          <div class="indicators">
            <div class="indicator-item">
              <span class="indicator-name">RSI (14)</span>
              <el-progress :percentage="65" :color="getRSIColor(65)" />
              <span class="indicator-value" :style="{ color: getRSIColor(65) }">65.4</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">MACD</span>
              <div class="macd-values">
                <span class="positive">MACD: 234.5</span>
                <span class="positive">Signal: 123.4</span>
                <span class="positive">Hist: 111.1</span>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">布林带</span>
              <div class="bollinger-values">
                <span>Upper: $47,234</span>
                <span>Middle: $45,123</span>
                <span>Lower: $43,012</span>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-name">移动平均线</span>
              <div class="ma-values">
                <span>MA7: $45,234</span>
                <span>MA25: $44,876</span>
                <span>MA99: $43,234</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>趋势分析</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button label="24H" />
                <el-radio-button label="7D" />
                <el-radio-button label="30D" />
              </el-radio-group>
            </div>
          </template>
          <div class="trend-analysis">
            <div class="trend-summary">
              <div class="trend-direction">
                <el-icon size="40" color="#67C23A" v-if="trendDirection === 'up'"><ArrowUp /></el-icon>
                <el-icon size="40" color="#F56C6C" v-else><ArrowDown /></el-icon>
                <span class="trend-text" :class="trendDirection">{{ trendDirection === 'up' ? '看涨' : '看跌' }}</span>
              </div>
              <div class="trend-confidence">
                <div class="confidence-label">置信度</div>
                <el-progress type="circle" :percentage="72" :width="100" />
              </div>
            </div>
            <div class="trend-factors">
              <div class="factor-title">影响因素</div>
              <el-tag v-for="factor in trendFactors" :key="factor.name" :type="factor.type" class="factor-tag">
                {{ factor.name }}: {{ factor.value }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>相关性分析</span>
          </template>
          <div class="correlation-chart">
            <v-chart :option="correlationOption" autoresize style="height: 300px;" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>流动性分析</span>
          </template>
          <div class="liquidity-analysis">
            <div class="liquidity-score">
              <div class="score-label">流动性评分</div>
              <div class="score-value">85/100</div>
              <el-rate :model-value="4.5" disabled show-score />
            </div>
            <div class="liquidity-details">
              <div class="detail-item">
                <span class="detail-label">买卖价差</span>
                <span class="detail-value">0.02%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">深度(1%)</span>
                <span class="detail-value">$12.5M</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">24H换手率</span>
                <span class="detail-value">45.2%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, HeatmapChart, GridComponent, TooltipComponent, VisualMapComponent])

const selectedSymbol = ref('BTCUSDT')
const trendPeriod = ref('24H')
const trendDirection = ref('up')

const trendFactors = ref([
  { name: '成交量', value: '放量', type: 'success' },
  { name: '资金流向', value: '净流入', type: 'success' },
  { name: '波动率', value: '上升', type: 'warning' },
  { name: '市场情绪', value: '贪婪', type: 'danger' },
])

const getRSIColor = (value: number) => {
  if (value > 70) return '#F56C6C'
  if (value < 30) return '#67C23A'
  return '#409EFF'
}

const correlationOption = computed(() => ({
  tooltip: { position: 'top' },
  grid: { top: '10%', bottom: '15%' },
  xAxis: {
    type: 'category',
    data: ['BTC', 'ETH', 'BNB', 'SOL', 'XRP'],
    splitArea: { show: true }
  },
  yAxis: {
    type: 'category',
    data: ['BTC', 'ETH', 'BNB', 'SOL', 'XRP'],
    splitArea: { show: true }
  },
  visualMap: {
    min: -1,
    max: 1,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%',
    inRange: {
      color: ['#F56C6C', '#fff', '#67C23A']
    }
  },
  series: [{
    type: 'heatmap',
    data: [
      [0, 0, 1], [0, 1, 0.85], [0, 2, 0.72], [0, 3, 0.68], [0, 4, 0.45],
      [1, 0, 0.85], [1, 1, 1], [1, 2, 0.78], [1, 3, 0.75], [1, 4, 0.52],
      [2, 0, 0.72], [2, 1, 0.78], [2, 2, 1], [2, 3, 0.65], [2, 4, 0.48],
      [3, 0, 0.68], [3, 1, 0.75], [3, 2, 0.65], [3, 3, 1], [3, 4, 0.55],
      [4, 0, 0.45], [4, 1, 0.52], [4, 2, 0.48], [4, 3, 0.55], [4, 4, 1],
    ],
    label: { show: true }
  }]
}))
</script>

<style scoped>
.analytics {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicators {
  padding: 10px 0;
}

.indicator-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.indicator-item:last-child {
  border-bottom: none;
}

.indicator-name {
  width: 100px;
  font-weight: 500;
  color: #606266;
}

.indicator-value {
  margin-left: 15px;
  font-weight: bold;
}

.macd-values, .bollinger-values, .ma-values {
  display: flex;
  gap: 20px;
  margin-left: 20px;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.trend-analysis {
  padding: 20px 0;
}

.trend-summary {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.trend-direction {
  text-align: center;
}

.trend-text {
  display: block;
  margin-top: 10px;
  font-size: 18px;
  font-weight: bold;
}

.trend-text.up {
  color: #67C23A;
}

.trend-text.down {
  color: #F56C6C;
}

.confidence-label {
  text-align: center;
  margin-bottom: 10px;
  color: #606266;
}

.trend-factors {
  padding-top: 20px;
}

.factor-title {
  font-weight: 500;
  margin-bottom: 15px;
}

.factor-tag {
  margin: 5px;
}

.liquidity-analysis {
  padding: 20px 0;
}

.liquidity-score {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.score-label {
  color: #606266;
  margin-bottom: 10px;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  color: #67C23A;
  margin-bottom: 10px;
}

.liquidity-details {
  padding-top: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  color: #606266;
}

.detail-value {
  font-weight: bold;
  color: #303133;
}
</style>
