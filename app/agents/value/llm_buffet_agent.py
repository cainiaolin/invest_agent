"""沃伦·巴菲特AI增强Agent"""
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMBuffetAgent(LLMAgent):
    """
    沃伦·巴菲特AI增强Agent

    结合LLM推理能力与巴菲特价值投资哲学：
    1. 使用思维链进行护城河分析
    2. 评估企业质量和长期竞争力
    3. 分析安全边际和内在价值
    4. LLM模拟巴菲特的思维过程进行决策
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Warren Buffett (AI)"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "AI增强的质量成长投资：结合LLM推理与巴菲特护城河理论"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行巴菲特风格分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        stock_code = state.get("stock_code", "")

        # 获取增强的股票数据
        stock_data = await self._get_enriched_stock_data(stock_code)

        # 计算巴菲特特定指标
        buffet_metrics = self._calculate_buffet_metrics(stock_data)

        # 加载巴菲特知识
        knowledge = await self.knowledge.load_knowledge("buffet")

        # 构建思维链Prompt
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, buffet_metrics)

        # 调用LLM推理
        try:
            llm_result = await self.llm.reason_with_cot(cot_prompt)
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}，使用规则引擎")
            return await self._fallback_to_rule_engine(state)
        logger.info("buffet LM Result: %s", llm_result)   
        # 解析和验证结果
        result = self._parse_llm_response(llm_result, stock_data)
     
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "buffet_metrics": buffet_metrics
        })

        # 验证结果
        validated_result = self._validate_result(result, buffet_metrics)

        return validated_result

    def _calculate_buffet_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """
        计算巴菲特特定指标

        Args:
            stock_data: 股票数据字典

        Returns:
            包含巴菲特指标的字典
        """
        metrics = stock_data.get("metrics", {})
        moat = stock_data.get("moat_indicators", {})

        return {
            "roe": metrics.get("roe", 0),
            "roic": metrics.get("roic", 0),
            "debt_ratio": metrics.get("debt_ratio", 0),
            "current_ratio": metrics.get("current_ratio", 0),
            "profit_margin": metrics.get("profit_margin", 0),
            "brand_strength": moat.get("brand_strength", 0),
            "market_share": moat.get("market_share", 0),
            "competitive_advantage": moat.get("competitive_advantage", False)
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, buffet_metrics: Dict) -> str:
        """
        构建巴菲特风格思维链Prompt

        Args:
            stock_data: 股票数据
            knowledge: 巴菲特知识
            buffet_metrics: 巴菲特指标

        Returns:
            Prompt字符串
        """
        stock_symbol = stock_data.get("symbol", "")
        stock_name = stock_data.get("name", "")
        price = stock_data.get("price", 0)
        metrics = stock_data.get("metrics", {})

        # 格式化指标
        formatted_metrics = f"""
PE比率: {metrics.get('pe_ratio', 0):.2f}
PB比率: {metrics.get('pb_ratio', 0):.2f}
ROE: {buffet_metrics.get('roe', 0):.2f}%
负债率: {buffet_metrics.get('debt_ratio', 0):.2f}%
流动比率: {buffet_metrics.get('current_ratio', 0):.2f}
利润率: {buffet_metrics.get('profit_margin', 0):.2f}%
品牌强度: {buffet_metrics.get('brand_strength', 0)}/10
市场份额: {buffet_metrics.get('market_share', 0):.1f}%
竞争优势: {'是' if buffet_metrics.get('competitive_advantage') else '否'}
""".strip()

        # 构建Prompt
        prompt = f"""你是沃伦·巴菲特(Warren Buffett)，价值投资大师，以护城河理论和长期持有著称。

## 当前分析标的
{stock_name}({stock_symbol})

## 公司基本面数据
{formatted_metrics}

## 巴菲特投资哲学核心原则
{knowledge.get('philosophy', '关注护城河、企业质量和长期价值')}

## 分析任务
请按照以下6个步骤进行深度价值分析，输出结构化的投资决策：

### 步骤1：企业质量评估
- 评估ROE和ROIC水平及稳定性
- 分析利润率和现金流质量
- 识别企业竞争优势的可持续性

### 步骤2：护城河分析
- 评估品牌护城河强度
- 分析网络效应和转换成本
- 判断成本优势是否可持续

### 步骤3：管理层评估
- 评估资本配置能力
- 分析股东回报政策
- 判断管理层诚信度

### 步骤4：估值合理性
- 计算内在价值（保守估计）
- 评估安全边际
- 比较市场价格与内在价值

### 步骤5：长期前景
- 分析行业发展趋势
- 评估企业未来10年前景
- 判断是否适合长期持有

### 步骤6：投资决策推理
基于以上分析，给出：
- **决策**: buy/sell/hold（三选一）
- **置信度**: 0.0-1.0之间的数值
- **关键因素**: 影响3-5个决策的关键因素列表
- **推理过程**: 详细的决策依据

## 输出格式要求
请严格按照以下JSON格式输出（不要添加其他文字）：

```json
{{
  "thought_process": {{
    "quality_assessment": "企业质量评估",
    "moat_analysis": "护城河分析",
    "management_evaluation": "管理层评估",
    "valuation_assessment": "估值评估",
    "long_term_prospects": "长期前景",
    "decision_reasoning": "决策推理"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "简洁的投资建议理由（1-2句话）",
  "key_metrics": {{
    "roe": {buffet_metrics.get('roe', 0)},
    "debt_ratio": {buffet_metrics.get('debt_ratio', 0)}
  }},
  "key_factors": ["因素1", "因素2", "因素3"],
  "buffett_quote": "巴菲特名言"
}}
```

请开始你的分析，记住：以合理价格买入优秀企业，长期持有，建立护城河是投资成功的关键。"""

        return prompt

    def _validate_result(self, result: Dict[str, Any], metrics: Dict) -> Dict[str, Any]:
        """
        验证LLM结果

        Args:
            result: LLM分析结果
            metrics: 计算指标

        Returns:
            验证后的结果
        """
        action = result.get("action", "hold")

        # 添加验证警告
        warnings = []
        if metrics.get("debt_ratio", 0) > 70:
            warnings.append("负债率过高")
        if metrics.get("roe", 0) < 10 and action == "buy":
            warnings.append("ROE较低但仍建议买入")

        if warnings:
            result["validation_warning"] = "; ".join(warnings)

        return result
