"""彼得·林奇AI增强Agent"""
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMLynchAgent(LLMAgent):
    """
    彼得·林奇AI增强Agent

    结合LLM推理能力与林奇GARP投资哲学：
    1. 使用思维链进行GARP分析
    2. 评估PEG比率和成长速度
    3. 分析"十倍股"潜力
    4. LLM模拟林奇的思维过程进行决策
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Peter Lynch (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的GARP投资：结合LLM推理与林奇PEG比率理论"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """使用LLM进行林奇风格分析"""
        stock_code = state.get("stock_code", "")
        stock_data = await self._get_enriched_stock_data(stock_code)
        lynch_metrics = self._calculate_lynch_metrics(stock_data)
        knowledge = await self.knowledge.load_knowledge("lynch")
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, lynch_metrics)

        try:
            llm_result = await self.llm.reason_with_cot(cot_prompt)
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}，使用规则引擎")
            return await self._fallback_to_rule_engine(state)

        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "lynch_metrics": lynch_metrics
        })

        return self._validate_result(result, lynch_metrics)

    def _calculate_lynch_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """计算林奇特定指标"""
        metrics = stock_data.get("metrics", {})
        pe = metrics.get("pe_ratio", 0)
        growth = metrics.get("revenue_growth", 0)

        peg = 0
        if pe > 0 and growth > 0:
            peg = pe / growth

        return {
            "pe": pe,
            "growth": growth,
            "peg": peg
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, lynch_metrics: Dict) -> str:
        """构建林奇风格思维链Prompt"""
        stock_symbol = stock_data.get("symbol", "")
        stock_name = stock_data.get("name", "")

        prompt = f"""你是彼得·林奇(Peter Lynch)，传奇基金经理，以GARP策略和PEG比率著称。

## 标的
{stock_name}({stock_symbol})

## 关键指标
PE: {lynch_metrics.get('pe', 0):.2f}
成长率: {lynch_metrics.get('growth', 0):.2f}%
PEG: {lynch_metrics.get('peg', 0):.2f}

## 分析任务
评估是否为GARP（合理价格成长）股票，是否有十倍股潜力。

## 输出格式
```json
{{
  "thought_process": {{
    "peg_analysis": "PEG分析",
    "category": "股票分类",
    "tenbagger_potential": "十倍股潜力",
    "decision_reasoning": "决策推理"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "建议理由",
  "key_metrics": {{"peg": {lynch_metrics.get('peg', 0)}}},
  "key_factors": ["因素1", "因素2"]
}}
```"""

        return prompt

    def _validate_result(self, result: Dict[str, Any], metrics: Dict) -> Dict[str, Any]:
        """验证结果"""
        return result
