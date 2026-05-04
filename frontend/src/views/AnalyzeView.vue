<template>
  <div class="analyze-view">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon><Aim /></el-icon>
          <span>个股分析</span>
        </div>
      </template>

      <el-form :model="form" label-width="100px">
        <el-form-item label="股票代码">
          <el-input
            v-model="form.stock_code"
            placeholder="请输入6位股票代码，如 600519"
            maxlength="6"
            clearable
          />
        </el-form-item>

        <el-form-item label="协作模式">
          <el-radio-group v-model="form.mode">
            <el-radio label="parallel">并行独立</el-radio>
            <el-radio label="vote">投票决策</el-radio>
            <el-radio label="debate">辩论仲裁</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="选择Agent">
          <el-checkbox-group v-model="form.agents">
            <el-checkbox label="buffet">巴菲特</el-checkbox>
            <el-checkbox label="graham">格雷厄姆</el-checkbox>
            <el-checkbox label="fisher">费雪</el-checkbox>
            <el-checkbox label="lynch">林奇</el-checkbox>
            <el-checkbox label="soros">索罗斯</el-checkbox>
            <el-checkbox label="dalio">达利欧</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleAnalyze"
            :loading="loading"
            :disabled="!form.stock_code"
          >
            开始分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="result" class="result-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>分析报告</span>
        </div>
      </template>

      <div class="result-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="股票代码">{{ result.stock_code }}</el-descriptions-item>
          <el-descriptions-item label="协作模式">{{ modeName }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>Agent分析结果</el-divider>

        <el-table :data="result.agent_analyses" border>
          <el-table-column prop="agent_name" label="Agent" width="120" />
          <el-table-column prop="agent_type" label="类型" width="100" />
          <el-table-column prop="action" label="建议" width="80">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)">{{ actionName(row.action) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" width="100">
            <template #default="{ row }">
              {{ (row.confidence * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="reasoning" label="分析理由" show-overflow-tooltip />
        </el-table>

        <el-divider v-if="result.final_decision">最终决策</el-divider>

        <div v-if="result.final_decision" class="final-decision">
          <el-alert
            :title="`投资建议: ${actionName(result.final_decision.action)}`"
            :description="result.final_decision.summary"
            :type="getActionType(result.final_decision.action)"
            :closable="false"
            show-icon
          />
          <p class="consensus">共识度: {{ (result.final_decision.consensus * 100).toFixed(1) }}%</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Aim, Document } from '@element-plus/icons-vue'
import axios from 'axios'

interface AgentAnalysis {
  agent_name: string
  agent_type: string
  action: string
  confidence: number
  reasoning: string
}

interface FinalDecision {
  action: string
  consensus: number
  summary: string
}

interface AnalyzeResult {
  stock_code: string
  mode: string
  agent_analyses: AgentAnalysis[]
  final_decision: FinalDecision | null
}

const form = ref({
  stock_code: '',
  mode: 'parallel',
  agents: ['buffet', 'graham', 'fisher']
})

const loading = ref(false)
const result = ref<AnalyzeResult | null>(null)

const modeName = computed(() => {
  const map: Record<string, string> = {
    parallel: '并行独立',
    vote: '投票决策',
    debate: '辩论仲裁'
  }
  return map[result.value?.mode || ''] || ''
})

const actionName = (action: string) => {
  const map: Record<string, string> = {
    buy: '买入',
    sell: '卖出',
    hold: '持有'
  }
  return map[action] || action
}

const getActionType = (action: string) => {
  const map: Record<string, any> = {
    buy: 'success',
    sell: 'danger',
    hold: 'info'
  }
  return map[action] || 'info'
}

const handleAnalyze = async () => {
  if (!form.value.stock_code) {
    ElMessage.warning('请输入股票代码')
    return
  }

  if (form.value.agents.length === 0) {
    ElMessage.warning('请至少选择一个Agent')
    return
  }

  loading.value = true
  result.value = null

  try {
    const response = await axios.post('/api/v1/analyze/', {
      stock_code: form.value.stock_code,
      mode: form.value.mode,
      agents: form.value.agents.join(',')
    })

    result.value = response.data
    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.analyze-view {
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

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.final-decision {
  padding: 10px 0;
}

.consensus {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>
