"""集成端到端测试"""
import pytest
import os
import sys
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch


class TestE2EAnalysisFlow:
    """端到端分析流程测试"""

    @patch("app.cli.main._get_service")
    @patch("app.cli.main._get_agents")
    def test_full_analysis_workflow(self, mock_get_agents, mock_get_service):
        """测试完整的分析工作流程"""
        # 准备Mock数据
        mock_service = Mock()
        mock_service.return_value.get_stock_data.return_value = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 30.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                "current_ratio": 3.0,
                "dividend_yield": 1.5,
                "revenue_growth": 15.0,
                "profit_growth": 18.0,
            },
            "moat_indicators": {
                "brand_strength": 9,
                "market_share": 50.0,
                "competitive_advantage": True,
            },
        }
        mock_get_service.return_value = mock_service

        # 准备Agent Mock
        from app.agents.value.buffet_agent import BuffetAgent

        mock_get_agents.return_value = {"buffet": BuffetAgent}

        # 执行CLI命令
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600519", "-v"])

        # 验证结果
        assert result.exit_code == 0
        assert "600519" in result.output
        assert "决策" in result.output or "DECISION" in result.output
        assert "贵州茅台" in result.output or "600519" in result.output

    @patch("app.cli.main._get_agents")
    def test_analysis_without_tushare(self, mock_get_agents):
        """测试没有Tushare服务时的分析流程（使用模拟数据）"""
        from app.agents.value.buffet_agent import BuffetAgent

        mock_get_agents.return_value = {"buffet": BuffetAgent}

        # 执行CLI命令（没有Mock服务，应该使用模拟数据）
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "600000"])

        # 验证结果
        assert result.exit_code == 0
        assert "600000" in result.output

    def test_buffett_agent_complete_analysis(self):
        """测试Buffett Agent完整分析流程"""
        from app.agents.value.buffet_agent import BuffetAgent

        agent = BuffetAgent()

        # 准备测试数据 - 优质价值股
        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 30.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                "current_ratio": 3.0,
                "dividend_yield": 1.5,
                "revenue_growth": 15.0,
                "profit_growth": 18.0,
            },
            "moat_indicators": {
                "brand_strength": 9,
                "market_share": 50.0,
                "competitive_advantage": True,
            },
        }

        # 执行分析
        analysis = agent.analyze(stock_data)

        # 验证分析结果结构
        assert "decision" in analysis
        assert "confidence" in analysis
        assert "reasoning" in analysis
        assert "key_factors" in analysis
        assert "scores" in analysis
        assert "total_score" in analysis

        # 执行投票
        vote = agent.vote(analysis)
        assert vote in ["buy", "sell", "hold"]

        # 执行辩论
        debate_context = {
            "stock": stock_data,
            "market_sentiment": "bullish",
            "other_opinions": ["其他Agent建议买入"],
        }
        debate_output = agent.debate(debate_context)
        assert isinstance(debate_output, str)
        assert len(debate_output) > 0


class TestConfigLoading:
    """配置加载测试"""

    def test_config_from_env_file(self):
        """测试从.env文件加载配置"""
        # 确保测试环境变量文件存在
        env_file = Path(__file__).parent.parent.parent / ".env.test"
        if not env_file.exists():
            pytest.skip(".env.test文件不存在")

        # 临时设置环境变量
        original_token = os.environ.get("TUSHARE_TOKEN")
        os.environ["TUSHARE_TOKEN"] = "test_token_from_env"

        try:
            # 重新加载配置
            import importlib

            if "app.core.config" in sys.modules:
                importlib.reload(sys.modules["app.core.config"])

            from app.core.config import settings

            assert settings.tushare_token == "test_token_from_env"

        finally:
            # 恢复原始环境变量
            if original_token:
                os.environ["TUSHARE_TOKEN"] = original_token
            else:
                os.environ.pop("TUSHARE_TOKEN", None)

    def test_config_defaults(self):
        """测试配置默认值"""
        from app.core.config import settings

        # 验证默认值
        assert settings.cache_ttl == 3600
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]


class TestCLIEntryPoint:
    """CLI入口点测试"""

    def test_cli_main_entry(self):
        """测试CLI主入口"""
        from app.cli.main import cli

        assert cli is not None

    def test_cli_help_output(self):
        """测试CLI帮助输出"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "投资智能体系统" in result.output
        assert "analyze" in result.output
        assert "config" in result.output
        assert "version" in result.output

    def test_cli_version_output(self):
        """测试版本信息输出"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["version"])

        assert result.exit_code == 0
        assert "0.1.0-alpha" in result.output


class TestDataFlow:
    """数据流测试"""

    def test_stock_data_structure(self):
        """测试股票数据结构"""
        # 准备符合结构的数据
        stock_data = {
            "symbol": "600000",
            "name": "测试股票",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 15.0,
                "pb_ratio": 2.0,
                "roe": 12.0,
                "debt_ratio": 40.0,
                "current_ratio": 1.5,
                "dividend_yield": 3.0,
                "revenue_growth": 8.0,
                "profit_growth": 10.0,
            },
            "moat_indicators": {
                "brand_strength": 7,
                "market_share": 15.0,
                "competitive_advantage": True,
            },
        }

        # 验证数据可以被Agent处理
        from app.agents.value.buffet_agent import BuffetAgent

        agent = BuffetAgent()
        analysis = agent.analyze(stock_data)

        assert analysis is not None
        assert "decision" in analysis

    def test_analysis_result_structure(self):
        """测试分析结果结构"""
        from app.agents.value.buffet_agent import BuffetAgent

        agent = BuffetAgent()
        stock_data = {
            "symbol": "600000",
            "price": 10.0,
            "metrics": {"pe_ratio": 15.0, "pb_ratio": 2.0},
        }

        analysis = agent.analyze(stock_data)

        # 验证结果结构符合预期
        required_fields = ["decision", "confidence", "reasoning", "key_factors"]
        for field in required_fields:
            assert field in analysis, f"缺少必需字段: {field}"

        # 验证数据类型
        assert isinstance(analysis["decision"], str)
        assert isinstance(analysis["confidence"], float)
        assert isinstance(analysis["reasoning"], str)
        assert isinstance(analysis["key_factors"], list)

        # 验证值的有效性
        assert analysis["decision"] in ["buy", "sell", "hold"]
        assert 0 <= analysis["confidence"] <= 1


class TestModuleIntegration:
    """模块集成测试"""

    def test_agents_module_import(self):
        """测试Agents模块导入"""
        from app.agents import BaseAgent
        from app.agents.value import BuffetAgent

        assert BaseAgent is not None
        assert BuffetAgent is not None
        assert issubclass(BuffettAgent, BaseAgent)

    def test_core_module_import(self):
        """测试核心模块导入"""
        from app.core import settings
        from app.core.state import AnalysisState, AgentVote

        assert settings is not None
        assert AnalysisState is not None
        assert AgentVote is not None

    def test_services_module_import(self):
        """测试服务模块导入"""
        try:
            from app.services import TushareService
            # 如果导入成功，验证它是类
            assert TushareService is not None
        except ImportError:
            # 如果导入失败（没有tushare包），这是预期的
            pass


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_stock_symbol(self):
        """测试无效股票代码处理"""
        from app.cli.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "INVALID"])

        # 应该有错误处理，不会崩溃
        assert result.exit_code == 0

    def test_missing_config(self):
        """测试缺少配置的处理"""
        # 临时移除环境变量
        original_token = os.environ.get("TUSHARE_TOKEN")
        os.environ.pop("TUSHARE_TOKEN", None)

        try:
            # 重新加载配置
            import importlib

            if "app.core.config" in sys.modules:
                importlib.reload(sys.modules["app.core.config"])

            # 尝试创建配置（应该处理缺失的配置）
            try:
                from app.core.config import Settings

                settings = Settings()
            except Exception as e:
                # 预期会抛出验证错误
                assert "tushare_token" in str(e).lower() or "field required" in str(e).lower()

        finally:
            # 恢复环境变量
            if original_token:
                os.environ["TUSHARE_TOKEN"] = original_token


class TestPerformance:
    """性能测试"""

    def test_analysis_performance(self):
        """测试分析性能"""
        import time
        from app.agents.value.buffet_agent import BuffetAgent

        agent = BuffetAgent()
        stock_data = {
            "symbol": "600000",
            "price": 10.0,
            "metrics": {"pe_ratio": 15.0, "pb_ratio": 2.0, "roe": 12.0},
            "moat_indicators": {"brand_strength": 7, "market_share": 15.0},
        }

        # 测量分析时间
        start_time = time.time()
        analysis = agent.analyze(stock_data)
        end_time = time.time()

        # 验证分析在合理时间内完成
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"分析耗时过长: {execution_time:.2f}秒"

        # 验证结果正确
        assert analysis is not None
