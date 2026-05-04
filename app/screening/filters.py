"""
股票过滤器 - 实现各种选股过滤条件
"""
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class StockFilter:
    """股票过滤器基类"""

    def __init__(self, name: str = "基础过滤器"):
        self.name = name

    def filter(self, stocks: List[Dict]) -> List[Dict]:
        """
        过滤股票列表

        Args:
            stocks: 股票列表

        Returns:
            过滤后的股票列表
        """
        raise NotImplementedError("子类必须实现filter方法")


class BasicFilter(StockFilter):
    """基础过滤器 - 基本股票筛选条件"""

    def __init__(
        self,
        exclude_st: bool = True,
        exclude_suspended: bool = True,
        exclude_new_days: int = 180,  # 排除上市N天内的股票
        min_market_cap: Optional[float] = None,  # 最小市值（亿元）
        max_market_cap: Optional[float] = None,  # 最大市值（亿元）
        industries: Optional[List[str]] = None  # 指定行业列表
    ):
        super().__init__("基础过滤器")
        self.exclude_st = exclude_st
        self.exclude_suspended = exclude_suspended
        self.exclude_new_days = exclude_new_days
        self.min_market_cap = min_market_cap
        self.max_market_cap = max_market_cap
        self.industries = industries

    def filter(self, stocks: List[Dict]) -> List[Dict]:
        """应用基础过滤条件"""
        filtered = []

        for stock in stocks:
            # 排除ST股票
            if self.exclude_st and self._is_st_stock(stock):
                continue

            # 排除停牌股票
            if self.exclude_suspended and stock.get('is_suspended', False):
                continue

            # 排除新股
            if self.exclude_new_days and self._is_new_stock(stock):
                continue

            # 市值过滤
            market_cap = stock.get('market_cap', 0)
            if self.min_market_cap and market_cap < self.min_market_cap:
                continue
            if self.max_market_cap and market_cap > self.max_market_cap:
                continue

            # 行业过滤
            if self.industries:
                industry = stock.get('industry', '')
                if industry not in self.industries:
                    continue

            filtered.append(stock)

        logger.info(
            f"基础过滤: {len(stocks)} -> {len(filtered)} "
            f"(过滤掉{len(stocks) - len(filtered)}只)"
        )

        return filtered

    def _is_st_stock(self, stock: Dict) -> bool:
        """判断是否为ST股票"""
        name = stock.get('name', '')
        return 'ST' in name or 'st' in name

    def _is_new_stock(self, stock: Dict) -> bool:
        """判断是否为新股"""
        list_date = stock.get('list_date')
        if not list_date:
            return False

        try:
            list_datetime = datetime.strptime(list_date, '%Y%m%d')
            days_since_list = (datetime.now() - list_datetime).days
            return days_since_list < self.exclude_new_days
        except:
            return False


class FundamentalFilter(StockFilter):
    """基本面过滤器 - 基于财务指标过滤"""

    def __init__(
        self,
        min_pe: Optional[float] = None,  # 最小市盈率
        max_pe: Optional[float] = None,  # 最大市盈率
        min_pb: Optional[float] = None,  # 最小市净率
        max_pb: Optional[float] = None,  # 最大市净率
        min_roe: Optional[float] = None,  # 最小ROE
        max_debt_ratio: Optional[float] = None,  # 最大资产负债率
        min_revenue_growth: Optional[float] = None,  # 最小营收增长率
        min_profit_growth: Optional[float] = None  # 最小利润增长率
    ):
        super().__init__("基本面过滤器")
        self.min_pe = min_pe
        self.max_pe = max_pe
        self.min_pb = min_pb
        self.max_pb = max_pb
        self.min_roe = min_roe
        self.max_debt_ratio = max_debt_ratio
        self.min_revenue_growth = min_revenue_growth
        self.min_profit_growth = min_profit_growth

    def filter(self, stocks: List[Dict]) -> List[Dict]:
        """应用基本面过滤条件"""
        filtered = []

        for stock in stocks:
            # PE过滤
            pe = stock.get('pe', 0)
            if self.min_pe and pe < self.min_pe:
                continue
            if self.max_pe and pe > self.max_pe:
                continue

            # PB过滤
            pb = stock.get('pb', 0)
            if self.min_pb and pb < self.min_pb:
                continue
            if self.max_pb and pb > self.max_pb:
                continue

            # ROE过滤
            roe = stock.get('roe', 0)
            if self.min_roe and roe < self.min_roe:
                continue

            # 资产负债率过滤
            debt_ratio = stock.get('debt_ratio', 0)
            if self.max_debt_ratio and debt_ratio > self.max_debt_ratio:
                continue

            # 营收增长率过滤
            revenue_growth = stock.get('revenue_growth', 0)
            if self.min_revenue_growth and revenue_growth < self.min_revenue_growth:
                continue

            # 利润增长率过滤
            profit_growth = stock.get('profit_growth', 0)
            if self.min_profit_growth and profit_growth < self.min_profit_growth:
                continue

            filtered.append(stock)

        logger.info(
            f"基本面过滤: {len(stocks)} -> {len(filtered)} "
            f"(过滤掉{len(stocks) - len(filtered)}只)"
        )

        return filtered


class TechnicalFilter(StockFilter):
    """技术面过滤器 - 基于技术指标过滤"""

    def __init__(
        self,
        min_volume_ratio: Optional[float] = None,  # 最小量比
        max_price_change: Optional[float] = None,  # 最大涨跌幅
        min_rsi: Optional[float] = None,  # 最小RSI
        max_rsi: Optional[float] = None,  # 最大RSI
        trend: Optional[str] = None,  # 趋势: 'up', 'down', 'neutral'
        ma_cross: Optional[str] = None  # 均线交叉: 'golden', 'death'
    ):
        super().__init__("技术面过滤器")
        self.min_volume_ratio = min_volume_ratio
        self.max_price_change = max_price_change
        self.min_rsi = min_rsi
        self.max_rsi = max_rsi
        self.trend = trend
        self.ma_cross = ma_cross

    def filter(self, stocks: List[Dict]) -> List[Dict]:
        """应用技术面过滤条件"""
        filtered = []

        for stock in stocks:
            # 量比过滤
            volume_ratio = stock.get('volume_ratio', 0)
            if self.min_volume_ratio and volume_ratio < self.min_volume_ratio:
                continue

            # 涨跌幅过滤
            price_change = stock.get('price_change_pct', 0)
            if self.max_price_change and abs(price_change) > self.max_price_change:
                continue

            # RSI过滤
            rsi = stock.get('rsi', 50)
            if self.min_rsi and rsi < self.min_rsi:
                continue
            if self.max_rsi and rsi > self.max_rsi:
                continue

            # 趋势过滤
            if self.trend:
                stock_trend = stock.get('trend', 'neutral')
                if stock_trend != self.trend:
                    continue

            # 均线交叉过滤
            if self.ma_cross:
                ma_signal = stock.get('ma_signal', '')
                if ma_signal != self.ma_cross:
                    continue

            filtered.append(stock)

        logger.info(
            f"技术面过滤: {len(stocks)} -> {len(filtered)} "
            f"(过滤掉{len(stocks) - len(filtered)}只)"
        )

        return filtered


class CompositeFilter(StockFilter):
    """组合过滤器 - 组合多个过滤器"""

    def __init__(self, filters: List[StockFilter]):
        super().__init__("组合过滤器")
        self.filters = filters

    def filter(self, stocks: List[Dict]) -> List[Dict]:
        """依次应用所有过滤器"""
        filtered = stocks

        for filter_obj in self.filters:
            filtered = filter_obj.filter(filtered)

        logger.info(
            f"组合过滤: 初始{len(stocks)}只 -> 最终{len(filtered)}只"
        )

        return filtered
