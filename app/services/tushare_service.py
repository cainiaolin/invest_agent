"""Tushare数据服务"""

import asyncio
from typing import Optional, Dict, Any
import pandas as pd
from tushare import pro_api
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TushareService:
    """Tushare数据服务封装类"""

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

    def _get_latest_trade_date(self) -> Optional[str]:
        """获取最近的交易日期（格式：YYYYMMDD）"""
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
            if not df.empty:
                return str(df.iloc[0]['cal_date'])
        except Exception as e:
            logger.error(f"获取最近交易日期失败: {e}")
        return None

    def get_stock_name(self, ts_code: str) -> str:
        """获取股票名称"""
        try:
            formatted = self._format_stock_code(ts_code)
            df = self.api.stock_basic(
                ts_code=formatted,
                fields='ts_code,name'
            )
            if not df.empty:
                return str(df.iloc[0]['name'])
        except Exception as e:
            logger.error(f"获取股票名称失败: {e}")
        return ""

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
    ) -> Dict[str, Any]:
        """
        获取股票每日基本面数据

        Args:
            stock_code: 股票代码
            trade_date: 交易日期（可选，格式：YYYYMMDD）

        Returns:
            包含daily_basic数据的字典，或空字典（如果无数据）
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的每日基本面数据")

            # 如果没有指定日期，获取最新交易日
            if trade_date is None:
                trade_date = self._get_latest_trade_date()
                if trade_date:
                    logger.info(f"使用最近交易日: {trade_date}")

            # 在线程池中执行同步API调用
            loop = asyncio.get_event_loop()

            # 优先使用 ts_code + trade_date 查询（权限要求低）
            if trade_date:
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
            else:
                # 回退：仅用 ts_code 查询
                df = await loop.run_in_executor(
                    None,
                    lambda: self.api.daily_basic(
                        ts_code=formatted_code,
                        fields="ts_code,trade_date,close,turnover_rate,volume_ratio,pe,"
                        "pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,"
                        "free_share,total_mv,circ_mv",
                    ),
                )

            if df.empty:
                logger.warning(f"股票 {formatted_code} 的每日基本面数据为空")
                return {}

            return {"daily_basic": df}

        except Exception as e:
            logger.error(f"获取每日基本面数据失败: {e}")
            return {}

    async def get_income_statement(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取利润表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含income数据的字典，或空字典（如果无数据）
        """
        try:
            formatted_code = self._format_stock_code(stock_code)
            logger.info(f"获取 {formatted_code} 的利润表数据")

            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None,
                lambda: self.api.income(
                    ts_code=formatted_code, period=period, fields="ts_code,ann_date,end_date,report_type,basic_eps,total_revenue,revenue,oper_cost,total_profit,total_cogs,sell_exp,admin_exp,fin_exp"
                ),
            )

            if df.empty:
                logger.warning(f"股票 {formatted_code} 的利润表数据为空")
                return {}

            return {"income": df}

        except Exception as e:
            logger.error(f"获取利润表数据失败: {e}")
            return {}

    async def get_balancesheet(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取资产负债表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含balancesheet数据的字典，或空字典（如果无数据）
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
                logger.warning(f"股票 {formatted_code} 的资产负债表数据为空")
                return {}

            return {"balancesheet": df}

        except Exception as e:
            logger.error(f"获取资产负债表数据失败: {e}")
            return {}

    async def get_cashflow(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取现金流量表数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含cashflow数据的字典，或空字典（如果无数据）
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
                logger.warning(f"股票 {formatted_code} 的现金流量表数据为空")
                return {}

            return {"cashflow": df}

        except Exception as e:
            logger.error(f"获取现金流量表数据失败: {e}")
            return {}

    async def get_fina_indicator(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取财务指标数据（ROE、利润率、流动比率等）

        Args:
            stock_code: 股票代码
            period: 报告期（可选）

        Returns:
            包含fina_indicator数据的字典
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
                logger.warning(f"股票 {formatted_code} 的财务指标数据为空")
                return {}

            return {"fina_indicator": df}

        except Exception as e:
            logger.error(f"获取财务指标数据失败: {e}")
            return {}

    async def get_stock_fundamentals(
        self, stock_code: str, period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取股票完整基本面数据

        Args:
            stock_code: 股票代码
            period: 报告期（可选，格式：YYYYMMDD）

        Returns:
            包含所有基本面数据的字典，或空字典（如果无数据）
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

        # 合并结果
        fundamentals = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"获取数据时发生错误: {result}")
                continue
            if isinstance(result, dict) and result:
                fundamentals.update(result)

        if not fundamentals:
            logger.warning(f"股票 {stock_code} 没有获取到任何基本面数据")
            return {}

        return fundamentals
