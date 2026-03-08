<template>
  <div class="onchain">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>链上概览</span>
              <el-select v-model="selectedChain" style="width: 120px;">
                <el-option label="Ethereum" value="ethereum" />
                <el-option label="BSC" value="bsc" />
                <el-option label="Polygon" value="polygon" />
                <el-option label="Arbitrum" value="arbitrum" />
                <el-option label="Base" value="base" />
              </el-select>
            </div>
          </template>
          <div class="chain-stats">
            <div class="stat-row">
              <span class="stat-label">当前区块</span>
              <span class="stat-value">#19,234,567</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">出块时间</span>
              <span class="stat-value">12s</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Gas价格</span>
              <span class="stat-value">25 Gwei</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">TPS</span>
              <span class="stat-value">15.3</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <span>最新区块</span>
          </template>
          <el-table :data="blocks" style="width: 100%">
            <el-table-column prop="number" label="区块" width="120">
              <template #default="{ row }">
                <el-link type="primary">#{{ row.number }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="tx_count" label="交易数" width="100" />
            <el-table-column prop="gas_used" label="Gas使用" width="150">
              <template #default="{ row }">
                {{ (row.gas_used / 1e6).toFixed(2) }}M
              </template>
            </el-table-column>
            <el-table-column prop="miner" label="矿工">
              <template #default="{ row }">
                {{ row.miner.slice(0, 10) }}...{{ row.miner.slice(-8) }}
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="150" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>大额转账监控</span>
            <el-tag type="warning">实时</el-tag>
          </template>
          <el-table :data="largeTransfers" style="width: 100%">
            <el-table-column prop="tx_hash" label="交易哈希" width="200">
              <template #default="{ row }">
                <el-link type="primary">{{ row.tx_hash.slice(0, 20) }}...</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="token" label="代币" width="120" />
            <el-table-column prop="amount" label="金额" width="150">
              <template #default="{ row }">
                <span style="color: #F56C6C; font-weight: bold;">{{ row.amount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="from" label="转出地址">
              <template #default="{ row }">
                {{ row.from.slice(0, 10) }}...{{ row.from.slice(-8) }}
              </template>
            </el-table-column>
            <el-table-column prop="to" label="转入地址">
              <template #default="{ row }">
                {{ row.to.slice(0, 10) }}...{{ row.to.slice(-8) }}
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="150" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedChain = ref('ethereum')

const blocks = ref([
  { number: 19234567, tx_count: 156, gas_used: 15823456, miner: '0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5', time: '10:23:45' },
  { number: 19234566, tx_count: 203, gas_used: 19876543, miner: '0x388C818CA8B9251b393131C08a736A67ccB19297', time: '10:23:33' },
  { number: 19234565, tx_count: 178, gas_used: 17654321, miner: '0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5', time: '10:23:21' },
  { number: 19234564, tx_count: 234, gas_used: 22345678, miner: '0x388C818CA8B9251b393131C08a736A67ccB19297', time: '10:23:09' },
])

const largeTransfers = ref([
  { tx_hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef', token: 'USDT', amount: '1,000,000', from: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', to: '0x8ba1f109551bD432803012645Hac136c82C3e8C9', time: '10:23:45' },
  { tx_hash: '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890', token: 'ETH', amount: '500', from: '0x8ba1f109551bD432803012645Hac136c82C3e8C9', to: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', time: '10:23:30' },
  { tx_hash: '0x7890abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456', token: 'USDC', amount: '2,500,000', from: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', to: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', time: '10:23:15' },
])
</script>

<style scoped>
.onchain {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chain-stats {
  padding: 10px 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: bold;
  color: #303133;
}
</style>
