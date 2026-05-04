"""股票数据测试fixtures"""

import pandas as pd
from datetime import datetime


def get_mock_daily_basic_data() -> pd.DataFrame:
    """模拟每日基本面数据"""
    data = {
        "ts_code": ["600519.SH", "000001.SZ"],
        "trade_date": ["20240101", "20240101"],
        "close": [1800.50, 12.35],
        "turnover_rate": [0.85, 1.23],
        "volume_ratio": [1.2, 0.95],
        "pe": [35.5, 8.2],
        "pe_ttm": [36.2, 8.5],
        "pb": [12.5, 0.95],
        "ps": [15.3, 2.1],
        "ps_ttm": [15.8, 2.2],
        "dv_ratio": [2.5, 1.8],
        "dv_ttm": [2.8, 2.0],
        "total_share": [125619.70, 1940555.66],
        "float_share": [125619.70, 1940555.66],
        "free_share": [125619.70, 1940555.66],
        "total_mv": [225870.8, 24015.6],
        "circ_mv": [225870.8, 24015.6],
    }
    return pd.DataFrame(data)


def get_mock_income_data() -> pd.DataFrame:
    """模拟利润表数据"""
    data = {
        "ts_code": ["600519.SH", "600519.SH"],
        "ann_date": ["20240120", "20230121"],
        "f_ann_date": ["20240120", "20230121"],
        "end_date": ["20231231", "20221231"],
        "report_type": ["1", "1"],
        "basic_eps": [45.25, 42.15],
        "diluted_eps": [45.25, 42.15],
        "total_revenue": [150560700000.0, 127560000000.0],
        "revenue": [150560700000.0, 127560000000.0],
        "int_income": [0.0, 0.0],
        "prem_earned": [0.0, 0.0],
        "comm_income": [0.0, 0.0],
        "n_oth_income": [0.0, 0.0],
        "n_oth_b_income": [0.0, 0.0],
        "prem_income": [0.0, 0.0],
        "out_prem": [0.0, 0.0],
        "une_prem_reser": [0.0, 0.0],
        "reins_income": [0.0, 0.0],
        "n_sec_tb_income": [0.0, 0.0],
        "n_sec_uw_income": [0.0, 0.0],
        "n_asset_mg_income": [0.0, 0.0],
        "oth_b_income": [0.0, 0.0],
        "fv_value_chg_gain": [0.0, 0.0],
        "invest_income": [1234567.0, 987654.0],
        "ass_invest_income": [0.0, 0.0],
        "total_cogs": [45678900.0, 38901200.0],
        "oper_cost": [45678900.0, 38901200.0],
        "int_exp": [0.0, 0.0],
        "comm_exp": [0.0, 0.0],
        "biz_tax_surchg": [25678900.0, 21345600.0],
        "sell_exp": [85678900.0, 72345600.0],
        "admin_exp": [98765400.0, 87654300.0],
        "fin_exp": [-1234567.0, -987654.0],
        "assets_impair_loss": [0.0, 0.0],
        "prem_refund": [0.0, 0.0],
        "comp_ser_pay": [0.0, 0.0],
        "reser_insur_liab": [0.0, 0.0],
        "pay_claim_premin": [0.0, 0.0],
        "insur_rese_pay": [0.0, 0.0],
        "reinsur_cost": [0.0, 0.0],
        "n_sec_biz_cost": [0.0, 0.0],
        "n_prot_fund_accur": [0.0, 0.0],
        "n_acg_fund_accur": [0.0, 0.0],
        "oper_exp": [0.0, 0.0],
        "oper_profit": [74787024333.0, 65012345678.0],
        "non_oper_income": [23456789.0, 19876543.0],
        "non_oper_exp": [1234567.0, 987654.0],
        "n_disp_subs_hld_eqt_inc": [0.0, 0.0],
        "fa_value_chg_gain": [0.0, 0.0],
        "impair_loss_assets": [0.0, 0.0],
        "credit_impar_loss_fin assets": [0.0, 0.0],
        "credit_impar_loss_inv_assets": [0.0, 0.0],
        "totprofit": [74818203055.0, 65112697567.0],
        "income_tax": [18704550764.0, 16278174392.0],
        "net_profit": [56113652291.0, 48834523175.0],
        "net_profit_inc_parent": [56113652291.0, 48834523175.0],
        "minority_gain": [0.0, 0.0],
    }
    return pd.DataFrame(data)


def get_mock_balance_data() -> pd.DataFrame:
    """模拟资产负债表数据"""
    data = {
        "ts_code": ["600519.SH", "600519.SH"],
        "ann_date": ["20240120", "20230121"],
        "f_ann_date": ["20240120", "20230121"],
        "end_date": ["20231231", "20221231"],
        "report_type": ["1", "1"],
        "total_assets": [245678900000.0, 234567800000.0],
        "total_hldr_eqy_exc_min_int": [215678900000.0, 204567800000.0],
        "equities_parent_comp": [215678900000.0, 204567800000.0],
        "total_liab": [30000000000.0, 30000000000.0],
        "current_assets": [180000000000.0, 170000000000.0],
        "current_liab": [28000000000.0, 27000000000.0],
        "cash_equivalents": [150000000000.0, 140000000000.0],
        "inventory": [4500000000.0, 4200000000.0],
        "accounts_receivable": [123456789.0, 98765432.0],
    }
    return pd.DataFrame(data)


def get_mock_cashflow_data() -> pd.DataFrame:
    """模拟现金流量表数据"""
    data = {
        "ts_code": ["600519.SH", "600519.SH"],
        "ann_date": ["20240120", "20230121"],
        "f_ann_date": ["20240120", "20230121"],
        "end_date": ["20231231", "20221231"],
        "report_type": ["1", "1"],
        "net_profit": [56113652291.0, 48834523175.0],
        "n_cashflow_act": [72345678901.0, 65432109876.0],
        "n_cash_flows_fnc_act": [-1234567890.0, -987654321.0],
        "n_cash_flows_inv_act": [-23456789012.0, -19876543210.0],
        "c_cash_equivalent_increase": [47689012345.0, 43432123456.0],
    }
    return pd.DataFrame(data)


def get_empty_dataframe() -> pd.DataFrame:
    """返回空DataFrame"""
    return pd.DataFrame()


def get_stock_codes():
    """返回测试用股票代码"""
    return {
        "shanghai": "600519",  # 贵州茅台
        "shenzhen": "000001",  # 平安银行
        "formatted_sh": "600519.SH",
        "formatted_sz": "000001.SZ",
    }
