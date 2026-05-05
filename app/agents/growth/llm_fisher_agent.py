"""菲利普·费雪AI增强Agent"""
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMFisherAgent(LLMAgent):
    """
    菲利普·费雪AI增强Agent

    结合LLM推理能力与费雪成长投资哲学：
    1. 使用思维链进行成长质量分析
    2. 评估管理层诚信度和能力
    3. 分析研发投入和长期成长潜力
    4. LLM模拟费雪的思维过程进行决策
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Philip Fisher (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的成长质量投资：结合LLM推理与费雪成长股理论"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行费雪风格分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        stock_code = state.get("stock_code", "")

        # 获取增强的股票数据
        stock_data = await self._get_enriched_stock_data(stock_code)

        # 计算费雪特定指标
        fisher_metrics = self._calculate_fisher_metrics(stock_data)

        # 加载费雪知识
        knowledge = await self.knowledge.load_knowledge("fisher")

        # 构建思维链Prompt
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, fisher_metrics)

        # 调用LLM推理
        try:
            llm_result = await self.llm.reason_with_cot(cot_prompt)
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}，使用规则引擎")
            return await self._fallback_to_rule_engine(state)

        # 解析和验证结果
        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "fisher_metrics": fisher_metrics
        })

        # 验证结果
        validated_result = self._validate_result(result, fisher_metrics)

        return validated_result

    def _calculate_fisher_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """计算费雪特定指标"""
        metrics = stock_data.get("metrics", {})

        return {
            "revenue_growth": metrics.get("revenue_growth", 0),
            "profit_growth": metrics.get("profit_growth", 0),
            "rd_ratio": metrics.get("rd_ratio", 0),
            "gross_margin": metrics.get("gross_margin", 0),
            "operating_margin": metrics.get("operating_margin", 0)
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, fisher_metrics: Dict) -> str:
        """构建费雪风格思维链Prompt"""
        stock_symbol = stock_data.get("symbol", "")
        stock_name = stock_data.get("name", "")
        metrics = stock_data.get("metrics", {})

        formatted_metrics = f"""
营收增长率: {fisher_metrics.get('revenue_growth', 0):.2f}%
利润增长率: {fisher_metrics.get('profit_growth', 0):.2f}%
研发投入比: {fisher_metrics.get('rd_ratio', 0):.2f}%
毛利率: {fisher_metrics.get('gross_margin', 0):.2f}%
营业利润率: {fisher_metrics.get('operating_margin', 0):.2f}%
""".strip()

        prompt = f"""你是菲利普·费雪(Philip Fisher)，成长投资先驱，以寻找高质量成长股著称。

## 当前分析标的
{stock_name}({stock_symbol})

## 公司基本面数据
{formatted_metrics}

## 费雪投资哲学核心原则
{knowledge.get('philosophy', '关注成长质量、管理层和长期竞争优势')}

## 分析任务（费雪15个原则）
请按照以下步骤进行成长股分析，输出结构化的投资决策。

## 输出格式要求
```json
{{
  "thought_process": {{
    "growth_quality": "成长质量评估",
    "management_assessment": "管理层评估",
    "competitive_position": "竞争地位",
    "profit_potential": "盈利潜力",
    "decision_reasoning": "决策推理"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "简洁的投资建议理由",
  "key_metrics": {{
    "revenue_growth": {fisher_metrics.get('revenue_growth', 0)}
  }},
  "key_factors": ["因素1", "因素2"]
}}
```"""

        return prompt

    def _validate_result(self, result: Dict[str, Any], metrics: Dict) -> Dict[str, Any]:
        """验证结果"""
        return result
