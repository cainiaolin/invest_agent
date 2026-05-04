"""
性能指标计算 - 计算夏普比率、最大回撤等关键指标
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    # 收益指标
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    daily_return_mean: float  # 日均收益率

    # 风险指标
    volatility: float  # 波动率
    max_drawdown: float  # 最大回撤
    max_drawdown_duration: int  # 最大回撤持续天数

    # 风险调整收益
    sharpe_ratio: float  # 夏普比率
    sortino_ratio: float  # 索提诺比率
    calmar_ratio: float  # 卡玛比率

    # 交易指标
    total_trades: int  # 总交易次数
    win_rate: float  # 胜率
    profit_factor: float  # 盈亏比

    # 基准对比
    benchmark_return: float  # 基准收益率
    excess_return: float  # 超额收益率
    information_ratio: float  # 信息比率

    # 统计指标
    skewness: float  # 偏度
    kurtosis: float  # 峰度
    var_95: float  # 95% VaR
    cvar_95: float  # 95% CVaR


class MetricsCalculator:
    """性能指标计算器"""

    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
        self.trading_days_per_year = 252

    def calculate(
        self,
        equity_curve: List[float],
        benchmark_curve: Optional[List[float]] = None,
        trades: Optional[List] = None
    ) -> PerformanceMetrics:
        """计算所有性能指标"""

        # 计算收益率序列
        returns = self._calculate_returns(equity_curve)

        # 基本收益指标
        total_return = (equity_curve[-1] / equity_curve[0]) - 1
        daily_return_mean = np.mean(returns)
        annual_return = (1 + daily_return_mean) ** self.trading_days_per_year - 1

        # 风险指标
        volatility = np.std(returns) * np.sqrt(self.trading_days_per_year)

        # 最大回撤
        max_drawdown, max_dd_duration = self._calculate_max_drawdown(
            equity_curve
        )

        # 风险调整收益
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        sortino_ratio = self._calculate_sortino_ratio(returns)
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # 基准对比
        benchmark_return = 0.0
        excess_return = 0.0
        information_ratio = 0.0

        if benchmark_curve:
            benchmark_returns = self._calculate_returns(benchmark_curve)
            benchmark_return = (benchmark_curve[-1] / benchmark_curve[0]) - 1
            excess_return = total_return - benchmark_return
            information_ratio = self._calculate_information_ratio(
                returns, benchmark_returns
            )

        # 交易指标
        total_trades = len(trades) if trades else 0
        win_rate = 0.0
        profit_factor = 0.0

        if trades:
            win_rate, profit_factor = self._calculate_trade_metrics(trades)

        # 统计指标
        skewness = float(self._calculate_skewness(returns))
        kurtosis = float(self._calculate_kurtosis(returns))
        var_95 = np.percentile(returns, 5)
        cvar_95 = np.mean(returns[returns <= var_95])

        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            daily_return_mean=daily_return_mean,
            volatility=volatility,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            information_ratio=information_ratio,
            skewness=skewness,
            kurtosis=kurtosis,
            var_95=var_95,
            cvar_95=cvar_95
        )

    def _calculate_returns(self, equity_curve: List[float]) -> List[float]:
        """计算收益率序列"""
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        return returns

    def _calculate_max_drawdown(
        self,
        equity_curve: List[float]
    ) -> tuple[float, int]:
        """计算最大回撤和持续时间"""
        if not equity_curve:
            return 0.0, 0

        peak = equity_curve[0]
        max_drawdown = 0.0
        max_dd_duration = 0
        current_dd_duration = 0

        for value in equity_curve:
            if value > peak:
                peak = value
                current_dd_duration = 0
            else:
                current_dd_duration += 1

            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_dd_duration = current_dd_duration

        return max_drawdown, max_dd_duration

    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """计算夏普比率"""
        if not returns:
            return 0.0

        daily_rf_rate = self.risk_free_rate / self.trading_days_per_year
        excess_returns = [r - daily_rf_rate for r in returns]

        if not excess_returns:
            return 0.0

        mean_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)

        if std_excess_return == 0:
            return 0.0

        sharpe = (mean_excess_return * self.trading_days_per_year) / (
            std_excess_return * np.sqrt(self.trading_days_per_year)
        )
        return sharpe

    def _calculate_sortino_ratio(self, returns: List[float]) -> float:
        """计算索提诺比率"""
        if not returns:
            return 0.0

        daily_rf_rate = self.risk_free_rate / self.trading_days_per_year
        excess_returns = [r - daily_rf_rate for r in returns]

        mean_excess_return = np.mean(excess_returns)

        # 计算下行偏差
        downside_returns = [r for r in excess_returns if r < 0]
        if not downside_returns:
            return 0.0

        downside_deviation = np.std(downside_returns)

        if downside_deviation == 0:
            return 0.0

        sortino = (mean_excess_return * self.trading_days_per_year) / (
            downside_deviation * np.sqrt(self.trading_days_per_year)
        )
        return sortino

    def _calculate_information_ratio(
        self,
        returns: List[float],
        benchmark_returns: List[float]
    ) -> float:
        """计算信息比率"""
        if len(returns) != len(benchmark_returns):
            return 0.0

        excess_returns = [
            r - b for r, b in zip(returns, benchmark_returns)
        ]

        if not excess_returns:
            return 0.0

        mean_excess = np.mean(excess_returns)
        tracking_error = np.std(excess_returns)

        if tracking_error == 0:
            return 0.0

        information_ratio = mean_excess / tracking_error
        return information_ratio * np.sqrt(self.trading_days_per_year)

    def _calculate_trade_metrics(
        self,
        trades: List
    ) -> tuple[float, float]:
        """计算交易指标"""
        # 简化版本：按买卖配对计算盈亏
        buy_trades = {}
        total_profit = 0.0
        total_loss = 0.0
        winning_trades = 0
        losing_trades = 0

        for trade in trades:
            if trade.action == 'buy':
                if trade.symbol not in buy_trades:
                    buy_trades[trade.symbol] = []
                buy_trades[trade.symbol].append(trade)
            elif trade.action == 'sell':
                if trade.symbol in buy_trades and buy_trades[trade.symbol]:
                    buy_trade = buy_trades[trade.symbol].pop(0)
                    pnl = (trade.price - buy_trade.price) * trade.shares
                    pnl -= (trade.commission + buy_trade.commission)

                    if pnl > 0:
                        total_profit += pnl
                        winning_trades += 1
                    else:
                        total_loss += abs(pnl)
                        losing_trades += 1

        # 计算胜率
        total_completed_trades = winning_trades + losing_trades
        win_rate = (
            winning_trades / total_completed_trades
            if total_completed_trades > 0 else 0.0
        )

        # 计算盈亏比
        profit_factor = (
            total_profit / total_loss if total_loss > 0 else 0.0
        )

        return win_rate, profit_factor

    def _calculate_skewness(self, returns: List[float]) -> float:
        """计算偏度"""
        if not returns or len(returns) < 3:
            return 0.0

        mean = np.mean(returns)
        std = np.std(returns)

        if std == 0:
            return 0.0

        skew = np.mean([((r - mean) / std) ** 3 for r in returns])
        return skew

    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """计算峰度"""
        if not returns or len(returns) < 4:
            return 0.0

        mean = np.mean(returns)
        std = np.std(returns)

        if std == 0:
            return 0.0

        kurt = np.mean([((r - mean) / std) ** 4 for r in returns]) - 3
        return kurt


def calculate_metrics(
    equity_curve: List[float],
    benchmark_curve: Optional[List[float]] = None,
    trades: Optional[List] = None,
    risk_free_rate: float = 0.03
) -> PerformanceMetrics:
    """
    便捷函数：计算性能指标

    Args:
        equity_curve: 权益曲线
        benchmark_curve: 基准曲线（可选）
        trades: 交易列表（可选）
        risk_free_rate: 无风险利率

    Returns:
        PerformanceMetrics对象
    """
    calculator = MetricsCalculator(risk_free_rate=risk_free_rate)
    return calculator.calculate(equity_curve, benchmark_curve, trades)
