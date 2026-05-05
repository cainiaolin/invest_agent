"""雷·达利欧AI增强Agent"""
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMDalioAgent(LLMAgent):
    """
    雷·达利欧AI增强Agent

    结合LLM推理能力与达利欧全天候策略：
    1. 使用思维链分析经济周期
    2. 评估债务周期和通胀影响
    3. 分析资产类別相关性
    4. LLM模拟达利欧的思维过程进行决策
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Ray Dalio (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的全天候策略：结合LLM推理与达利欧经济周期理论"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """使用LLM进行达利欧风格分析"""
        stock_code = state.get("stock_code", "")
        stock_data = await self._get_enriched_stock_data(stock_code)
        dalio_metrics = self._calculate_dalio_metrics(stock_data)
        knowledge = await self.knowledge.load_knowledge("dalio")
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, dalio_metrics)

        try:
            llm_result = await self.llm.reason_with_cot(cot_prompt)
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}，使用规则引擎")
            return await self._fallback_to_rule_engine(state)
        logger.info("dalio LM Result: %s", llm_result)   
        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "dalio_metrics": dalio_metrics
        })

        return self._validate_result(result, dalio_metrics)

    def _calculate_dalio_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """计算达利欧特定指标"""
        metrics = stock_data.get("metrics", {})

        return {
            "economic_cycle": metrics.get("economic_cycle", "expansion"),
            "inflation_rate": metrics.get("inflation_rate", 0),
            "interest_rate": metrics.get("interest_rate", 0)
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, dalio_metrics: Dict) -> str:
        """构建达利欧风格思维链Prompt"""
        stock_symbol = stock_data.get("symbol", "")
        stock_name = stock_data.get("name", "")

        prompt = f"""你是雷·达利欧(Ray Dalio)，桥水基金创始人，以全天候策略和经济周期分析著称。

## 标的
{stock_name}({stock_symbol})

## 宏观指标
经济周期: {dalio_metrics.get('economic_cycle', 'expansion')}
通胀率: {dalio_metrics.get('inflation_rate', 0):.2f}%
利率: {dalio_metrics.get('interest_rate', 0):.2f}%

## 分析任务
基于经济周期和债务周期，评估资产配置价值。

## 输出格式
```json
{{
  "thought_process": {{
    "cycle_analysis": "周期分析",
    "debt_cycle": "债务周期",
    "inflation_impact": "通胀影响",
    "decision_reasoning": "决策推理"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "建议理由",
  "key_metrics": {{}},
  "key_factors": ["因素1", "因素2"]
}}
```"""

        return prompt

    def _validate_result(self, result: Dict[str, Any], metrics: Dict) -> Dict[str, Any]:
        """验证结果"""
        return result
