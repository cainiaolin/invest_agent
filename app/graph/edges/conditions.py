"""条件边函数：控制工作流的路由逻辑"""
from typing import Literal
from app.core.state import AnalysisState


def route_to_agents(state: AnalysisState) -> Literal["parallel", "value", "growth", "macro"]:
    """
    路由到合适的Agent执行节点

    根据router节点选择的Agent类型路由

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    agent_type = state.get("selected_agent_type", "parallel")

    if agent_type == "value":
        return "value"
    elif agent_type == "growth":
        return "growth"
    elif agent_type == "macro":
        return "macro"
    else:
        return "parallel"


def route_after_agents(state: AnalysisState) -> Literal["vote", "debate", "parallel"]:
    """
    Agent执行后路由到协作节点

    根据协作模式路由：
    - vote → vote_collaboration
    - debate → debate_collaboration
    - parallel → 直接输出（跳过协作）

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    mode = state.get("mode", "parallel")

    if mode == "vote":
        return "vote"
    elif mode == "debate":
        return "debate"
    else:
        return "parallel"


def route_after_collaboration(state: AnalysisState) -> Literal["output", "end"]:
    """
    协作后路由到输出或结束

    目前直接路由到output，未来可以扩展错误处理等逻辑

    Args:
        state: 当前状态

    Returns:
        下一个节点名称
    """
    # 检查是否有错误
    if state.get("error"):
        return "output"

    # 正常流程
    return "output"
