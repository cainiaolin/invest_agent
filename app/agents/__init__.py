"""Agent模块 - 规则引擎和AI增强Agent"""

from app.agents.base import BaseAgent
from app.agents.value.graham_agent import GrahamAgent
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.macro.dalio_agent import DalioAgent

# 规则引擎Agent映射
RULE_AGENTS = {
    "graham": GrahamAgent,
    "buffet": BuffetAgent,
    "fisher": FisherAgent,
    "lynch": LynchAgent,
    "soros": SorosAgent,
    "dalio": DalioAgent,
}

# AI增强Agent映射（延迟导入避免循环依赖）
_AI_AGENTS = None


def get_ai_agents():
    """延迟加载AI Agent"""
    global _AI_AGENTS
    if _AI_AGENTS is None:
        from app.agents.value.llm_graham_agent import LLMGrahamAgent

        _AI_AGENTS = {
            "graham": LLMGrahamAgent,
        }
    return _AI_AGENTS


def get_agent(agent_name: str, mode: str = "rule", **kwargs):
    """
    获取Agent实例

    Args:
        agent_name: Agent名称
        mode: "rule" | "ai" | "hybrid"
        **kwargs: Agent初始化参数

    Returns:
        Agent实例

    Raises:
        ValueError: 未知的Agent
    """
    if mode == "ai":
        ai_agents = get_ai_agents()
        agent_class = ai_agents.get(agent_name)
        if agent_class:
            # 添加master_name参数
            kwargs["master_name"] = agent_name
            return agent_class(**kwargs)

    # 默认使用规则引擎
    agent_class = RULE_AGENTS.get(agent_name)
    if agent_class:
        return agent_class(**kwargs)

    raise ValueError(f"Unknown agent: {agent_name}")


__all__ = [
    "BaseAgent",
    "GrahamAgent",
    "BuffetAgent",
    "FisherAgent",
    "LynchAgent",
    "SorosAgent",
    "DalioAgent",
    "RULE_AGENTS",
    "get_ai_agents",
    "get_agent",
]
