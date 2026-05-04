<template>
  <div class="screen-view">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>智能选股</span>
        </div>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="股票池">
          <el-select v-model="form.universe" placeholder="选择股票池">
            <el-option label="全部A股" value="all" />
            <el-option label="沪深300" value="index:沪深300" />
            <el-option label="银行" value="industry:银行" />
            <el-option label="医药生物" value="industry:医药生物" />
            <el-option label="食品饮料" value="industry:食品饮料" />
          </el-select>
        </el-form-item>

        <el-form-item label="Agent选择">
          <el-select v-model="form.agents" multiple placeholder="选择Agent">
            <el-option label="全部Agent" value="all" />
            <el-option label="巴菲特" value="buffet" />
            <el-option label="格雷厄姆" value="graham" />
            <el-option label="费雪" value="fisher" />
            <el-option label="林奇" value="lynch" />
            <el-option label="索罗斯" value="soros" />
            <el-option label="达利欧" value="dalio" />
          </el-select>
        </el-form-item>

        <el-form-item label="返回数量">
          <el-input-number v-model="form.top_n" :min="1" :max="100" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleScreen" :loading="loading">
            开始选股
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="results.length > 0" class="result-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-icon><DataLine /></el-icon>
          <span>选股结果 (前{{ results.length }}只)</span>
        </div>
      </template>

      <el-table :data="results" border stripe>
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="stock_name" label="股票名称" width="120" />
        <el-table-column prop="total_score" label="综合评分" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.total_score)">{{ row.total_score.toFixed(1) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buy_votes" label="买入票数" width="100" />
        <el-table-column prop="total_agents" label="总Agent数" width="100" />
        <el-table-column label="推荐" width="120">
          <template #default="{ row }">
            <el-tag :type="getRecommendType(row)">{{ getRecommend(row) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="summary">
        <el-text type="info">扫描了 {{ totalAnalyzed }} 只股票，返回前 {{ results.length }} 只</el-text>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, DataLine } from '@element-plus/icons-vue'
import axios from 'axios'

interface StockScore {
  stock_code: string
  stock_name: string
  total_score: number
  buy_votes: number
  total_agents: number
}

const form = ref({
  universe: 'all',
  agents: ['all'],
  top_n: 20
})

const loading = ref(false)
const results = ref<StockScore[]>([])
const totalAnalyzed = ref(0)

const getScoreType = (score: number) => {
  if (score >= 85) return 'success'
  if (score >= 75) return 'warning'
  return 'info'
}

const getRecommend = (row: StockScore) => {
  if (row.total_score >= 85) return '强烈推荐'
  if (row.total_score >= 75) return '推荐'
  return '观望'
}

const getRecommendType = (row: StockScore) => {
  if (row.total_score >= 85) return 'success'
  if (row.total_score >= 75) return 'warning'
  return 'info'
}

const handleScreen = async () => {
  loading.value = true
  results.value = []

  try {
    const response = await axios.post('/api/v1/screen/', {
      universe: form.value.universe,
      agents: form.value.agents.join(','),
      top_n: form.value.top_n
    })

    results.value = response.data.results
    totalAnalyzed.value = response.data.total_analyzed
    ElMessage.success('选股完成')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '选股失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.screen-view {
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

.summary {
  margin-top: 15px;
  text-align: center;
}
</style>
