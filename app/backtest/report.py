"""
回测报告生成 - 生成详细的回测报告
"""
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
import logging

from .portfolio import Portfolio, PortfolioSnapshot
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class BacktestReport:
    """回测报告类"""

    def __init__(
        self,
        portfolio: Portfolio,
        metrics: PerformanceMetrics,
        start_date: datetime,
        end_date: datetime,
        strategy_name: str = "未命名策略"
    ):
        self.portfolio = portfolio
        self.metrics = metrics
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_name = strategy_name

    def generate_text_report(self) -> str:
        """生成文本报告"""
        lines = [
            "=" * 80,
            f"回测报告: {self.strategy_name}",
            "=" * 80,
            "",
            f"回测期间: {self.start_date.strftime('%Y-%m-%d')} 至 "
            f"{self.end_date.strftime('%Y-%m-%d')}",
            f"初始资金: ¥{self.portfolio.initial_cash:,.2f}",
            f"最终资金: ¥{self.portfolio.total_value:,.2f}",
            "",
            "-" * 80,
            "收益指标",
            "-" * 80,
            f"总收益率: {self.metrics.total_return*100:.2f}%",
            f"年化收益率: {self.metrics.annual_return*100:.2f}%",
            f"日均收益率: {self.metrics.daily_return_mean*100:.4f}%",
            "",
            "-" * 80,
            "风险指标",
            "-" * 80,
            f"波动率: {self.metrics.volatility*100:.2f}%",
            f"最大回撤: {self.metrics.max_drawdown*100:.2f}%",
            f"最大回撤持续天数: {self.metrics.max_drawdown_duration}天",
            "",
            "-" * 80,
            "风险调整收益",
            "-" * 80,
            f"夏普比率: {self.metrics.sharpe_ratio:.3f}",
            f"索提诺比率: {self.metrics.sortino_ratio:.3f}",
            f"卡玛比率: {self.metrics.calmar_ratio:.3f}",
            "",
            "-" * 80,
            "交易统计",
            "-" * 80,
            f"总交易次数: {self.metrics.total_trades}",
            f"胜率: {self.metrics.win_rate*100:.2f}%",
            f"盈亏比: {self.metrics.profit_factor:.2f}",
            "",
        ]

        if self.metrics.benchmark_return != 0:
            lines.extend([
                "-" * 80,
                "基准对比",
                "-" * 80,
                f"基准收益率: {self.metrics.benchmark_return*100:.2f}%",
                f"超额收益率: {self.metrics.excess_return*100:.2f}%",
                f"信息比率: {self.metrics.information_ratio:.3f}",
                "",
            ])

        lines.extend([
            "-" * 80,
            "统计指标",
            "-" * 80,
            f"偏度: {self.metrics.skewness:.3f}",
            f"峰度: {self.metrics.kurtosis:.3f}",
            f"95% VaR: {self.metrics.var_95*100:.2f}%",
            f"95% CVaR: {self.metrics.cvar_95*100:.2f}%",
            "",
            "=" * 80,
        ])

        return "\n".join(lines)

    def generate_json_report(self) -> Dict:
        """生成JSON报告"""
        return {
            "strategy_name": self.strategy_name,
            "backtest_period": {
                "start_date": self.start_date.isoformat(),
                "end_date": self.end_date.isoformat()
            },
            "initial_capital": self.portfolio.initial_cash,
            "final_capital": self.portfolio.total_value,
            "total_return": self.metrics.total_return,
            "annual_return": self.metrics.annual_return,
            "volatility": self.metrics.volatility,
            "max_drawdown": self.metrics.max_drawdown,
            "sharpe_ratio": self.metrics.sharpe_ratio,
            "total_trades": self.metrics.total_trades,
            "win_rate": self.metrics.win_rate,
            "equity_curve": [
                {
                    "date": snapshot.timestamp.isoformat(),
                    "value": snapshot.total_value,
                    "return": snapshot.cumulative_return
                }
                for snapshot in self.portfolio.snapshots
            ]
        }

    def save_report(self, output_dir: Path, format: str = "both"):
        """
        保存报告到文件

        Args:
            output_dir: 输出目录
            format: 报告格式 ('text', 'json', 'both')
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format in ["text", "both"]:
            text_file = output_dir / f"{self.strategy_name}_{timestamp}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_text_report())
            logger.info(f"文本报告已保存: {text_file}")

        if format in ["json", "both"]:
            json_file = output_dir / f"{self.strategy_name}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.generate_json_report(), f, indent=2, ensure_ascii=False)
            logger.info(f"JSON报告已保存: {json_file}")

    def get_equity_curve_data(self) -> List[Dict]:
        """获取权益曲线数据（用于图表）"""
        return [
            {
                "date": snapshot.timestamp.strftime("%Y-%m-%d"),
                "value": snapshot.total_value,
                "return": snapshot.cumulative_return * 100,
                "cash": snapshot.cash
            }
            for snapshot in self.portfolio.snapshots
        ]

    def get_position_summary(self) -> List[Dict]:
        """获取持仓摘要"""
        positions = []
        for symbol, pos in self.portfolio.positions.items():
            positions.append({
                "symbol": symbol,
                "shares": pos.shares,
                "avg_cost": pos.avg_cost,
                "current_price": pos.current_price,
                "market_value": pos.market_value,
                "unrealized_pnl": pos.unrealized_pnl(),
                "return": ((pos.current_price - pos.avg_cost) / pos.avg_cost) * 100
            })
        return positions


def generate_report(
    portfolio: Portfolio,
    metrics: PerformanceMetrics,
    start_date: datetime,
    end_date: datetime,
    strategy_name: str = "未命名策略",
    output_dir: Optional[Path] = None,
    format: str = "both"
) -> BacktestReport:
    """
    便捷函数：生成回测报告

    Args:
        portfolio: 投资组合对象
        metrics: 性能指标对象
        start_date: 回测开始日期
        end_date: 回测结束日期
        strategy_name: 策略名称
        output_dir: 输出目录（可选）
        format: 报告格式 ('text', 'json', 'both')

    Returns:
        BacktestReport对象
    """
    report = BacktestReport(
        portfolio=portfolio,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        strategy_name=strategy_name
    )

    if output_dir:
        report.save_report(output_dir, format)

    return report
