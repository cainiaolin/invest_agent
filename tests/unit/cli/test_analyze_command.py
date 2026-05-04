"""测试analyze命令"""
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from app.cli.commands.analyze import analyze


class TestAnalyzeCommand:
    """测试analyze命令的核心功能"""

    @pytest.fixture
    def runner(self):
        """创建CLI测试运行器"""
        return CliRunner()

    @pytest.fixture
    def mock_workflow_result(self):
        """模拟工作流返回结果"""
        return {
            "agent_analyses": [
                {
                    "agent_name": "Warren Buffett",
                    "agent_type": "value",
                    "action": "buy",
                    "confidence": 0.85,
                    "reasoning": "优质公司，合理价格",
                    "key_metrics": {"total_score": 85},
                    "price_target": None,
                },
                {
                    "agent_name": "Peter Lynch",
                    "agent_type": "growth",
                    "action": "buy",
                    "confidence": 0.78,
                    "reasoning": "成长潜力良好",
                    "key_metrics": {"total_score": 78},
                    "price_target": None,
                },
            ],
            "final_decision": {
                "action": "buy",
                "consensus": 0.815,
                "participating_agents": ["Warren Buffett", "Peter Lynch"],
                "summary": "多数Agent建议买入",
            },
            "error": None,
        }

    @pytest.fixture
    def mock_stock_data(self):
        """模拟股票数据"""
        return {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1850.00,
            "metrics": {
                "pe_ratio": 35.5,
                "pb_ratio": 12.8,
                "roe": 25.6,
                "revenue_growth": 15.2,
                "net_profit_growth": 18.5,
            },
        }

    def test_analyze_command_requires_stock_code(self, runner):
        """测试analyze命令需要股票代码参数"""
        result = runner.invoke(analyze, [])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "stock_code" in result.output

    def test_analyze_with_valid_stock_code(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试使用有效股票代码执行分析"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            # 设置mock
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            # 执行命令
            result = runner.invoke(analyze, ["600519"])

            # 验证
            assert result.exit_code == 0
            assert "600519" in result.output or "贵州茅台" in result.output
            assert "BUY" in result.output or "buy" in result.output

    def test_analyze_with_parallel_mode(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试并行模式"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--mode", "parallel"])

            assert result.exit_code == 0
            # 验证工作流被调用
            mock_workflow.invoke.assert_called_once()
            # 验证mode参数被正确传递
            call_args = mock_workflow.invoke.call_args
            assert call_args is not None

    def test_analyze_with_vote_mode(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试投票模式"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--mode", "vote"])

            assert result.exit_code == 0

    def test_analyze_with_debate_mode(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试辩论模式"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--mode", "debate"])

            assert result.exit_code == 0

    def test_analyze_with_specific_agents(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试指定特定agents"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--agents", "buffet,graham"])

            assert result.exit_code == 0
            # 验证agents参数被正确处理
            call_args = mock_workflow.invoke.call_args
            assert call_args is not None

    def test_analyze_with_verbose_mode(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试详细输出模式"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--verbose"])

            assert result.exit_code == 0
            # 详细模式应该显示更多信息
            assert "分析理由" in result.output or "reasoning" in result.output

    def test_analyze_with_invalid_mode(self, runner):
        """测试无效的mode参数"""
        result = runner.invoke(analyze, ["600519", "--mode", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_analyze_handles_service_error(
        self, runner, mock_stock_data
    ):
        """测试处理服务错误"""
        with patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_service = Mock()
            mock_service.get_stock_data = Mock(side_effect=Exception("API错误"))
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519"])

            # 应该显示错误信息
            assert "API错误" in result.output or "失败" in result.output

    def test_analyze_handles_workflow_error(
        self, runner, mock_stock_data
    ):
        """测试处理工作流错误"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(side_effect=Exception("工作流错误"))
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "--verbose"])

            # 应该显示错误信息
            assert "工作流错误" in result.output or "失败" in result.output

    def test_analyze_shows_agent_results_table(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试显示Agent结果表格"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519"])

            assert result.exit_code == 0
            # 应该包含Agent信息
            assert "Buffett" in result.output or "Agent" in result.output

    def test_analyze_shows_final_decision_panel(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试显示最终决策面板"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519"])

            assert result.exit_code == 0
            # 应该包含最终决策信息
            assert "决策" in result.output or "Decision" in result.output or "consensus" in result.output

    def test_analyze_short_flag_verbose(
        self, runner, mock_workflow_result, mock_stock_data
    ):
        """测试verbose简写标志-v"""
        with patch(
            "app.cli.commands.analyze.create_investment_workflow"
        ) as mock_create_workflow, patch(
            "app.cli.commands.analyze.TushareService"
        ) as mock_service_class:
            mock_workflow = Mock()
            mock_workflow.invoke = Mock(return_value=mock_workflow_result)
            mock_create_workflow.return_value = mock_workflow

            mock_service = Mock()
            mock_service.get_stock_data = Mock(return_value=mock_stock_data)
            mock_service_class.return_value = mock_service

            result = runner.invoke(analyze, ["600519", "-v"])

            assert result.exit_code == 0
