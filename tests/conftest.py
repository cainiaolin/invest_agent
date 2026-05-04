"""pytest配置和共享fixtures"""

import pytest
import os
from pathlib import Path

# 设置测试环境变量
os.environ.setdefault("TUSHARE_TOKEN", "test_token_for_pytest")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_stock_code():
    """模拟股票代码"""
    return "600519"


@pytest.fixture
def mock_tushare_token():
    """模拟Tushare Token"""
    return "test_token_123"
