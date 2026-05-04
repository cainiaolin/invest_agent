"""BaseAgent 抽象类定义"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.state import AnalysisState


class BaseAgent(ABC):
    """
    投资分析Agent基类

    所有具体的Agent实现必须继承此类并实现所有抽象方法
    """

    def __init__(self, tushare_service):
        """
        初始化Agent

        Args:
            tushare_service: Tushare数据服务实例
        """
        self.tushare = tushare_service

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent名称

        Returns:
            str: Agent的显示名称
        """
        pass

    @property
    @abstractmethod
    def style(self) -> str:
        """
        投资风格描述

        Returns:
            str: 投资风格的简短描述
        """
        pass

    @abstractmethod
    async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        """
        分析股票数据

        Args:
            state: 分析状态，包含股票代码、模式等信息

        Returns:
            dict: 分析结果，包含:
                - agent_name (str): Agent名称
                - action (str): 决策建议 (buy/sell/hold)
                - confidence (float): 置信度 (0-1)
                - reasoning (str): 决策理由
                - key_metrics (dict): 关键指标
        """
        pass

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            str: 投票结果 (buy/sell/hold)
        """
        return analysis.get("action", "hold")

    async def debate(self, message: dict) -> dict:
        """
        参与辩论讨论

        Args:
            message: 辩论消息，包含其他Agent的观点

        Returns:
            dict: 该Agent的观点回应
        """
        return {
            "agent_name": self.name,
            "content": f"{self.name}支持当前决策。",
            "round": message.get("round", 0)
        }
