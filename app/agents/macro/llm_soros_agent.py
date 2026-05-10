"""乔治·索罗斯AI增强Agent"""
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMSorosAgent(LLMAgent):
    """
    乔治·索罗斯AI增强Agent

    结合LLM推理能力与索罗斯反身性理论：
    1. 使用思维链分析市场反身性
    2. 评估趋势拐点和泡沫风险
    3. 分析市场情绪和偏见
    4. LLM模拟索罗斯的思维过程进行决策
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "George Soros (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的宏观对冲：结合LLM推理与索罗斯反身性理论"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """使用LLM进行索罗斯风格分析"""
        stock_code = state.get("stock_code", "")
        stock_data = await self._get_enriched_stock_data(stock_code)
        soros_metrics = self._calculate_soros_metrics(stock_data)
        knowledge = await self.knowledge.load_knowledge("soros")
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, soros_metrics)

        try:
            llm_result = await self.llm.reason_with_cot(cot_prompt)
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}，使用规则引擎")
            return await self._fallback_to_rule_engine(state)
        logger.info("soros LM Result: %s", llm_result)   
        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "soros_metrics": soros_metrics
        })

        return self._validate_result(result, soros_metrics)

    def _calculate_soros_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """计算索罗斯特定指标"""
        metrics = stock_data.get("metrics", {})

        return {
            "price_momentum": metrics.get("price_momentum", 0),
            "volume_surge": metrics.get("volume_surge", False),
            "market_sentiment": metrics.get("market_sentiment", "neutral")
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, soros_metrics: Dict) -> str:
        """构建索罗斯风格思维链Prompt"""
        stock_symbol = stock_data.get("symbol", "")
        stock_name = stock_data.get("name", "")

        prompt = f"""你是乔治·索罗斯(George Soros)，量子基金创始人，以反身性理论和趋势拐点判断著称。

## 标的
{stock_name}({stock_symbol})

## 市场指标
价格动量: {soros_metrics.get('price_momentum', 0)}
成交量异动: {'是' if soros_metrics.get('volume_surge') else '否'}
市场情绪: {soros_metrics.get('market_sentiment', 'neutral')}

## 分析任务
应用反身性理论，寻找市场偏见和趋势拐点。

## 输出格式
```json
{{
  "thought_process": {{
    "reflexivity_analysis": "反身性分析",
    "market_bias": "市场偏见",
    "trend_inflection": "趋势拐点",
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
