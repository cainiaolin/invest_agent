"""Agents模块初始化"""
from app.agents.base import BaseAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.dalio_agent import DalioAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.value.graham_agent import GrahamAgent

__all__ = [
    "BaseAgent",
    "FisherAgent",
    "LynchAgent",
    "DalioAgent",
    "SorosAgent",
    "BuffetAgent",
    "GrahamAgent",
]
