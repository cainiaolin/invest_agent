"""Nodes模块初始化"""
from app.graph.nodes.router import router_node
from app.graph.nodes.agents import (
    parallel_agents_node,
    value_agent_node,
    growth_agent_node,
    macro_agent_node,
)
from app.graph.nodes.collaboration import vote_collaboration_node, debate_collaboration_node
from app.graph.nodes.output import output_node

__all__ = [
    "router_node",
    "parallel_agents_node",
    "value_agent_node",
    "growth_agent_node",
    "macro_agent_node",
    "vote_collaboration_node",
    "debate_collaboration_node",
    "output_node",
]
