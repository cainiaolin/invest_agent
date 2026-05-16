"""
Buffett Search Agent - 巴菲特投资哲学的搜索增强Agent

实现沃伦·巴菲特价值投资哲学的智能分析，专注于护城河分析、
管理层评估、财务质量判断和估值分析。
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.agents.search_enhanced_agent import SearchEnhancedAgent
from app.models.search_strategy import SearchStrategy


class BuffetSearchAgent(SearchEnhancedAgent):
    """巴菲特搜索增强Agent - 实现巴菲特价值投资哲学"""

    def __init__(self, tushare_service, search_service, llm_service, knowledge_service):
        """
        初始化BuffetSearchAgent

        Args:
            tushare_service: Tushare数据服务
            search_service: 搜索服务
            llm_service: LLM服务
            knowledge_service: 知识服务
        """
        # 调用父类初始化
        super().__init__(
            tushare_service=tushare_service,
            search_service=search_service,
            llm_service=llm_service,
            knowledge_service=knowledge_service,
            master_name="Buffett"
        )

    @property
    def name(self) -> str:
        """返回Agent名称"""
        return "Buffett"

    @property
    def style(self) -> str:
        """返回投资风格"""
        return "价值投资 - 护城河与安全边际"

    def get_search_strategy(self) -> SearchStrategy:
        """
        获取巴菲特的搜索策略配置

        巴菲特关注基本面分析，重视护城河、管理层质量和财务健康，
        不太关注短期市场情绪，追求长期价值。
        """
        return SearchStrategy(
            search_basic_info=True,        # 关注财报和公告
            search_market_sentiment=False, # 不太关注短期情绪
            search_industry=True,         # 关注行业地位
            search_competitors=True,      # 关注竞争格局
            time_horizon=30,               # 看更长期（30天）
            min_reliability=0.7,          # 要求高可信度
            max_results_per_source=15     # 需要更多信息
        )

    def _build_cot_prompt(self, stock_data: Dict[str, Any], knowledge: Dict[str, Any],
                          search_context: str = "") -> str:
        """
        构建巴菲特风格的Chain of Thought Prompt

        Args:
            stock_data: 股票基础数据
            knowledge: 大师知识库
            search_context: 搜索增强上下文信息

        Returns:
            构建好的分析Prompt
        """

        # 巴菲特投资哲学核心原则
        buffet_philosophy = f"""
## 巴菲特投资哲学核心原则

### 投资哲学
{knowledge.get('investment_philosophy', '寻找具有持久竞争优势的企业，以合理的价格买入并长期持有')}

### 关键原则
"""

        for i, principle in enumerate(knowledge.get('key_principles', []), 1):
            buffet_philosophy += f"{i}. {principle}\n"

        # 案例研究
        if knowledge.get('case_studies'):
            buffet_philosophy += "\n### 经典案例\n"
            for case in knowledge['case_studies'][:3]:  # 只显示前3个案例
                buffet_philosophy += f"- {case}\n"

        # 当前股票数据
        stock_info = f"""
## 目标股票分析
- 公司名称: {stock_data.get('name', '未知')}
- 股票代码: {stock_data.get('code', '未知')}
- 当前价格: {stock_data.get('price', '未知')}
- 市值: {stock_data.get('market_cap', '未知')}
"""

        # 添加关键财务指标
        if stock_data.get('pe'):
            stock_info += f"- 市盈率(PE): {stock_data['pe']}\n"
        if stock_data.get('pb'):
            stock_info += f"- 市净率(PB): {stock_data['pb']}\n"
        if stock_data.get('roe'):
            stock_info += f"- 净资产收益率(ROE): {stock_data['roe']}%\n"
        if stock_data.get('eps'):
            stock_info += f"- 每股收益(EPS): {stock_data['eps']}\n"
        if stock_data.get('market_cap'):
            stock_info += f"- 市值: {stock_data['market_cap']}\n"

        # 搜索增强信息
        enhanced_context = ""
        if search_context:
            enhanced_context = f"""
## 搜索增强信息
{search_context}
"""

        # 分析框架
        analysis_framework = """
## 分析框架

### 1. 护城河分析
- 评估企业的竞争优势是否持久
- 分析品牌优势、转换成本、网络效应、成本优势等
- 竞争优势是否容易被模仿或替代

### 2. 管理层评估
- 管理层是否诚信、能力出众
- 是否以股东利益为重
- 资本配置能力如何

### 3. 财务质量分析
- 盈利能力是否稳定且强劲
- 负债水平是否合理
- 现金流是否充足
- 利润率趋势如何

### 4. 估值判断
- 当前估值是否合理
- 是否有足够的安全边际
- 与内在价值的对比

### 5. 长期前景
- 行业发展趋势
- 公司增长潜力
- 可预见的挑战

## 任务要求
请基于巴菲特投资哲学对上述股票进行深入分析，必须输出JSON格式，包含以下字段：

```json
{
    "action": "BUY" | "HOLD" | "SELL",
    "confidence": 0.0-1.0,
    "reasoning": "详细的投资理由",
    "key_metrics": {
        "pe": 15.2,
        "pb": 2.1,
        "roe": 18.5
    },
    "key_factors": ["护城河宽阔", "管理层优秀", "估值合理"],
    "thought_process": "完整的思考过程"
}
```

请仔细分析每个因素，给出投资建议。
"""

        # 组合完整的prompt
        full_prompt = buffet_philosophy + stock_info + enhanced_context + analysis_framework

        return full_prompt

    async def analyze_with_enhanced_context(self, state: Dict[str, Any],
                                           analysis_context: Dict[str, Any],
                                           search_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用增强上下文进行抽象分析（子类必须实现）

        Args:
            state: 分析状态
            analysis_context: 分析上下文
            search_summary: 搜索摘要（可选）

        Returns:
            Dict: 分析结果
        """
        # 调用基类的搜索增强方法
        result = await self._analyze_with_search_enhancement(
            state,
            await self._get_enriched_stock_data(state.get("stock_code", "")),
            await self.knowledge.load_knowledge(self.master_name)
        )

        # 添加额外的上下文信息
        result.update({
            "analysis_context": analysis_context,
            "search_summary": search_summary
        })

        return result