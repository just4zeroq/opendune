<template>
  <div class="alerts">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>告警规则</span>
              <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>新增规则
              </el-button>
            </div>
          </template>
          <el-table :data="rules" style="width: 100%">
            <el-table-column prop="name" label="规则名称" width="200" />
            <el-table-column prop="type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getTypeTag(row.type)">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="condition" label="触发条件" />
            <el-table-column prop="severity" label="严重等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-switch v-model="row.status" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link @click="editRule(row)">编辑</el-button>
                <el-button type="danger" link @click="deleteRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>告警统计</span>
          </template>
          <div class="alert-stats">
            <div class="stat-item critical">
              <div class="stat-value">2</div>
              <div class="stat-label">严重告警</div>
            </div>
            <div class="stat-item warning">
              <div class="stat-value">5</div>
              <div class="stat-label">警告告警</div>
            </div>
            <div class="stat-item info">
              <div class="stat-value">12</div>
              <div class="stat-label">信息提示</div>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>最近触发</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="alert in recentAlerts"
              :key="alert.id"
              :type="alert.severity === 'critical' ? 'danger' : alert.severity === 'warning' ? 'warning' : 'info'"
              :timestamp="alert.time"
            >
              <div class="alert-item">
                <div class="alert-name">{{ alert.rule_name }}</div>
                <div class="alert-message">{{ alert.message }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建规则弹窗 -->
    <el-dialog v-model="showCreateDialog" title="创建告警规则" width="600px">
      <el-form :model="newRule" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="newRule.name" placeholder="输入规则名称" />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-select v-model="newRule.type" style="width: 100%;">
            <el-option label="价格" value="price" />
            <el-option label="成交量" value="volume" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="监控标的">
          <el-input v-model="newRule.symbol" placeholder="如: BTCUSDT" />
        </el-form-item>
        <el-form-item label="触发条件">
          <el-row :gutter="10">
            <el-col :span="8">
              <el-select v-model="newRule.operator">
                <el-option label=">" value="gt" />
                <el-option label="<" value="lt" />
                <el-option label="=" value="eq" />
                <el-option label="变化率 >" value="change_gt" />
              </el-select>
            </el-col>
            <el-col :span="16">
              <el-input-number v-model="newRule.threshold" style="width: 100%;" />
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="严重等级">
          <el-radio-group v-model="newRule.severity">
            <el-radio-button label="info">信息</el-radio-button>
            <el-radio-button label="warning">警告</el-radio-button>
            <el-radio-button label="critical">严重</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createRule">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const showCreateDialog = ref(false)

const rules = ref([
  { id: 1, name: 'BTC价格突破45000', type: 'price', condition: 'BTCUSDT > 45000', severity: 'warning', status: true },
  { id: 2, name: 'ETH成交量异常', type: 'volume', condition: 'ETHUSDT 24H成交量 > 平均300%', severity: 'critical', status: true },
  { id: 3, name: '大额转账监控', type: 'custom', condition: '单笔转账 > 1000 ETH', severity: 'info', status: true },
])

const newRule = ref({
  name: '',
  type: 'price',
  symbol: '',
  operator: 'gt',
  threshold: 0,
  severity: 'warning',
})

const recentAlerts = ref([
  { id: 1, rule_name: 'BTC价格突破', message: 'Bitcoin价格突破45000 USDT', severity: 'warning', time: '10:20:00' },
  { id: 2, rule_name: '成交量异常', message: 'ETH/USDT交易量超过平均值300%', severity: 'critical', time: '10:15:00' },
  { id: 3, rule_name: '大额转账', message: '检测到1000 ETH大额转账', severity: 'info', time: '10:10:00' },
])

const getTypeTag = (type: string) => {
  const map: Record<string, string> = { price: 'success', volume: 'warning', custom: 'info' }
  return map[type] || 'info'
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = { info: 'info', warning: 'warning', critical: 'danger' }
  return map[severity] || 'info'
}

const editRule = (rule: any) => {
  // TODO: 编辑规则
}

const deleteRule = (rule: any) => {
  // TODO: 删除规则
}

const createRule = () => {
  // TODO: 创建规则
  showCreateDialog.value = false
}
</script>

<style scoped>
.alerts {
  padding-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 15px 30px;
  border-radius: 8px;
  background: #f5f7fa;
}

.stat-item.critical {
  background: rgba(245, 108, 108, 0.1);
}

.stat-item.warning {
  background: rgba(230, 162, 60, 0.1);
}

.stat-item.info {
  background: rgba(144, 147, 153, 0.1);
}

.stat-item.critical .stat-value {
  color: #F56C6C;
}

.stat-item.warning .stat-value {
  color: #E6A23C;
}

.stat-item.info .stat-value {
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-label {
  margin-top: 5px;
  color: #606266;
}

.alert-item {
  padding: 5px 0;
}

.alert-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.alert-message {
  font-size: 12px;
  color: #606266;
}
</style>
