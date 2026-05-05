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

    <el-card class="mode-selector">
      <template #header>
        <span>分析模式</span>
      </template>

      <el-radio-group v-model="agentMode">
        <el-radio-button label="rule">
          <el-icon><Coin /></el-icon>
          规则引擎
        </el-radio-button>
        <el-radio-button label="ai">
          <el-icon><MagicStick /></el-icon>
          AI增强
        </el-radio-button>
        <el-radio-button label="hybrid">
          <el-icon><DataAnalysis /></el-icon>
          混合模式
        </el-radio-button>
      </el-radio-group>
    </el-card>

    <el-card v-if="agentMode === 'ai'" class="ai-config">
      <template #header>
        <span>LLM配置</span>
      </template>

      <el-form :model="llmConfig" label-width="100px">
        <el-form-item label="提供商">
          <el-select v-model="llmConfig.provider">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="本地模型" value="local" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型">
          <el-select v-model="llmConfig.model">
            <el-option label="GPT-4o" value="gpt-4o" />
            <el-option label="GPT-4 Turbo" value="gpt-4-turbo" />
            <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet-20241022" />
          </el-select>
        </el-form-item>

        <el-form-item label="Temperature">
          <el-slider v-model="llmConfig.temperature" :min="0" :max="1" :step="0.1" />
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

        <el-card v-if="result.stock_info" class="stock-info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span style="font-weight: 600;">Tushare 实时数据 — {{ result.stock_info.trade_date }}</span>
            </div>
          </template>
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="收盘价">
              <span class="price">{{ result.stock_info.close.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="市盈率(PE TTM)">
              {{ result.stock_info.pe_ttm.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="市净率(PB)">
              {{ result.stock_info.pb.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="换手率(%)">
              {{ result.stock_info.turnover_rate.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="量比">
              {{ result.stock_info.volume_ratio.toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="总市值(亿)">
              {{ (result.stock_info.total_mv / 1e8).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="流通市值(亿)">
              {{ (result.stock_info.circ_mv / 1e8).toFixed(2) }}
            </el-descriptions-item>
            <el-descriptions-item label="数据日期">
              <el-tag type="info" size="small">{{ result.stock_info.trade_date }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-divider>Agent分析结果</el-divider>

        <el-table :data="result.agent_analyses" border>
          <el-table-column prop="agent_name" label="Agent" width="110" />
          <el-table-column prop="agent_type" label="类型" width="80" />
          <el-table-column label="当前价" width="90">
            <template #default>
              {{ result.stock_info?.close?.toFixed(2) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column label="PE(TTM)" width="90">
            <template #default>
              {{ result.stock_info?.pe_ttm?.toFixed(2) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column label="PB" width="80">
            <template #default>
              {{ result.stock_info?.pb?.toFixed(2) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="action" label="建议" width="70">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)" size="small">{{ actionName(row.action) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" width="80">
            <template #default="{ row }">
              {{ (row.confidence * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column label="数据日期" width="100">
            <template #default>
              <el-tag type="info" size="small">{{ result.stock_info?.trade_date ?? '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reasoning" label="分析理由" min-width="200" show-overflow-tooltip />
        </el-table>

        <!-- Agent 详细分析卡片 -->
        <div v-for="analysis in result.agent_analyses" :key="analysis.agent_name" class="agent-detail-card">
          <el-card shadow="hover">
            <template #header>
              <div class="agent-detail-header">
                <span>{{ analysis.agent_name }} - 详细分析</span>
                <el-tag v-if="analysis.analysis_mode" type="info" size="small">
                  {{ formatAnalysisMode(analysis.analysis_mode) }}
                </el-tag>
              </div>
            </template>

            <div v-if="analysis.thought_process && analysis.analysis_mode === 'ai_llm'" class="thought-process">
              <el-collapse>
                <el-collapse-item title="查看AI分析思维过程" name="thought">
                  <div class="thought-steps">
                    <div v-for="(step, key) in analysis.thought_process" :key="key" class="step">
                      <h5>{{ formatStepName(key) }}</h5>
                      <p v-if="Array.isArray(step)">{{ step.join(', ') }}</p>
                      <p v-else>{{ step }}</p>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <div v-if="analysis.validation_warning" class="validation-warning">
              <el-alert
                title="验证警告"
                :description="analysis.validation_warning"
                type="warning"
                :closable="false"
                show-icon
              />
            </div>

            <div v-if="analysis.llm_model" class="llm-info">
              <el-tag type="success" size="small">模型: {{ analysis.llm_model }}</el-tag>
            </div>
          </el-card>
        </div>

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
import { Aim, Document, Coin, MagicStick, DataAnalysis } from '@element-plus/icons-vue'
import { analyzeStock, type LLMConfig, type AnalyzeResult, type AgentAnalysis } from '@/api/analyze'

const form = ref({
  stock_code: '',
  mode: 'parallel',
  agents: ['buffet', 'graham', 'fisher']
})

const agentMode = ref<'rule' | 'ai' | 'hybrid'>('rule')
const llmConfig = ref<LLMConfig>({
  provider: 'openai',
  model: 'gpt-4o',
  temperature: 0.7,
  max_tokens: 4000
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

const formatStepName = (key: string): string => {
  const names: Record<string, string> = {
    step1_data_understanding: '第1步：数据理解',
    step2_philosophy_alignment: '第2步：理念对照',
    step3_dimension_scores: '第3步：维度评分',
    step4_risks: '第4步：风险识别',
    step5_decision_reasoning: '第5步：决策推理',
    step6_graham_quote: '第6步：格雷厄姆语录'
  }
  return names[key] || key
}

const formatAnalysisMode = (mode: string): string => {
  const modes: Record<string, string> = {
    rule: '规则引擎',
    ai_llm: 'AI增强',
    hybrid: '混合模式'
  }
  return modes[mode] || mode
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
    result.value = await analyzeStock({
      stock_code: form.value.stock_code,
      mode: form.value.mode as 'parallel' | 'vote' | 'debate',
      agents: form.value.agents.join(','),
      agent_mode: agentMode.value,
      llm_config: agentMode.value === 'ai' ? llmConfig.value : undefined
    })

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

.stock-info-card {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
}

.stock-info-card .price {
  font-size: 18px;
  font-weight: 700;
  color: #cf1322;
}

.stock-info-card .el-descriptions__cell {
  padding: 8px 12px;
}

.mode-selector,
.ai-config {
  margin-top: 20px;
}

.agent-detail-card {
  margin-top: 16px;
}

.agent-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.thought-process {
  margin-bottom: 16px;
}

.thought-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.thought-steps .step {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.thought-steps .step h5 {
  margin: 0 0 8px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
}

.thought-steps .step p {
  margin: 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.validation-warning {
  margin-top: 12px;
}

.llm-info {
  margin-top: 12px;
  text-align: right;
}

.el-radio-button {
  margin-right: 8px;
}

.el-radio-button :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
