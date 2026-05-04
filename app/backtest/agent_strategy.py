"""Agent回测策略 - 将Agent决策集成到回测引擎"""

import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime

from app.services.tushare_service import TushareService
from app.agents import BaseAgent
from app.agents import BuffetAgent, GrahamAgent, FisherAgent, LynchAgent, SorosAgent, DalioAgent

logger = logging.getLogger(__name__)

# Agent映射
AGENT_MAP = {
    "buffet": BuffetAgent,
    "graham": GrahamAgent,
    "fisher": FisherAgent,
    "lynch": LynchAgent,
    "soros": SorosAgent,
    "dalio": DalioAgent,
}


class AgentBacktestStrategy:
    """Agent回测策略类"""

    def __init__(self, agent_name: str, tushare_service: TushareService):
        """
        初始化Agent策略

        Args:
            agent_name: Agent名称
            tushare_service: Tushare数据服务
        """
        agent_class = AGENT_MAP.get(agent_name.lower())
        if not agent_class:
            raise ValueError(f"不支持的Agent: {agent_name}")

        self.agent = agent_class(tushare_service)
        self.agent_name = agent_name
        self.last_action = None  # 记录上次动作，避免频繁交易
        self.last_action_date = None

    async def generate_signal(
        self,
        stock_code: str,
        current_date: datetime,
        current_price: float
    ) -> Optional[Dict]:
        """
        生成交易信号

        Args:
            stock_code: 股票代码
            current_date: 当前日期
            current_price: 当前价格

        Returns:
            交易信号字典 或 None
        """
        try:
            # 调用Agent分析
            from app.core.state import AnalysisState

            state = AnalysisState(
                stock_code=stock_code,
                mode="parallel",
                user_request="回测决策",
                agent_analyses=[],
                debate_round=0,
                debate_history=[],
                final_decision=None,
                error=None
            )

            analysis = await self.agent.analyze(state)
            action = analysis.get("action", "hold")
            reason = analysis.get("reasoning", "")
            confidence = analysis.get("confidence", 0.0)

            # 避免频繁交易：只有当置信度高于阈值或动作改变时才交易
            if action == "hold":
                return None

            # 如果上次动作相同且时间间隔短，跳过
            if (self.last_action == action and
                self.last_action_date and
                (current_date - self.last_action_date).days < 30):
                return None

            # 更新状态
            self.last_action = action
            self.last_action_date = current_date

            # 计算交易数量（简化：全仓买入/卖出）
            signal = {
                'date': current_date,
                'symbol': stock_code,
                'action': action,
                'confidence': confidence,
                'reason': reason,
                'price': current_price
            }

            logger.info(
                f"{self.agent_name} 生成信号: {action} {stock_code} "
                f"@{current_price:.2f} (置信度: {confidence:.2%})"
            )

            return signal

        except Exception as e:
            logger.warning(f"Agent分析失败: {e}")
            return None


def create_agent_strategy_function(
    stock_code: str,
    agent_strategy: AgentBacktestStrategy,
    historical_data: Dict[str, List[Dict]]
) -> Callable:
    """
    创建Agent策略函数供回测引擎使用

    Args:
        stock_code: 股票代码
        agent_strategy: Agent策略实例
        historical_data: 历史数据字典

    Returns:
        策略函数
    """
    async def strategy_func(
        trade_date: datetime,
        current_data: Dict,
        portfolio
    ) -> List[Dict]:
        """
        策略函数

        Args:
            trade_date: 交易日期
            current_data: 当前数据
            portfolio: 投资组合

        Returns:
            信号列表
        """
        if stock_code not in current_data:
            return []

        current_price = current_data[stock_code]['close']

        # 每月重新评估一次
        # 根据日期判断是否需要重新评估（例如每月1号）
        if trade_date.day != 1:
            return []

        signal = await agent_strategy.generate_signal(
            stock_code, trade_date, current_price
        )

        if signal:
            # 计算交易数量
            shares = 0
            if signal['action'] == 'buy':
                # 使用可用现金的95%买入
                if portfolio.cash > 0:
                    shares = int((portfolio.cash * 0.95) / signal['price'])
            elif signal['action'] == 'sell':
                # 全部卖出
                if stock_code in portfolio.positions:
                    shares = portfolio.positions[stock_code].shares

            if shares > 0:
                return [{
                    'date': signal['date'],
                    'symbol': signal['symbol'],
                    'action': signal['action'],
                    'shares': shares,
                    'price': signal['price']
                }]

        return []

    return strategy_func
