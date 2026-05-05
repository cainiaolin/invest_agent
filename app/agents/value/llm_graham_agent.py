"""本杰明·格雷厄姆AI增强Agent"""
import math
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMGrahamAgent(LLMAgent):
    """
    本杰明·格雷厄姆AI增强Agent

    结合LLM推理能力与格雷厄姆价值投资哲学：
    1. 使用思维链进行深度价值分析
    2. 计算Graham公式内在价值和安全边际
    3. 评估净净机会(Net-Net)和盈利收益率
    4. LLM模拟格雷厄姆的思维过程进行决策
    """

    # Graham公式常数
    GRAHAM_CONSTANT = 22.5

    # 默认AAA债券收益率
    DEFAULT_AAA_BOND_YIELD = 3.0

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Benjamin Graham (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的深度价值投资：结合LLM推理与格雷厄姆投资哲学"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行格雷厄姆风格分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        stock_code = state.get("stock_code", "")

        # 获取增强的股票数据
        stock_data = await self._get_enriched_stock_data(stock_code)

        # 计算格雷厄姆特定指标
        graham_metrics = self._calculate_graham_metrics(stock_data)

        # 加载格雷厄姆知识
        knowledge = await self.knowledge.load_knowledge("graham")

        # 构建思维链Prompt
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, graham_metrics)

        # 调用LLM推理
        llm_result = await self.llm.reason_with_cot(cot_prompt)
        logger.info("graLLM Result: %s", llm_result)
        # 解析和验证结果
        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "graham_metrics": graham_metrics
        })

        # 验证结果
        validated_result = self._validate_result(result, graham_metrics)

        return validated_result

    def _calculate_graham_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """
        计算格雷厄姆特定指标

        Args:
            stock_data: 股票数据字典

        Returns:
            包含格雷厄姆指标的字典
        """
        metrics = stock_data.get("metrics", {})
        price = stock_data.get("price", 0)

        # 提取基本指标
        eps = metrics.get("eps", 0)
        bvps = metrics.get("bvps", 0)
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)

        # 1. 计算Graham公式内在价值
        # 公式: √(22.5 × EPS × BVPS)
        intrinsic_value = 0
        if eps > 0 and bvps > 0:
            try:
                intrinsic_value = math.sqrt(self.GRAHAM_CONSTANT * eps * bvps)
            except (ValueError, TypeError):
                intrinsic_value = 0

        # 2. 计算安全边际百分比
        # 安全边际 = (内在价值 - 价格) / 内在价值
        safety_margin = 0
        safety_margin_pct = 0
        if intrinsic_value > 0 and price > 0:
            safety_margin = (intrinsic_value - price) / intrinsic_value
            safety_margin_pct = safety_margin * 100

        # 3. 计算盈利收益率
        # 盈利收益率 = 1/PE
        earnings_yield = 0
        if pe_ratio > 0:
            earnings_yield = 1.0 / pe_ratio

        # 4. 净净营运资本评估
        net_net_wc = stock_data.get("net_net_working_capital", 0)
        net_net_discount = 0
        if net_net_wc > 0 and price > 0:
            net_net_discount = (net_net_wc - price) / net_net_wc * 100

        # 5. AAA债券收益率要求
        aaa_bond_yield = stock_data.get("aaa_bond_yield", self.DEFAULT_AAA_BOND_YIELD)
        required_earnings_yield = (aaa_bond_yield / 100) * 2

        return {
            "intrinsic_value": round(intrinsic_value, 2),
            "safety_margin": round(safety_margin, 4),
            "safety_margin_pct": round(safety_margin_pct, 2),
            "earnings_yield": round(earnings_yield, 4),
            "net_net_working_capital": round(net_net_wc, 2),
            "net_net_discount": round(net_net_discount, 2),
            "required_earnings_yield": round(required_earnings_yield, 4),
            "price": round(price, 2),
            "eps": round(eps, 2),
            "bvps": round(bvps, 2),
            "pe_ratio": round(pe_ratio, 2),
            "pb_ratio": round(pb_ratio, 2)
        }

    def _build_cot_prompt(
        self,
        stock_data: Dict,
        knowledge: Dict,
        graham_metrics: Dict
    ) -> str:
        """
        构建格雷厄姆风格的思维链Prompt

        Args:
            stock_data: 股票数据
            knowledge: 格雷厄姆知识
            graham_metrics: 格雷厄姆指标

        Returns:
            思维链Prompt字符串
        """
        stock_name = stock_data.get("name", "该股票")
        stock_symbol = stock_data.get("symbol", "")

        # 格式化股票数据
        formatted_metrics = self._format_stock_data(graham_metrics)

        # 构建Prompt
        prompt = f"""你是本杰明·格雷厄姆(Benjamin Graham)，价值投资之父，以深度价值分析和安全边际原则闻名。

## 当前分析标的
{stock_name}({stock_symbol})

## 公司基本面数据
{formatted_metrics}

## 格雷厄姆投资哲学核心原则
{knowledge.get('philosophy', '关注安全边际、内在价值和深度价值机会')}

## 分析任务
请按照以下6个步骤进行深度价值分析，输出结构化的投资决策：

### 步骤1：数据理解与估值计算
- 评估财务数据的质量和可靠性
- 计算并解释内在价值和安全边际的意义
- 识别数据中的异常或危险信号

### 步骤2：投资哲学对齐
- 对照格雷厄姆的核心原则评估该标的
- 判断是否符合"深度价值"标准
- 识别价值陷阱的潜在风险

### 步骤3：维度评分（0-100分）
请对以下维度打分并解释：
- 内在价值吸引力（基于安全边际）
- 净净机会（Net-Net bargain）
- 盈利收益率（相对于AAA债券）
- 财务安全性（负债率、流动性）
- 估值合理性（PE、PB水平）

### 步骤4：风险识别
- 识别该投资的主要下行风险
- 评估最坏情况下的潜在损失
- 判断安全边际是否足够覆盖这些风险

### 步骤5：投资决策推理
基于以上分析，给出：
- **决策**: buy/sell/hold（三选一）
- **置信度**: 0.0-1.0之间的数值
- **关键因素**: 影响3-5个决策的关键因素列表
- **推理过程**: 详细的决策依据

### 步骤6：格雷厄姆名言引用
引用一句格雷厄姆的投资名言来支持你的决策。

## 输出格式要求
请严格按照以下JSON格式输出（不要添加其他文字）：

```json
{{
  "thought_process": {{
    "data_understanding": "数据理解总结",
    "philosophy_alignment": "哲学对齐分析",
    "dimension_scores": {{
      "intrinsic_value": 分数,
      "net_net": 分数,
      "earnings_yield": 分数,
      "financial_safety": 分数,
      "valuation": 分数
    }},
    "risk_identification": ["风险1", "风险2", "风险3"],
    "decision_reasoning": "详细推理过程"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "简洁的投资建议理由（1-2句话）",
  "key_metrics": {{
    "intrinsic_value": {graham_metrics['intrinsic_value']},
    "safety_margin_pct": {graham_metrics['safety_margin_pct']},
    "earnings_yield": {graham_metrics['earnings_yield']}
  }},
  "key_factors": ["因素1", "因素2", "因素3"],
  "graham_quote": "格雷厄姆名言"
}}
```

请开始你的分析，记住：安全边际是投资的基石，在别人恐惧时贪婪，但永远不要在没有足够保护的情况下投资。
"""

        return prompt

    def _validate_result(self, result: Dict, graham_metrics: Dict) -> Dict:
        """
        验证LLM输出结果

        Args:
            result: LLM分析结果
            graham_metrics: 格雷厄姆指标

        Returns:
            验证后的结果
        """
        # 基本验证
        action = result.get("action", "hold")
        confidence = result.get("confidence", 0.5)

        # 验证action在有效范围内
        valid_actions = ["buy", "sell", "hold"]
        if action not in valid_actions:
            logger.warning(f"无效的action: {action}，修正为hold")
            result["action"] = "hold"

        # 验证confidence在[0,1]范围内
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            logger.warning(f"无效的confidence: {confidence}，修正为0.5")
            result["confidence"] = 0.5

        # 格雷厄姆特定验证：安全边际为负时不应该建议买入
        safety_margin = graham_metrics.get("safety_margin", 0)
        if safety_margin < 0 and result["action"] == "buy":
            logger.warning(
                f"安全边际为负({safety_margin:.2%})但LLM建议买入，"
                f"根据格雷厄姆原则修正为sell"
            )
            result["action"] = "sell"
            result["validation_warning"] = (
                f"安全边际为负({safety_margin:.2%})，已根据格雷厄姆原则"
                f"将决策从buy修正为sell"
            )

        # 验证key_metrics存在
        if "key_metrics" not in result:
            result["key_metrics"] = {}

        # 确保包含格雷厄姆核心指标
        result["key_metrics"].update({
            "intrinsic_value": graham_metrics["intrinsic_value"],
            "safety_margin_pct": graham_metrics["safety_margin_pct"],
            "earnings_yield": graham_metrics["earnings_yield"]
        })

        return result

    def _format_stock_data(self, graham_metrics: Dict) -> str:
        """
        格式化股票数据为Markdown列表

        Args:
            graham_metrics: 格雷厄姆指标字典

        Returns:
            格式化的Markdown字符串
        """
        lines = [
            "### 核心指标",
            f"- **当前价格**: {graham_metrics['price']:.2f}元",
            f"- **内在价值**: {graham_metrics['intrinsic_value']:.2f}元",
            f"- **安全边际**: {graham_metrics['safety_margin_pct']:.2f}%",
            "",
            "### 估值指标",
            f"- **每股收益(EPS)**: {graham_metrics['eps']:.2f}元",
            f"- **每股净资产(BVPS)**: {graham_metrics['bvps']:.2f}元",
            f"- **市盈率(PE)**: {graham_metrics['pe_ratio']:.2f}",
            f"- **市净率(PB)**: {graham_metrics['pb_ratio']:.2f}",
            "",
            "### 收益指标",
            f"- **盈利收益率**: {graham_metrics['earnings_yield']:.2%}",
            f"- **要求收益率**: {graham_metrics['required_earnings_yield']:.2%} (2×AAA债券)",
            "",
            "### 净净分析",
            f"- **净净营运资本**: {graham_metrics['net_net_working_capital']:.2f}亿元",
            f"- **净净折扣率**: {graham_metrics['net_net_discount']:.2f}%"
        ]

        return "\n".join(lines)
