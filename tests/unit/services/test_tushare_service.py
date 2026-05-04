"""TushareService单元测试"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from app.services.tushare_service import TushareService
from tests.fixtures.stock_data import (
    get_mock_daily_basic_data,
    get_mock_income_data,
    get_mock_balance_data,
    get_mock_cashflow_data,
    get_empty_dataframe,
    get_stock_codes,
)


class TestTushareService:
    """TushareService测试套件"""

    @pytest.fixture
    def service(self):
        """创建TushareService实例"""
        with patch("app.services.tushare_service.pro_api"):
            service = TushareService(token="test_token")
            return service

    @pytest.fixture
    def mock_api(self, service):
        """Mock Tushare API"""
        return service.api

    def test_init_with_token(self):
        """测试使用token初始化"""
        with patch("app.services.tushare_service.pro_api") as mock_pro_api:
            mock_api_instance = MagicMock()
            mock_pro_api.return_value = mock_api_instance

            service = TushareService(token="test_token")

            mock_pro_api.assert_called_once_with("test_token")
            assert service.api == mock_api_instance

    def test_format_stock_code_shanghai(self, service):
        """测试格式化上海股票代码"""
        codes = ["600519", "600000", "601318"]
        for code in codes:
            formatted = service._format_stock_code(code)
            assert formatted == f"{code}.SH"

    def test_format_stock_code_shenzhen(self, service):
        """测试格式化深圳股票代码"""
        codes = ["000001", "000002", "300001"]
        for code in codes:
            formatted = service._format_stock_code(code)
            assert formatted == f"{code}.SZ"

    def test_format_stock_code_already_formatted(self, service):
        """测试已经格式化的股票代码"""
        codes = ["600519.SH", "000001.SZ"]
        for code in codes:
            formatted = service._format_stock_code(code)
            assert formatted == code

    async def test_get_daily_basic_success(self, service, mock_api):
        """测试成功获取每日基本面数据"""
        mock_data = get_mock_daily_basic_data()
        mock_api.daily_basic.return_value = mock_data

        result = await service.get_daily_basic("600519")

        assert isinstance(result, dict)
        assert "daily_basic" in result
        assert not result["daily_basic"].empty
        assert result["daily_basic"].iloc[0]["ts_code"] == "600519.SH"

    async def test_get_daily_basic_empty_data(self, service, mock_api):
        """测试获取空数据时的处理"""
        mock_api.daily_basic.return_value = get_empty_dataframe()

        result = await service.get_daily_basic("600519")

        assert result == {}

    async def test_get_income_statement_success(self, service, mock_api):
        """测试成功获取利润表数据"""
        mock_data = get_mock_income_data()
        mock_api.income.return_value = mock_data

        result = await service.get_income_statement("600519")

        assert isinstance(result, dict)
        assert "income" in result
        assert not result["income"].empty
        assert result["income"].iloc[0]["ts_code"] == "600519.SH"

    async def test_get_income_statement_empty_data(self, service, mock_api):
        """测试利润表空数据处理"""
        mock_api.income.return_value = get_empty_dataframe()

        result = await service.get_income_statement("600519")

        assert result == {}

    async def test_get_balancesheet_success(self, service, mock_api):
        """测试成功获取资产负债表数据"""
        mock_data = get_mock_balance_data()
        mock_api.balancesheet.return_value = mock_data

        result = await service.get_balancesheet("600519")

        assert isinstance(result, dict)
        assert "balancesheet" in result
        assert not result["balancesheet"].empty
        assert result["balancesheet"].iloc[0]["ts_code"] == "600519.SH"

    async def test_get_balancesheet_empty_data(self, service, mock_api):
        """测试资产负债表空数据处理"""
        mock_api.balancesheet.return_value = get_empty_dataframe()

        result = await service.get_balancesheet("600519")

        assert result == {}

    async def test_get_cashflow_success(self, service, mock_api):
        """测试成功获取现金流量表数据"""
        mock_data = get_mock_cashflow_data()
        mock_api.cashflow.return_value = mock_data

        result = await service.get_cashflow("600519")

        assert isinstance(result, dict)
        assert "cashflow" in result
        assert not result["cashflow"].empty
        assert result["cashflow"].iloc[0]["ts_code"] == "600519.SH"

    async def test_get_cashflow_empty_data(self, service, mock_api):
        """测试现金流量表空数据处理"""
        mock_api.cashflow.return_value = get_empty_dataframe()

        result = await service.get_cashflow("600519")

        assert result == {}

    async def test_get_stock_fundamentals_complete(self, service, mock_api):
        """测试获取完整股票基本面数据"""
        # 设置所有mock返回值
        mock_api.daily_basic.return_value = get_mock_daily_basic_data()
        mock_api.income.return_value = get_mock_income_data()
        mock_api.balancesheet.return_value = get_mock_balance_data()
        mock_api.cashflow.return_value = get_mock_cashflow_data()

        result = await service.get_stock_fundamentals("600519")

        assert isinstance(result, dict)
        assert "daily_basic" in result
        assert "income" in result
        assert "balancesheet" in result
        assert "cashflow" in result

        # 验证所有数据都不为空
        assert not result["daily_basic"].empty
        assert not result["income"].empty
        assert not result["balancesheet"].empty
        assert not result["cashflow"].empty

    async def test_get_stock_fundamentals_partial_data(self, service, mock_api):
        """测试部分数据缺失时的处理"""
        # 设置部分返回空数据
        mock_api.daily_basic.return_value = get_mock_daily_basic_data()
        mock_api.income.return_value = get_empty_dataframe()
        mock_api.balancesheet.return_value = get_mock_balance_data()
        mock_api.cashflow.return_value = get_empty_dataframe()

        result = await service.get_stock_fundamentals("600519")

        assert isinstance(result, dict)
        # 只有daily_basic和balancesheet有数据
        assert "daily_basic" in result
        assert "balancesheet" in result
        # income和cashflow应该不在结果中
        assert "income" not in result
        assert "cashflow" not in result

    async def test_get_stock_fundamentals_all_empty(self, service, mock_api):
        """测试所有数据都为空时返回空字典"""
        mock_api.daily_basic.return_value = get_empty_dataframe()
        mock_api.income.return_value = get_empty_dataframe()
        mock_api.balancesheet.return_value = get_empty_dataframe()
        mock_api.cashflow.return_value = get_empty_dataframe()

        result = await service.get_stock_fundamentals("600519")

        assert result == {}

    def test_format_stock_code_various_formats(self, service):
        """测试各种格式的股票代码"""
        test_cases = [
            ("600519", "600519.SH"),
            ("000001", "000001.SZ"),
            ("300001", "300001.SZ"),
            ("600519.SH", "600519.SH"),
            ("000001.SZ", "000001.SZ"),
            ("688001", "688001.SH"),  # 科创板
        ]

        for input_code, expected in test_cases:
            result = service._format_stock_code(input_code)
            assert result == expected, f"Failed for {input_code}: expected {expected}, got {result}"

    async def test_api_call_parameters(self, service, mock_api):
        """测试API调用参数传递"""
        mock_data = get_mock_daily_basic_data()
        mock_api.daily_basic.return_value = mock_data

        await service.get_daily_basic("600519")

        # 验证API调用参数
        mock_api.daily_basic.assert_called_once()
        call_args = mock_api.daily_basic.call_args
        assert call_args is not None

    async def test_multiple_stock_codes(self, service, mock_api):
        """测试处理多个股票代码"""
        mock_data = get_mock_daily_basic_data()
        mock_api.daily_basic.return_value = mock_data

        stock_codes = ["600519", "000001", "300001"]
        for code in stock_codes:
            result = await service.get_daily_basic(code)
            assert isinstance(result, dict)
            if result:
                assert "daily_basic" in result
