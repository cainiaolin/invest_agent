"""配置管理测试"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from pydantic import ValidationError


def test_settings_loads_from_env(monkeypatch):
    """测试配置从环境变量加载"""
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token_123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # 重新导入模块以触发新的环境变量
    import importlib
    if 'app.core.config' in sys.modules:
        importlib.reload(sys.modules['app.core.config'])

    from app.core.config import settings

    assert settings.tushare_token == "test_token_123"
    assert settings.log_level == "DEBUG"


def test_settings_default_values(monkeypatch):
    """测试配置默认值"""
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token")

    # 重新导入模块
    import importlib
    if 'app.core.config' in sys.modules:
        importlib.reload(sys.modules['app.core.config'])

    from app.core.config import settings

    assert settings.cache_ttl == 3600
    assert settings.log_level == "INFO"


def test_settings_missing_token():
    """测试缺少必需配置时报错"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    env_file = Path(temp_dir) / ".env"
    env_file.write_text("")  # 空的.env文件

    original_cwd = os.getcwd()

    try:
        # 改变工作目录到临时目录
        os.chdir(temp_dir)

        # 确保没有环境变量
        if "TUSHARE_TOKEN" in os.environ:
            del os.environ["TUSHARE_TOKEN"]

        # 清除已加载的模块
        if 'app.core.config' in sys.modules:
            del sys.modules['app.core.config']
        if 'app.core' in sys.modules:
            del sys.modules['app.core']

        # 修改Settings的env_file配置
        from app.core.config import Settings
        original_config = Settings.model_config.copy()
        Settings.model_config['env_file'] = str(env_file)

        try:
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            # 验证错误信息包含正确的字段
            assert 'tushare_token' in str(exc_info.value)
            assert 'Field required' in str(exc_info.value)
        finally:
            # 恢复原配置
            Settings.model_config = original_config

    finally:
        # 恢复工作目录
        os.chdir(original_cwd)
        # 清理临时目录
        shutil.rmtree(temp_dir)
        # 确保恢复环境变量
        os.environ["TUSHARE_TOKEN"] = "test_token"
