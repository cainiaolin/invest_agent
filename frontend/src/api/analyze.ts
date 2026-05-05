import axios from 'axios'

export interface LLMConfig {
  provider?: 'openai' | 'anthropic' | 'local' | 'deepseek' | 'glm'
  model?: string
  api_key?: string
  base_url?: string
  temperature?: number
  max_tokens?: number
}

export interface ThoughtProcess {
  step1_data_understanding?: string
  step2_philosophy_alignment?: string
  step3_dimension_scores?: string
  step4_risks?: string[]
  step5_decision_reasoning?: string
  step6_graham_quote?: string
}

export interface AnalyzeRequest {
  stock_code: string
  mode?: 'parallel' | 'vote' | 'debate'
  agents?: string
  agent_mode?: 'rule' | 'ai' | 'hybrid'
  llm_config?: LLMConfig
  verbose?: boolean
}

export interface AgentAnalysis {
  agent_name: string
  agent_type: string
  action: string
  confidence: number
  reasoning: string
  key_metrics: Record<string, any>
  price_target?: number
  analysis_mode?: string
  thought_process?: ThoughtProcess
  llm_model?: string
  validation_warning?: string
}

export interface FinalDecision {
  action: string
  consensus: number
  summary: string
}

export interface StockInfo {
  stock_name: string
  trade_date: string
  close: number
  pe_ttm: number
  pb: number
  total_mv: number
  circ_mv: number
  turnover_rate: number
  volume_ratio: number
}

export interface AnalyzeResult {
  stock_code: string
  mode: string
  agent_analyses: AgentAnalysis[]
  final_decision: FinalDecision | null
  stock_info: StockInfo | null
}

export async function analyzeStock(request: AnalyzeRequest): Promise<AnalyzeResult> {
  const response = await axios.post<AnalyzeResult>('/api/v1/analyze/', {
    stock_code: request.stock_code,
    mode: request.mode || 'parallel',
    agents: request.agents,
    agent_mode: request.agent_mode,
    llm_config: request.llm_config,
    verbose: request.verbose || false
  })
  return response.data
}
