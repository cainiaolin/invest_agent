"""Tushare客户端 - 为回测引擎提供兼容接口"""

from typing import Optional
import pandas as pd
from app.services.tushare_service import TushareService


class TushareClient:
    """Tushare客户端类 - 回测引擎兼容接口"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化Tushare客户端

        Args:
            token: Tushare API Token (可选，默认从环境变量读取)
        """
        from app.core.config import settings
        self.token = token or settings.tushare_token
        self.service = TushareService(self.token)

    def get_daily_data(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        retry: int = 3
    ) -> Optional[pd.DataFrame]:
        """
        获取日线数据

        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            retry: 重试次数

        Returns:
            DataFrame or None
        """
        try:
            import asyncio

            # 使用同步方式调用异步方法
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 获取日线数据
            df = self.service.api.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )

            loop.close()

            return df if df is not None and not df.empty else None

        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return None

    def get_stock_basic(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        获取股票基本信息

        Args:
            **kwargs: 参数

        Returns:
            DataFrame or None
        """
        try:
            df = self.service.api.stock_basic(**kwargs)
            return df if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None

    def get_pro_bar(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """
        获取K线数据

        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数

        Returns:
            DataFrame or None
        """
        return self.get_daily_data(ts_code, start_date, end_date)
