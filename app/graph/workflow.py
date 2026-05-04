"""LangGraph工作流定义"""
from langgraph.graph import StateGraph, END

from app.core.state import AnalysisState
from app.graph.nodes.router import router_node
from app.graph.nodes.agents import (
    parallel_agents_node,
    value_agent_node,
    growth_agent_node,
    macro_agent_node,
)
from app.graph.nodes.collaboration import vote_collaboration_node, debate_collaboration_node
from app.graph.nodes.output import output_node
from app.graph.edges.conditions import (
    route_to_agents,
    route_after_agents,
    route_after_collaboration,
)


def create_investment_workflow() -> StateGraph:
    """
    创建投资分析工作流

    工作流结构:
        1. router → 选择Agent
        2. agents → 并行执行Agent分析
        3. collaboration → 根据mode执行协作
           - vote: 投票模式
           - debate: 辩论模式
           - parallel: 直接输出
        4. output → 格式化输出

    Returns:
        StateGraph: 编译后的工作流图
    """
    # 创建状态图
    workflow = StateGraph(AnalysisState)

    # 添加节点
    workflow.add_node("router", router_node)
    workflow.add_node("parallel_agents", parallel_agents_node)
    workflow.add_node("value_agents", value_agent_node)
    workflow.add_node("growth_agents", growth_agent_node)
    workflow.add_node("macro_agents", macro_agent_node)
    workflow.add_node("vote_collaboration", vote_collaboration_node)
    workflow.add_node("debate_collaboration", debate_collaboration_node)
    workflow.add_node("output", output_node)

    # 设置入口点
    workflow.set_entry_point("router")

    # 添加边：router → agents（根据选择的Agent类型路由）
    workflow.add_conditional_edges(
        "router",
        route_to_agents,
        {
            "parallel": "parallel_agents",
            "value": "value_agents",
            "growth": "growth_agents",
            "macro": "macro_agents",
        },
    )

    # 添加边：agents → collaboration（根据mode路由）
    workflow.add_conditional_edges(
        "parallel_agents",
        route_after_agents,
        {
            "vote": "vote_collaboration",
            "debate": "debate_collaboration",
            "parallel": "output",
        },
    )

    # value_agents完成后也根据mode路由
    workflow.add_conditional_edges(
        "value_agents",
        route_after_agents,
        {
            "vote": "vote_collaboration",
            "debate": "debate_collaboration",
            "parallel": "output",
        },
    )

    # growth_agents完成后也根据mode路由
    workflow.add_conditional_edges(
        "growth_agents",
        route_after_agents,
        {
            "vote": "vote_collaboration",
            "debate": "debate_collaboration",
            "parallel": "output",
        },
    )

    # macro_agents完成后也根据mode路由
    workflow.add_conditional_edges(
        "macro_agents",
        route_after_agents,
        {
            "vote": "vote_collaboration",
            "debate": "debate_collaboration",
            "parallel": "output",
        },
    )

    # 添加边：collaboration → output
    workflow.add_edge("vote_collaboration", "output")
    workflow.add_edge("debate_collaboration", "output")

    # 添加边：output → END
    workflow.add_edge("output", END)

    # 编译工作流
    return workflow.compile()
