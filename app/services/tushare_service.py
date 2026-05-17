"""Tushare数据服务"""

import asyncio
from typing import Optional, Dict, Any, List
import pandas as pd
from tushare import pro_api
import logging
from datetime import datetime

from app.services.exceptions import (
    TushareAPIError,
    TushareDataNotFoundError,
    TusharePermissionError,
)

logger = logging.getLogger(__name__)


class TushareService:
    """
    Tushare数据服务封装类

    特点：
    - 严格的错误处理和数据验证
    - 明确区分API错误、权限不足、数据不存在
    - 关键数据缺失时抛出异常而非返回默认值
    """

    # 2000积分可以访问的API接口
    REQUIRED_POINTS = 2000

    # 关键财务数据接口（需要2000积分）
    FINANCIAL_APIS = {
        "income": "利润表",
        "balancesheet": "资产负债表",
        "cashflow": "现金流量表",
        "fina_indicator": "财务指标",
        "daily_basic": "每日基本面",
    }

    def __init__(self, token: str = None):
        """
        初始化Tushare服务

        Args:
            token: Tushare Pro API Token (可选，默认从环境变量读取)
        """
        if token is None:
            from app.core.config import settings
            token = settings.tushare_token

        self.api = pro_api(token)
        logger.info("Tushare服务初始化完成")
        self._api_tested = False

    def _test_api_connection(self) -> None:
        """测试API连接和权限"""
        if self._api_tested:
            return

        try:
            # 测试调用一个基础接口验证token有效性
            df = self.api.trade_cal(
                exchange='SSE',
                start_date='20200101',
                end_date='20200105',
                fields='cal_date'
            )
            self._api_tested = True
            logger.info("Tushare API连接测试成功")
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="trade_cal",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0
                )
            else:
                raise TushareAPIError(
                    message=f"API连接失败: {error_msg}",
                    api_name="trade_cal",
                    original_error=e
                )

    def _get_latest_trade_date(self) -> str:
        """
        获取最近的交易日期（格式：YYYYMMDD）

        Returns:
            最近交易日期

        Raises:
            TushareAPIError: API调用失败
        """
        try:
            today = datetime.now().strftime('%Y%m%d')
            df = self.api.trade_cal(
                exchange='SSE',
                is_open='1',
                start_date='20200101',
                end_date=today,
                limit=1,
                fields='cal_date'
            )
            if df.empty:
                raise TushareAPIError("未找到交易日数据", api_name="trade_cal")
            return str(df.iloc[0]['cal_date'])
        except TushareAPIError:
            raise
        except Exception as e:
            raise TushareAPIError(
                message=f"获取最近交易日期失败: {str(e)}",
                api_name="trade_cal",
                original_error=e
            )

    def get_stock_name(self, ts_code: str) -> str:
        """
        获取股票名称

        Args:
            ts_code: 股票代码

        Returns:
            股票名称

        Raises:
            TushareDataNotFoundError: 股票代码不存在
            TushareAPIError: API调用失败
        """
        try:
            formatted = self._format_stock_code(ts_code)
            df = self.api.stock_basic(
                ts_code=formatted,
                fields='ts_code,name'
            )
            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="stock_basic",
                    stock_code=ts_code,
                    reason="股票代码不存在或未上市"
                )
            return str(df.iloc[0]['name'])
        except TushareDataNotFoundError:
            raise
        except Exception as e:
            raise TushareAPIError(
                message=f"获取股票名称失败: {str(e)}",
                api_name="stock_basic",
                stock_code=ts_code,
                original_error=e
            )

    def _format_stock_code(self, stock_code: str) -> str:
        """
        格式化股票代码为Tushare标准格式

        Args:
            stock_code: 股票代码（600519 或 600519.SH）

        Returns:
            格式化后的股票代码（600519.SH 或 000001.SZ）
        """
        # 如果已经包含后缀，直接返回
        if "." in stock_code:
            return stock_code

        # 根据股票代码前缀判断交易所
        if stock_code.startswith("6") or stock_code.startswith("5"):
            # 上海交易所：6开头的A股，5开头的基金
            return f"{stock_code}.SH"
        elif stock_code.startswith(("0", "3")):
            # 深圳交易所：0开头的A股，3开头的创业板
            return f"{stock_code}.SZ"
        else:
            # 默认为上海交易所
            return f"{stock_code}.SH"

    async def get_daily_basic(
        self, stock_code: str, trade_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取股票每日基本面数据

        Args:
            stock_code: 股票代码
            trade_date: 交易日期（可选，格式：YYYYMMDD）

        Returns:
            包含daily_basic数据的DataFrame

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
        """
        self._test_api_connection()

        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的每日基本面数据")

            # 如果没有指定日期，获取最新交易日
            if trade_date is None:
                trade_date = self._get_latest_trade_date()
                logger.info(f"使用最近交易日: {trade_date}")

            loop = asyncio.get_event_loop()

            # 优先使用 ts_code + trade_date 查询（权限要求低）
            df = await loop.run_in_executor(
                None,
                lambda: self.api.daily_basic(
                    ts_code=formatted_code,
                    trade_date=trade_date,
                    fields="ts_code,trade_date,close,turnover_rate,volume_ratio,pe,"
                    "pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,"
                    "free_share,total_mv,circ_mv",
                ),
            )

            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="daily_basic",
                    stock_code=formatted_code,
                    reason=f"在{trade_date}无数据"
                )

            return df

        except TushareDataNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="daily_basic",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0,
                    stock_code=stock_code
                )
            raise TushareAPIError(
                message=f"获取每日基本面数据失败: {error_msg}",
                api_name="daily_basic",
                stock_code=stock_code,
                original_error=e
            )

    async def get_income_statement(
        self, stock_code: str, period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取利润表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含income数据的DataFrame

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的利润表数据")

            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.api.income(
                    ts_code=formatted_code,
                    period=period,
                    fields="ts_code,ann_date,end_date,report_type,basic_eps,total_revenue,revenue,oper_cost,operate_profit,total_profit,total_cogs,sell_exp,admin_exp,fin_exp"
                ),
            )

            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="income",
                    stock_code=formatted_code,
                    reason=f"报告期{period}无数据"
                )

            return df

        except TushareDataNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="income",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0,
                    stock_code=stock_code
                )
            raise TushareAPIError(
                message=f"获取利润表数据失败: {error_msg}",
                api_name="income",
                stock_code=stock_code,
                original_error=e
            )

    async def get_balancesheet(
        self, stock_code: str, period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取资产负债表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含balancesheet数据的DataFrame

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的资产负债表数据")

            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.api.balancesheet(
                    ts_code=formatted_code,
                    period=period,
                    fields="ts_code,ann_date,f_ann_date,end_date,report_type,total_assets,total_hldr_eqy_exc_min_int,total_liab,total_cur_assets,total_cur_liab",
                ),
            )

            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="balancesheet",
                    stock_code=formatted_code,
                    reason=f"报告期{period}无数据"
                )

            return df

        except TushareDataNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="balancesheet",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0,
                    stock_code=stock_code
                )
            raise TushareAPIError(
                message=f"获取资产负债表数据失败: {error_msg}",
                api_name="balancesheet",
                stock_code=stock_code,
                original_error=e
            )

    async def get_cashflow(
        self, stock_code: str, period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取现金流量表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含cashflow数据的DataFrame

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的现金流量表数据")

            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.api.cashflow(
                    ts_code=formatted_code,
                    period=period,
                    fields="ts_code,ann_date,f_ann_date,end_date,report_type,net_profit,n_cashflow_act,n_cash_flows_fnc_act,n_cash_flows_inv_act,c_cash_equivalent_increase",
                ),
            )

            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="cashflow",
                    stock_code=formatted_code,
                    reason=f"报告期{period}无数据"
                )

            return df

        except TushareDataNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="cashflow",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0,
                    stock_code=stock_code
                )
            raise TushareAPIError(
                message=f"获取现金流量表数据失败: {error_msg}",
                api_name="cashflow",
                stock_code=stock_code,
                original_error=e
            )

    async def get_fina_indicator(
        self, stock_code: str, period: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取财务指标数据（ROE、利润率、流动比率等）

        Args:
            stock_code: 股票代码
            period: 报告期（可选）

        Returns:
            包含fina_indicator数据的DataFrame

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的财务指标数据")

            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.api.fina_indicator(
                    ts_code=formatted_code,
                    period=period,
                    fields="ts_code,ann_date,end_date,roe,roe_waa,grossprofit_margin,"
                    "netprofit_margin,current_ratio,quick_ratio,debt_to_assets,"
                    "op_yoy,netprofit_yoy,rev_yoy",
                ),
            )

            if df.empty:
                raise TushareDataNotFoundError(
                    api_name="fina_indicator",
                    stock_code=formatted_code,
                    reason=f"报告期{period}无数据"
                )

            return df

        except TushareDataNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "权限" in error_msg or "积分" in error_msg:
                raise TusharePermissionError(
                    api_name="fina_indicator",
                    required_points=self.REQUIRED_POINTS,
                    current_points=0,
                    stock_code=stock_code
                )
            raise TushareAPIError(
                message=f"获取财务指标数据失败: {error_msg}",
                api_name="fina_indicator",
                stock_code=stock_code,
                original_error=e
            )

    async def get_stock_fundamentals(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        获取股票完整基本面数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含所有基本面数据的字典，键为数据类型

        Raises:
            TushareAPIError: 任一API调用失败
            MissingCriticalDataError: 关键数据缺失
        """
        logger.info(f"获取股票 {stock_code} 的完整基本面数据")

        # 并发获取所有数据
        results = await asyncio.gather(
            self.get_daily_basic(stock_code),
            self.get_income_statement(stock_code, period),
            self.get_balancesheet(stock_code, period),
            self.get_cashflow(stock_code, period),
            self.get_fina_indicator(stock_code, period),
            return_exceptions=True,
        )

        # 检查结果
        fundamentals = {}
        errors = []

        # 日线数据（可选）
        if not isinstance(results[0], Exception) and results[0] is not None:
            fundamentals["daily_basic"] = results[0]
        else:
            logger.warning(f"日线数据获取失败: {results[0]}")

        # 利润表（必需）
        if isinstance(results[1], Exception):
            errors.append(f"利润表: {results[1]}")
        elif results[1] is not None:
            fundamentals["income"] = results[1]

        # 资产负债表（必需）
        if isinstance(results[2], Exception):
            errors.append(f"资产负债表: {results[2]}")
        elif results[2] is not None:
            fundamentals["balancesheet"] = results[2]

        # 现金流量表（必需）
        if isinstance(results[3], Exception):
            errors.append(f"现金流量表: {results[3]}")
        elif results[3] is not None:
            fundamentals["cashflow"] = results[3]

        # 财务指标（必需）
        if isinstance(results[4], Exception):
            errors.append(f"财务指标: {results[4]}")
        elif results[4] is not None:
            fundamentals["fina_indicator"] = results[4]

        # 检查关键数据是否完整
        required_data = ["income", "balancesheet", "cashflow", "fina_indicator"]
        missing_data = [d for d in required_data if d not in fundamentals]

        if missing_data:
            error_msg = f"缺少关键财务数据: {', '.join(missing_data)}"
            if errors:
                error_msg += f" | 错误: {'; '.join(errors)}"
            from app.services.exceptions import MissingCriticalDataError
            raise MissingCriticalDataError(
                missing_fields=missing_data,
                stock_code=stock_code
            )

        return fundamentals
