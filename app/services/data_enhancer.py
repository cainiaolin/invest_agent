"""数据增强服务 - 基于Tushare数据的智能分析增强

不依赖可能不稳定的第三方API，而是：
1. 充分利用Tushare已有的可靠数据
2. 智能分析和推导更多信息
3. 明确标注数据可用性
4. 改进LLM的Prompt，让AI更好地分析现有数据
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class DataEnhancerService:
    """
    数据增强服务

    基于Tushare数据提供智能分析和补充
    """

    @staticmethod
    def enhance_stock_data_for_llm(stock_data: Dict[str, Any], stock_name: str, stock_code: str) -> str:
        """
        为LLM增强股票数据展示

        将Tushare的数据以结构化方式呈现，帮助LLM更好地理解和分析

        Args:
            stock_data: Tushare获取的股票数据
            stock_name: 股票名称
            stock_code: 股票代码

        Returns:
            格式化的数据增强文本
        """
        sections = []

        # 1. 基本信息
        sections.append(f"""## 基本信息
- 股票名称: {stock_name}
- 股票代码: {stock_code}
- 当前价格: {stock_data.get('price', 'N/A')}元
""")

        # 2. 财务指标分析
        metrics = stock_data.get('metrics', {})
        if metrics:
            sections.append(DataEnhancerService._analyze_financial_metrics(metrics))

        # 3. 护城河分析
        moat = stock_data.get('moat_indicators', {})
        if moat:
            sections.append(DataEnhancerService._analyze_moat_indicators(moat))

        # 4. 数据可用性说明
        sections.append(DataEnhancerService._explain_data_availability(stock_data))

        return "\n".join(sections)

    @staticmethod
    def _analyze_financial_metrics(metrics: Dict[str, Any]) -> str:
        """分析财务指标"""
        lines = ["## 财务指标分析"]

        # 盈利能力
        lines.append("\n### 盈利能力")
        roe = metrics.get('roe', 0)
        net_margin = metrics.get('net_margin', 0)
        gross_margin = metrics.get('gross_margin', 0)

        lines.append(f"- ROE（净资产收益率）: {roe:.2f}%")
        if roe >= 15:
            lines.append(f"  → 评估: 优秀（ROE≥15%表明公司盈利能力强）")
        elif roe >= 10:
            lines.append(f"  → 评估: 良好（ROE≥10%表明公司盈利能力较好）")
        else:
            lines.append(f"  → 评估: 一般（ROE<10%需要关注盈利能力）")

        if net_margin > 0:
            lines.append(f"- 净利率: {net_margin:.2f}%")
            if net_margin >= 20:
                lines.append(f"  → 评估: 优秀（净利率≥20%表明盈利质量高）")

        if gross_margin > 0:
            lines.append(f"- 毛利率: {gross_margin:.2f}%")

        # 成长能力
        lines.append("\n### 成长能力")
        revenue_growth = metrics.get('revenue_growth', 0)
        profit_growth = metrics.get('profit_growth', 0)

        if revenue_growth != 0:
            lines.append(f"- 营收增长率: {revenue_growth:.2f}%")
            if revenue_growth > 20:
                lines.append(f"  → 评估: 高成长")
            elif revenue_growth > 10:
                lines.append(f"  → 评估: 稳健成长")
            elif revenue_growth > 0:
                lines.append(f"  → 评估: 低成长")

        if profit_growth != 0:
            lines.append(f"- 利润增长率: {profit_growth:.2f}%")

        # 财务健康
        lines.append("\n### 财务健康")
        debt_ratio = metrics.get('debt_ratio', 0)
        current_ratio = metrics.get('current_ratio', 0)

        if debt_ratio > 0:
            lines.append(f"- 资产负债率: {debt_ratio:.2f}%")
            if debt_ratio < 30:
                lines.append(f"  → 评估: 健康（负债率低）")
            elif debt_ratio < 60:
                lines.append(f"  → 评估: 合理")
            else:
                lines.append(f"  → 评估: 需关注（负债率较高）")

        if current_ratio > 0:
            lines.append(f"- 流动比率: {current_ratio:.2f}")
            if current_ratio >= 2:
                lines.append(f"  → 评估: 优秀（流动能力强）")
            elif current_ratio >= 1:
                lines.append(f"  → 评估: 合理")

        # 估值指标
        lines.append("\n### 估值指标")
        pe_ratio = metrics.get('pe_ratio', 0)
        pb_ratio = metrics.get('pb_ratio', 0)

        if pe_ratio > 0:
            lines.append(f"- 市盈率(PE): {pe_ratio:.2f}")
            if pe_ratio < 15:
                lines.append(f"  → 评估: 估值较低")
            elif pe_ratio < 30:
                lines.append(f"  → 评估: 估值合理")
            else:
                lines.append(f"  → 评估: 估值较高")

        if pb_ratio > 0:
            lines.append(f"- 市净率(PB): {pb_ratio:.2f}")

        return "\n".join(lines)

    @staticmethod
    def _analyze_moat_indicators(moat: Dict[str, Any]) -> str:
        """分析护城河指标"""
        lines = ["## 护城河指标"]

        brand_strength = moat.get('brand_strength', 0)
        market_share = moat.get('market_share', 0)
        competitive_advantage = moat.get('competitive_advantage', False)

        if brand_strength > 0:
            lines.append(f"- 品牌强度: {brand_strength}/10")
            if brand_strength >= 7:
                lines.append(f"  → 评估: 具有品牌护城河")

        if market_share > 0:
            lines.append(f"- 市场份额: {market_share:.1f}%")
            if market_share >= 20:
                lines.append(f"  → 评估: 市场地位稳固")

        if competitive_advantage:
            lines.append("- 竞争优势: 是")
            lines.append(f"  → 评估: 具有竞争优势")
        else:
            lines.append("- 竞争优势: 数据显示为否，但这不代表没有优势，可能需要更深入分析")

        return "\n".join(lines)

    @staticmethod
    def _explain_data_availability(stock_data: Dict[str, Any]) -> str:
        """说明数据可用性"""
        lines = ["## 数据可用性说明"]

        lines.append("本分析基于以下数据源：")
        lines.append("[OK] Tushare官方数据 - 财务指标、估值数据")
        lines.append("[OK] 历史交易数据")

        # 检查缺失的关键数据
        missing = []
        metrics = stock_data.get('metrics', {})

        critical_fields = {
            'roe': 'ROE（净资产收益率）',
            'debt_ratio': '资产负债率',
            'pe_ratio': '市盈率',
            'revenue_growth': '营收增长率',
        }

        for field, name in critical_fields.items():
            if field not in metrics or metrics[field] == 0:
                missing.append(name)

        if missing:
            lines.append(f"\n注：以下数据本次未获取到：{', '.join(missing)}")
            lines.append("这可能是因为：")
            lines.append("- 数据暂未更新")
            lines.append("- 需要更高级别的Tushare权限")
            lines.append("- 数据确实不存在（如新股）")
        else:
            lines.append("\n[OK] 所有关键数据均已获取")

        lines.append("\n重要提示：")
        lines.append("- 请基于已有数据进行分析")
        lines.append("- 对于缺失数据，明确标注'数据不可用'而非猜测")
        lines.append("- 如果关键数据缺失，建议'hold'（观望）而非强行决策")

        return "\n".join(lines)


def create_enhanced_prompt_template(master_name: str, stock_data: Dict, stock_name: str, stock_code: str) -> str:
    """
    创建增强的分析Prompt

    Args:
        master_name: 大师名称
        stock_data: 股票数据
        stock_name: 股票名称
        stock_code: 股票代码

    Returns:
        增强的Prompt
    """
    # 获取数据增强说明
    data_enhancement = DataEnhancerService.enhance_stock_data_for_llm(
        stock_data, stock_name, stock_code
    )

    # 根据不同的大师创建专用的Prompt
    if master_name == "buffet":
        return f"""你是沃伦·巴菲特(Warren Buffett)，价值投资大师，以护城河理论和长期持有著称。

## 当前分析标的
{stock_name}({stock_code})

{data_enhancement}

## 巴菲特投资分析框架

基于以上数据，请按照以下步骤进行深度分析：

### 步骤1：企业质量评估
- 基于ROE和利润率评估盈利能力
- 评估资产负债率和流动比率判断财务健康
- **如果有品牌强度数据**：分析品牌护城河
- **如果没有品牌数据**：基于财务表现推断竞争优势

### 步骤2：护城河分析
- **如果有市场数据**：评估市场份额和竞争地位
- **如果数据缺失**：基于盈利能力的持续性判断是否有护城河
- 高ROE持续存在通常意味着有某种竞争优势

### 步骤3：估值合理性
- 使用PE和PB进行初步估值
- 评估当前价格是否合理
- **注意**：如果没有足够数据，保守估计

### 步骤4：长期前景
- 基于成长能力评估未来潜力
- 判断是否适合长期持有

### 步骤5：投资决策
- **决策原则**：如果有足够数据 → 给出明确建议（buy/sell/hold）
- **如果数据不足**：给出"hold"（观望）建议，并说明需要什么数据才能做出决策

## 输出要求

请严格按照以下JSON格式输出（不要添加其他文字）：

```json
{{
  "thought_process": {{
    "quality_assessment": "基于ROE={roe}%、净利率={margin}%等指标评估企业质量",
    "moat_analysis": "基于品牌强度{brand}/10、市场份额{share}%等分析护城河，如果数据缺失则说明'基于{roe}%的ROE推测存在竞争优势'",
    "management_evaluation": "基于财务表现（如利润留存、现金流等）评估管理层",
    "valuation_assessment": "基于PE={pe}、PB={pb}进行估值",
    "long_term_prospects": "基于营收增长{growth}%评估长期前景"
  }},
  "action": "buy/sell/hold",
  "confidence": 0.0-1.0,
  "reasoning": "简洁的投资建议理由（明确基于哪些数据）",
  "key_metrics": {{
    "roe": {roe},
    "debt_ratio": {debt_ratio}
  }},
  "key_factors": ["因素1", "因素2", "因素3"],
  "data_completeness": "high/medium/low - 数据完整度评估"
}}
```

**重要**：
1. 充分利用已有数据进行分析
2. 缺失数据时明确说明，不要猜测
3. 数据不足时选择hold（观望）而非强行决策
4. 保持分析的真实性和可靠性
"""

    elif master_name == "graham":
        return f"""你是本杰明·格雷厄姆(Benjamin Graham)，价值投资之父。

## 当前分析标的
{stock_name}({stock_code})

{data_enhancement}

## 格雷厄姆投资分析

基于以上数据，请进行深度价值分析：

**关键原则**：
1. 安全边际至上
2. 基于已有数据保守估值
3. 数据缺失时选择观望

请按照JSON格式输出分析结果。

**注意**：数据完整度低时，confidence应该较低，倾向于hold。
"""

    # 其他大师的Prompt可以类似处理...

    return f"""你是{master_name}投资大师。

## 当前分析标的
{stock_name}({stock_code})

{data_enhancement}

请基于以上数据进行分析。对于缺失的数据，明确标注"数据不可用"。

按照JSON格式输出分析结果。
"""
