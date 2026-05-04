"""
回测模块 - 提供完整的回测引擎功能
"""
from .engine import BacktestEngine
from .portfolio import Portfolio
from .metrics import calculate_metrics, MetricsCalculator
from .report import generate_report

__all__ = [
    'BacktestEngine',
    'Portfolio',
    'calculate_metrics',
    'MetricsCalculator',
    'generate_report'
]
