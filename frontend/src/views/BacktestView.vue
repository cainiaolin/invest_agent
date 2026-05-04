<template>
  <div class="backtest-view">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>策略回测</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="股票代码">
          <el-input
            v-model="form.stock_code"
            placeholder="请输入6位股票代码，如 600519"
            maxlength="6"
            clearable
          />
        </el-form-item>

        <el-form-item label="Agent策略">
          <el-select v-model="form.agent" placeholder="选择Agent">
            <el-option label="巴菲特 - 价值投资" value="buffet" />
            <el-option label="格雷厄姆 - 深度价值" value="graham" />
            <el-option label="费雪 - 成长投资" value="fisher" />
            <el-option label="林奇 - GARP策略" value="lynch" />
            <el-option label="索罗斯 - 宏观对冲" value="soros" />
            <el-option label="达利欧 - 全天候策略" value="dalio" />
          </el-select>
        </el-form-item>

        <el-form-item label="回测时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="初始资金">
          <el-input-number v-model="form.initial_capital" :min="100000" :step="100000" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleBacktest" :loading="loading">
            开始回测
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="result" class="result-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>回测报告</span>
        </div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="股票代码">{{ result.stock_code }}</el-descriptions-item>
        <el-descriptions-item label="Agent">{{ result.agent_name }}</el-descriptions-item>
        <el-descriptions-item label="回测周期">{{ result.start_date }} ~ {{ result.end_date }}</el-descriptions-item>
        <el-descriptions-item label="初始资金">¥{{ result.initial_capital.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="最终资金">¥{{ result.final_capital.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="总收益率">
          <span :class="getReturnClass(result.total_return)">
            {{ (result.total_return * 100).toFixed(2) }}%
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>收益指标</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="年化收益率" :value="result.annual_return * 100" :precision="2" suffix="%">
            <template #prefix>
              <span :class="getReturnClass(result.annual_return)">📈</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="夏普比率" :value="result.sharpe_ratio" :precision="2" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="最大回撤" :value="result.max_drawdown * 100" :precision="2" suffix="%">
            <template #prefix>
              <span class="negative">📉</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider>交易统计</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="总交易次数" :value="result.total_trades" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="胜率" :value="result.win_rate * 100" :precision="1" suffix="%" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="盈亏比" :value="result.profit_factor" :precision="2" />
        </el-col>
      </el-row>

      <el-divider>基准对比</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="沪深300收益" :value="result.benchmark_return * 100" :precision="2" suffix="%" />
        </el-col>
        <el-col :span="12">
          <el-statistic title="超额收益" :value="result.excess_return * 100" :precision="2" suffix="%">
            <template #prefix>
              <span :class="getReturnClass(result.excess_return)">
                {{ result.excess_return > 0 ? '🎯' : '📊' }}
              </span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-divider v-if="result.trades.length > 0">交易明细</el-divider>
      <el-table v-if="result.trades.length > 0" :data="result.trades" border stripe size="small">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="action" label="操作" width="80">
          <template #default="{ row }">
            <el-tag :type="row.action === 'buy' ? 'success' : 'danger'">
              {{ row.action === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shares" label="数量" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥{{ row.amount.toLocaleString() }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Document } from '@element-plus/icons-vue'
import axios from 'axios'

interface BacktestResult {
  stock_code: string
  agent_name: string
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  annual_return: number
  sharpe_ratio: number
  max_drawdown: number
  max_drawdown_duration: number
  total_trades: number
  win_rate: number
  profit_factor: number
  benchmark_return: number
  excess_return: number
  information_ratio: number
  trades: any[]
}

const form = ref({
  stock_code: '',
  agent: 'buffet',
  initial_capital: 1000000
})

const dateRange = ref<string[]>(['2020-01-01', '2024-12-31'])
const loading = ref(false)
const result = ref<BacktestResult | null>(null)

const getReturnClass = (value: number) => {
  return value >= 0 ? 'positive' : 'negative'
}

const handleBacktest = async () => {
  if (!form.value.stock_code) {
    ElMessage.warning('请输入股票代码')
    return
  }

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择回测时间范围')
    return
  }

  loading.value = true
  result.value = null

  try {
    const response = await axios.post('/api/v1/backtest/', {
      stock_code: form.value.stock_code,
      agent: form.value.agent,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      initial_capital: form.value.initial_capital
    })

    result.value = response.data
    ElMessage.success('回测完成')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '回测失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.backtest-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.positive {
  color: #67c23a;
}

.negative {
  color: #f56c6c;
}
</style>
