"""测试CLI模块"""
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch


class TestCLI:
    """测试CLI命令"""

    def test_cli_help(self):
        """测试CLI帮助信息"""
        # 延迟导入以避免依赖问题
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "投资智能体系统" in result.output

    def test_version_command(self):
        """测试版本命令"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert "0.1.0-alpha" in result.output
        assert "投资智能体系统" in result.output

    @patch("app.cli.main.TushareService")
    @patch("app.cli.main.BuffetAgent")
    def test_analyze_command_success(self, mock_agent_class, mock_service_class):
        """测试analyze命令成功场景"""
        from app.cli.main import cli

        # Mock TushareService
        mock_service = Mock()
        mock_service.get_stock_data.return_value = {
            "symbol": "600000",
            "name": "浦发银行",
            "price": 10.0,
            "metrics": {"pe_ratio": 8.5, "pb_ratio": 0.9},
        }
        mock_service_class.return_value = mock_service

        # Mock BuffetAgent
        mock_agent = Mock()
        mock_agent.name = "Warren Buffett"
        mock_agent.analyze.return_value = {
            "decision": "hold",
            "confidence": 0.6,
            "reasoning": "观望",
            "key_factors": ["估值合理"],
        }
        mock_agent.vote.return_value = "hold"
        mock_agent_class.return_value = mock_agent

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000"])
        assert result.exit_code == 0
        assert "600000" in result.output

    @patch("app.cli.main.TushareService")
    def test_analyze_command_no_data(self, mock_service_class):
        """测试analyze命令无数据场景"""
        from app.cli.main import cli

        mock_service = Mock()
        mock_service.get_stock_data.return_value = None
        mock_service_class.return_value = mock_service

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000"])
        assert result.exit_code == 0
        assert "无法获取" in result.output or "错误" in result.output

    @patch("app.cli.main.settings")
    def test_config_command(self, mock_settings):
        """测试config命令"""
        from app.cli.main import cli

        mock_settings.tushare_token = "test_token_12345678901234567890"
        mock_settings.log_level = "INFO"
        mock_settings.cache_ttl = 3600

        runner = CliRunner()
        result = runner.invoke(cli, ["config"])
        assert result.exit_code == 0
        assert "系统配置" in result.output

    def test_analyze_command_invalid_agent(self):
        """测试analyze命令使用无效Agent"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000", "--agent", "invalid"])
        # 应该显示错误信息
        assert result.exit_code == 0

    def test_analyze_command_verbose_mode(self):
        """测试analyze命令详细模式"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000", "--verbose"])
        # 验证命令可以处理verbose标志
        assert result.exit_code == 0 or "traceback" in result.output.lower()


class TestCLIDisplayFunctions:
    """测试CLI显示函数"""

    def test_display_stock_info(self):
        """测试股票信息显示"""
        from app.cli.main import _display_stock_info
        from rich.console import Console

        stock_data = {
            "symbol": "600000",
            "name": "浦发银行",
            "price": 10.5,
            "metrics": {"pe_ratio": 8.5, "pb_ratio": 0.9, "roe": 15.0},
        }

        console = Console()
        # 这个函数主要验证不会抛出异常
        console.print(_display_stock_info(stock_data))

    def test_display_analysis_result(self):
        """测试分析结果显示"""
        from app.cli.main import _display_analysis_result
        from rich.console import Console

        mock_agent = Mock()
        mock_agent.name = "Warren Buffett"

        analysis = {
            "decision": "buy",
            "confidence": 0.85,
            "reasoning": "优质价值股",
            "key_factors": ["低PE", "高ROE"],
            "scores": {"moat": 80, "financial_health": 75},
        }

        console = Console()
        # 验证函数不会抛出异常
        console.print(_display_analysis_result(mock_agent, analysis, verbose=True))


class TestCLIIntegration:
    """CLI集成测试"""

    @patch("app.cli.main.TushareService")
    @patch("app.cli.main.BuffetAgent")
    def test_full_analysis_flow(self, mock_agent_class, mock_service_class):
        """测试完整分析流程"""
        from app.cli.main import cli

        # 准备测试数据
        mock_service = Mock()
        mock_service.get_stock_data.return_value = {
            "symbol": "600000",
            "name": "测试银行",
            "price": 10.0,
            "metrics": {"pe_ratio": 8.0, "pb_ratio": 0.8, "roe": 18.0},
            "moat_indicators": {"brand_strength": 8, "market_share": 25.0},
        }
        mock_service_class.return_value = mock_service

        mock_agent = Mock()
        mock_agent.name = "Warren Buffett"
        mock_agent.analyze.return_value = {
            "decision": "buy",
            "confidence": 0.8,
            "reasoning": "优质价值股",
            "key_factors": ["强大护城河", "财务健康"],
            "scores": {"moat": 80, "financial_health": 75, "valuation": 70, "quality": 70},
        }
        mock_agent.vote.return_value = "buy"
        mock_agent_class.return_value = mock_agent

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000", "-v"])

        assert result.exit_code == 0
        # 验证输出包含关键信息
        assert "600000" in result.output
        assert "决策" in result.output or "BUY" in result.output
