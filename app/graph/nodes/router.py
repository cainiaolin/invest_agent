"""路由节点：根据用户需求选择合适的Agent"""
from typing import Dict, Any
from app.core.state import AnalysisState
from app.services.tushare_service import TushareService


async def router_node(state: AnalysisState) -> AnalysisState:
    """
    路由节点：获取股票数据并选择合适的Agent

    功能：
    1. 解析用户需求
    2. 获取股票数据
    3. 根据需求关键词选择Agent类型

    Args:
        state: 当前状态

    Returns:
        更新后的状态（包含股票数据和选中的Agent类型）
    """
    user_request = state.get("user_request", "").lower()
    stock_code = state.get("stock_code", "")

    # 初始化Tushare服务
    service = TushareService()

    try:
        # 获取股票基础数据（简化版，直接使用stock_code）
        # 实际应用中应从tushare获取完整数据
        stock_data = {
            "symbol": stock_code,
            "name": f"股票{stock_code}",
            "metrics": {
                "pe_ratio": 15.0,
                "pb_ratio": 2.5,
                "roe": 18.0,
                "debt_ratio": 35.0,
                "current_ratio": 1.8,
                "dividend_yield": 2.5,
                "revenue_growth": 12.0,
                "profit_growth": 15.0,
            },
            "moat_indicators": {
                "brand_strength": 7,
                "market_share": 25.0,
                "competitive_advantage": True,
            }
        }

        # 将股票数据添加到状态中（供后续Agent使用）
        state["stock_data"] = stock_data

        # 根据用户需求选择Agent类型
        agent_type = _select_agent_type(user_request)

        # 记录选择的Agent类型
        state["selected_agent_type"] = agent_type

        return state

    except Exception as e:
        state["error"] = f"路由节点错误: {str(e)}"
        return state


def _select_agent_type(user_request: str) -> str:
    """
    根据用户需求选择Agent类型

    规则：
    - 包含"价值"、"安全边际"、"护城河"、"低估" → value
    - 包含"成长"、"增长"、"潜力" → growth
    - 包含"宏观"、"经济"、"政策" → macro
    - 默认 → parallel（所有Agent）

    Args:
        user_request: 用户需求文本

    Returns:
        Agent类型: "value" | "growth" | "macro" | "parallel"
    """
    # 价值投资关键词
    value_keywords = ["价值", "安全边际", "护城河", "低估", "便宜", "折扣", "内在价值"]

    # 成长投资关键词
    growth_keywords = ["成长", "增长", "潜力", "扩张", "高增长", "成长性"]

    # 宏观分析关键词
    macro_keywords = ["宏观", "经济", "政策", "周期", "宏观经", "经济周期"]

    # 检查关键词
    for keyword in value_keywords:
        if keyword in user_request:
            return "value"

    for keyword in growth_keywords:
        if keyword in user_request:
            return "growth"

    for keyword in macro_keywords:
        if keyword in user_request:
            return "macro"

    # 默认使用所有Agent
    return "parallel"
