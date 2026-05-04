"""
回测引擎 - 核心回测逻辑
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import logging

from .portfolio import Portfolio, Trade
from .metrics import MetricsCalculator, PerformanceMetrics
from .report import generate_report
from app.core.tushare_client import TushareClient

logger = logging.getLogger(__name__)


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        initial_cash: float = 1000000.0,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.001,
        benchmark: Optional[str] = "000300.SH"  # 沪深300
    ):
        self.portfolio = Portfolio(
            initial_cash=initial_cash,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate
        )
        self.benchmark = benchmark
        self.metrics_calculator = MetricsCalculator()

        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None

        self.historical_data: Dict[str, List[Dict]] = {}
        self.benchmark_data: List[Dict] = []

        self.signals: List[Dict] = []

        logger.info(
            f"初始化回测引擎: 初始资金={initial_cash:,.2f}, "
            f"基准={benchmark}"
        )

    def fetch_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, List[Dict]]:
        """
        获取历史数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            历史数据字典 {symbol: [data_dict]}
        """
        ts_client = TushareClient()

        historical_data = {}

        for symbol in symbols:
            try:
                df = ts_client.get_daily_data(
                    ts_code=symbol,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )

                if df is not None and not df.empty:
                    data_list = []
                    for _, row in df.iterrows():
                        data_list.append({
                            'date': row['trade_date'],
                            'open': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close']),
                            'volume': float(row['vol']),
                            'amount': float(row['amount'])
                        })

                    historical_data[symbol] = data_list
                    logger.info(f"获取 {symbol} 数据: {len(data_list)}条")
                else:
                    logger.warning(f"获取 {symbol} 数据失败")

            except Exception as e:
                logger.error(f"获取 {symbol} 数据异常: {e}")

        return historical_data

    def fetch_benchmark_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        获取基准数据

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            基准数据列表
        """
        if not self.benchmark:
            return []

        ts_client = TushareClient()

        try:
            df = ts_client.get_daily_data(
                ts_code=self.benchmark,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )

            if df is not None and not df.empty:
                data_list = []
                for _, row in df.iterrows():
                    data_list.append({
                        'date': row['trade_date'],
                        'close': float(row['close'])
                    })

                logger.info(f"获取基准 {self.benchmark} 数据: {len(data_list)}条")
                return data_list

        except Exception as e:
            logger.error(f"获取基准数据异常: {e}")

        return []

    def prepare_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ):
        """
        准备回测数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
        """
        self.start_date = start_date
        self.end_date = end_date

        logger.info(
            f"开始准备回测数据: {start_date.strftime('%Y-%m-%d')} 至 "
            f"{end_date.strftime('%Y-%m-%d')}"
        )

        # 获取历史数据
        self.historical_data = self.fetch_historical_data(
            symbols, start_date, end_date
        )

        # 获取基准数据
        self.benchmark_data = self.fetch_benchmark_data(start_date, end_date)

        logger.info("回测数据准备完成")

    def add_signal(self, signal: Dict):
        """
        添加交易信号

        Args:
            signal: 交易信号字典
                {
                    'date': datetime,
                    'symbol': str,
                    'action': str,  # 'buy' or 'sell'
                    'shares': int,
                    'price': float (可选)
                }
        """
        self.signals.append(signal)

    def execute_signal(self, signal: Dict, current_prices: Dict[str, float]):
        """
        执行交易信号

        Args:
            signal: 交易信号
            current_prices: 当前价格字典
        """
        symbol = signal['symbol']
        action = signal['action']
        shares = signal['shares']

        if symbol not in current_prices:
            logger.warning(f"股票 {symbol} 无当前价格，跳过交易")
            return

        price = signal.get('price', current_prices[symbol])
        timestamp = signal['date']

        if action == 'buy':
            self.portfolio.buy(symbol, shares, price, timestamp)
        elif action == 'sell':
            self.portfolio.sell(symbol, shares, price, timestamp)

    def run(self, strategy_func: Optional[Callable] = None) -> PerformanceMetrics:
        """
        运行回测

        Args:
            strategy_func: 策略函数 (可选)
                签名: strategy_func(date, current_prices, portfolio) -> List[Dict]

        Returns:
            PerformanceMetrics对象
        """
        if not self.historical_data:
            raise ValueError("历史数据未准备，请先调用 prepare_data()")

        logger.info("开始运行回测...")

        # 构建交易日序列
        all_dates = set()
        for data in self.historical_data.values():
            for item in data:
                all_dates.add(item['date'])

        trading_days = sorted(all_dates)

        # 按日期执行交易
        for trade_date in trading_days:
            current_prices = {}
            current_data = {}

            # 获取当日数据
            for symbol, data in self.historical_data.items():
                for item in data:
                    if item['date'] == trade_date:
                        current_prices[symbol] = item['close']
                        current_data[symbol] = item
                        break

            if not current_prices:
                continue

            # 执行预设信号
            for signal in self.signals:
                if signal['date'] == trade_date:
                    self.execute_signal(signal, current_prices)

            # 执行策略函数
            if strategy_func:
                try:
                    strategy_signals = strategy_func(
                        trade_date, current_data, self.portfolio
                    )
                    for signal in strategy_signals:
                        self.execute_signal(signal, current_prices)
                except Exception as e:
                    logger.error(f"策略函数执行异常: {e}")

            # 更新持仓价格
            self.portfolio.update_prices(current_prices)

            # 创建快照
            self.portfolio.take_snapshot(trade_date)

        # 计算性能指标
        equity_curve = [s.total_value for s in self.portfolio.snapshots]

        benchmark_curve = []
        if self.benchmark_data:
            benchmark_prices = {}
            for item in self.benchmark_data:
                benchmark_prices[item['date']] = item['close']

            # 标准化基准曲线
            first_benchmark_price = None
            for snapshot in self.portfolio.snapshots:
                date = snapshot.timestamp.strftime('%Y%m%d')
                if date in benchmark_prices:
                    if first_benchmark_price is None:
                        first_benchmark_price = benchmark_prices[date]
                    normalized_value = (
                        benchmark_prices[date] / first_benchmark_price
                    ) * self.portfolio.initial_cash
                    benchmark_curve.append(normalized_value)
                else:
                    # 使用前一日价格
                    if benchmark_curve:
                        benchmark_curve.append(benchmark_curve[-1])

        metrics = self.metrics_calculator.calculate(
            equity_curve=equity_curve,
            benchmark_curve=benchmark_curve if benchmark_curve else None,
            trades=self.portfolio.trades
        )

        logger.info(
            f"回测完成: 总收益率={metrics.total_return*100:.2f}%, "
            f"夏普比率={metrics.sharpe_ratio:.3f}"
        )

        return metrics

    def generate_report(
        self,
        strategy_name: str = "未命名策略",
        output_dir: Optional[str] = None
    ):
        """
        生成回测报告

        Args:
            strategy_name: 策略名称
            output_dir: 输出目录（可选）

        Returns:
            BacktestReport对象
        """
        if not self.portfolio.snapshots:
            raise ValueError("回测未运行，无数据可生成报告")

        # 重新计算指标
        equity_curve = [s.total_value for s in self.portfolio.snapshots]

        benchmark_curve = []
        if self.benchmark_data:
            benchmark_prices = {}
            for item in self.benchmark_data:
                benchmark_prices[item['date']] = item['close']

            first_benchmark_price = None
            for snapshot in self.portfolio.snapshots:
                date = snapshot.timestamp.strftime('%Y%m%d')
                if date in benchmark_prices:
                    if first_benchmark_price is None:
                        first_benchmark_price = benchmark_prices[date]
                    normalized_value = (
                        benchmark_prices[date] / first_benchmark_price
                    ) * self.portfolio.initial_cash
                    benchmark_curve.append(normalized_value)
                else:
                    if benchmark_curve:
                        benchmark_curve.append(benchmark_curve[-1])

        metrics = self.metrics_calculator.calculate(
            equity_curve=equity_curve,
            benchmark_curve=benchmark_curve if benchmark_curve else None,
            trades=self.portfolio.trades
        )

        return generate_report(
            portfolio=self.portfolio,
            metrics=metrics,
            start_date=self.start_date,
            end_date=self.end_date,
            strategy_name=strategy_name,
            output_dir=output_dir
        )

    def get_equity_curve(self) -> List[Dict]:
        """获取权益曲线"""
        return [
            {
                'date': snapshot.timestamp.strftime('%Y-%m-%d'),
                'value': snapshot.total_value,
                'return': snapshot.cumulative_return * 100
            }
            for snapshot in self.portfolio.snapshots
        ]
