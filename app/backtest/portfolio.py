"""
投资组合管理 - 处理持仓、交易和资金管理
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    market_value: float = 0.0

    def update_price(self, price: float):
        """更新当前价格"""
        self.current_price = price
        self.market_value = self.shares * price

    def unrealized_pnl(self) -> float:
        """计算未实现盈亏"""
        return (self.current_price - self.avg_cost) * self.shares


@dataclass
class Trade:
    """交易记录"""
    symbol: str
    action: str  # 'buy' or 'sell'
    shares: int
    price: float
    timestamp: datetime
    commission: float = 0.0
    slippage: float = 0.0


@dataclass
class PortfolioSnapshot:
    """组合快照"""
    timestamp: datetime
    cash: float
    total_value: float
    positions: Dict[str, Position]
    daily_return: float = 0.0
    cumulative_return: float = 0.0


class Portfolio:
    """投资组合类"""

    def __init__(
        self,
        initial_cash: float = 1000000.0,
        commission_rate: float = 0.0003,  # 万三佣金
        min_commission: float = 5.0,
        slippage_rate: float = 0.001  # 千一滑点
    ):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.slippage_rate = slippage_rate

        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.snapshots: List[PortfolioSnapshot] = []
        self.total_value = initial_cash

        logger.info(f"初始化投资组合: 初始资金={initial_cash:,.2f}")

    def calculate_commission(self, amount: float) -> float:
        """计算佣金"""
        commission = amount * self.commission_rate
        return max(commission, self.min_commission)

    def calculate_slippage(self, price: float, action: str) -> float:
        """计算滑点"""
        slippage = price * self.slippage_rate
        # 买入时价格偏高，卖出时价格偏低
        return slippage if action == 'buy' else -slippage

    def buy(
        self,
        symbol: str,
        shares: int,
        price: float,
        timestamp: datetime
    ) -> Optional[Trade]:
        """买入股票"""
        # 计算实际成交价格（含滑点）
        actual_price = price + self.calculate_slippage(price, 'buy')
        trade_value = shares * actual_price
        commission = self.calculate_commission(trade_value)
        total_cost = trade_value + commission

        # 检查资金是否充足
        if total_cost > self.cash:
            logger.warning(
                f"资金不足买入 {symbol}: 需要={total_cost:,.2f}, "
                f"可用={self.cash:,.2f}"
            )
            return None

        # 扣除资金
        self.cash -= total_cost

        # 更新持仓
        if symbol not in self.positions:
            self.positions[symbol] = Position(
                symbol=symbol,
                shares=0,
                avg_cost=0.0
            )

        # 计算新的平均成本
        pos = self.positions[symbol]
        total_shares = pos.shares + shares
        pos.avg_cost = (
            (pos.avg_cost * pos.shares + actual_price * shares) / total_shares
        )
        pos.shares = total_shares
        pos.update_price(actual_price)

        # 记录交易
        trade = Trade(
            symbol=symbol,
            action='buy',
            shares=shares,
            price=actual_price,
            timestamp=timestamp,
            commission=commission,
            slippage=actual_price - price
        )
        self.trades.append(trade)

        logger.info(
            f"买入 {symbol}: {shares}股 @{actual_price:.2f}, "
            f"佣金={commission:.2f}, 剩余资金={self.cash:,.2f}"
        )

        return trade

    def sell(
        self,
        symbol: str,
        shares: int,
        price: float,
        timestamp: datetime
    ) -> Optional[Trade]:
        """卖出股票"""
        if symbol not in self.positions:
            logger.warning(f"持仓中没有 {symbol}")
            return None

        pos = self.positions[symbol]
        if shares > pos.shares:
            logger.warning(
                f"持仓不足卖出 {symbol}: 持有={pos.shares}, 卖出={shares}"
            )
            return None

        # 计算实际成交价格（含滑点）
        actual_price = price + self.calculate_slippage(price, 'sell')
        trade_value = shares * actual_price
        commission = self.calculate_commission(trade_value)
        total_proceeds = trade_value - commission

        # 增加资金
        self.cash += total_proceeds

        # 更新持仓
        pos.shares -= shares
        if pos.shares == 0:
            del self.positions[symbol]

        # 记录交易
        trade = Trade(
            symbol=symbol,
            action='sell',
            shares=shares,
            price=actual_price,
            timestamp=timestamp,
            commission=commission,
            slippage=actual_price - price
        )
        self.trades.append(trade)

        logger.info(
            f"卖出 {symbol}: {shares}股 @{actual_price:.2f}, "
            f"佣金={commission:.2f}, 剩余资金={self.cash:,.2f}"
        )

        return trade

    def update_prices(self, prices: Dict[str, float]):
        """更新所有持仓的当前价格"""
        for symbol, pos in self.positions.items():
            if symbol in prices:
                pos.update_price(prices[symbol])

    def calculate_total_value(self) -> float:
        """计算总资产"""
        market_value = sum(
            pos.market_value for pos in self.positions.values()
        )
        self.total_value = self.cash + market_value
        return self.total_value

    def take_snapshot(self, timestamp: datetime) -> PortfolioSnapshot:
        """创建组合快照"""
        total_value = self.calculate_total_value()

        # 计算收益率
        daily_return = 0.0
        if self.snapshots:
            prev_value = self.snapshots[-1].total_value
            daily_return = (total_value - prev_value) / prev_value

        cumulative_return = (total_value - self.initial_cash) / self.initial_cash

        snapshot = PortfolioSnapshot(
            timestamp=timestamp,
            cash=self.cash,
            total_value=total_value,
            positions=dict(self.positions),
            daily_return=daily_return,
            cumulative_return=cumulative_return
        )

        self.snapshots.append(snapshot)
        return snapshot

    def get_position_count(self) -> int:
        """获取持仓数量"""
        return len(self.positions)

    def get_market_value(self) -> float:
        """获取市值"""
        return sum(pos.market_value for pos in self.positions.values())

    def get_cash_ratio(self) -> float:
        """获取现金比例"""
        return self.cash / self.total_value if self.total_value > 0 else 0.0

    def get_position_list(self) -> List[Position]:
        """获取持仓列表"""
        return list(self.positions.values())

    def get_trade_count(self) -> int:
        """获取交易次数"""
        return len(self.trades)
