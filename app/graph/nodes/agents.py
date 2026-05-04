"""Agent执行节点：并行或分类执行Agent分析"""
from typing import List, Dict, Any
from app.core.state import AnalysisState, AgentAnalysis
from app.agents.base import BaseAgent
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.value.graham_agent import GrahamAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.macro.dalio_agent import DalioAgent
from app.services.tushare_service import TushareService
from app.core.config import settings


async def parallel_agents_node(state: AnalysisState) -> AnalysisState:
    """
    并行执行所有Agent的分析

    执行所有6个Agent：Buffett、Graham、Fisher、Lynch、Soros、Dalio

    Args:
        state: 当前状态

    Returns:
        更新后的状态（包含所有Agent的分析结果）
    """
    stock_data = state.get("stock_data", {})

    # 创建Tushare服务
    tushare_service = TushareService(settings.tushare_token)

    # 所有Agent列表
    all_agents: List[BaseAgent] = [
        BuffetAgent(tushare_service),
        GrahamAgent(tushare_service),
        FisherAgent(tushare_service),
        LynchAgent(tushare_service),
        SorosAgent(tushare_service),
        DalioAgent(tushare_service),
    ]

    # 并行执行所有Agent
    analyses = []
    for agent in all_agents:
        try:
            # 执行分析（使用state而不是stock_data）
            analysis_result = await agent.analyze(state)

            # 构造AgentAnalysis
            agent_analysis = AgentAnalysis(
                agent_name=agent.name,
                agent_type=_get_agent_type(agent.name),
                action=analysis_result.get("action", "hold"),
                confidence=analysis_result.get("confidence", 0.0),
                reasoning=analysis_result.get("reasoning", ""),
                key_metrics=analysis_result.get("key_metrics", {}),
                price_target=None,
            )

            analyses.append(agent_analysis)

        except Exception as e:
            # 记录错误但继续执行其他Agent
            print(f"Agent {agent.name} 执行失败: {str(e)}")
            continue

    # 更新状态
    state["agent_analyses"] = analyses

    return state


async def value_agent_node(state: AnalysisState) -> AnalysisState:
    """
    执行价值投资Agent的分析

    执行Buffett和Graham两个Agent

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    stock_data = state.get("stock_data", {})

    # 创建Tushare服务
    tushare_service = TushareService(settings.tushare_token)

    # 价值投资Agent
    value_agents: List[BaseAgent] = [
        BuffetAgent(tushare_service),
        GrahamAgent(tushare_service)
    ]

    analyses = []
    for agent in value_agents:
        try:
            analysis_result = await agent.analyze(state)

            agent_analysis = AgentAnalysis(
                agent_name=agent.name,
                agent_type="value",
                action=analysis_result.get("action", "hold"),
                confidence=analysis_result.get("confidence", 0.0),
                reasoning=analysis_result.get("reasoning", ""),
                key_metrics=analysis_result.get("key_metrics", {}),
                price_target=None,
            )

            analyses.append(agent_analysis)

        except Exception as e:
            print(f"Agent {agent.name} 执行失败: {str(e)}")
            continue

    state["agent_analyses"] = analyses

    return state


async def growth_agent_node(state: AnalysisState) -> AnalysisState:
    """
    执行成长投资Agent的分析

    执行Fisher和Lynch两个Agent

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    stock_data = state.get("stock_data", {})

    # 创建Tushare服务
    tushare_service = TushareService(settings.tushare_token)

    # 成长投资Agent
    growth_agents: List[BaseAgent] = [
        FisherAgent(tushare_service),
        LynchAgent(tushare_service)
    ]

    analyses = []
    for agent in growth_agents:
        try:
            analysis_result = await agent.analyze(state)

            agent_analysis = AgentAnalysis(
                agent_name=agent.name,
                agent_type="growth",
                action=analysis_result.get("action", "hold"),
                confidence=analysis_result.get("confidence", 0.0),
                reasoning=analysis_result.get("reasoning", ""),
                key_metrics=analysis_result.get("key_metrics", {}),
                price_target=None,
            )

            analyses.append(agent_analysis)

        except Exception as e:
            print(f"Agent {agent.name} 执行失败: {str(e)}")
            continue

    state["agent_analyses"] = analyses

    return state


async def macro_agent_node(state: AnalysisState) -> AnalysisState:
    """
    执行宏观分析Agent的分析

    执行Soros和Dalio两个Agent

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    stock_data = state.get("stock_data", {})

    # 创建Tushare服务
    tushare_service = TushareService(settings.tushare_token)

    # 宏观分析Agent
    macro_agents: List[BaseAgent] = [
        SorosAgent(tushare_service),
        DalioAgent(tushare_service)
    ]

    analyses = []
    for agent in macro_agents:
        try:
            analysis_result = await agent.analyze(state)

            agent_analysis = AgentAnalysis(
                agent_name=agent.name,
                agent_type="macro",
                action=analysis_result.get("action", "hold"),
                confidence=analysis_result.get("confidence", 0.0),
                reasoning=analysis_result.get("reasoning", ""),
                key_metrics=analysis_result.get("key_metrics", {}),
                price_target=None,
            )

            analyses.append(agent_analysis)

        except Exception as e:
            print(f"Agent {agent.name} 执行失败: {str(e)}")
            continue

    state["agent_analyses"] = analyses

    return state


def _get_agent_type(agent_name: str) -> str:
    """
    根据Agent名称获取类型

    Args:
        agent_name: Agent名称

    Returns:
        Agent类型
    """
    value_agents = ["Warren Buffett", "Benjamin Graham"]
    growth_agents = ["Philip Fisher", "Peter Lynch"]
    macro_agents = ["George Soros", "Ray Dalio"]

    if agent_name in value_agents:
        return "value"
    elif agent_name in growth_agents:
        return "growth"
    elif agent_name in macro_agents:
        return "macro"
    else:
        return "unknown"
