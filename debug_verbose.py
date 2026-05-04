"""Debug verbose mode issue"""
import sys
sys.path.insert(0, 'E:/claude code/invest_agent/invest_agent_by_graph')

from click.testing import CliRunner
from unittest.mock import Mock, patch

def debug_verbose():
    """Debug verbose mode"""
    print("Debugging verbose mode...")

    from app.cli.main import cli
    runner = CliRunner()

    mock_stock_data = {
        "symbol": "600519",
        "name": "贵州茅台",
        "price": 1850.00,
        "metrics": {
            "pe_ratio": 35.5,
            "pb_ratio": 12.8,
            "roe": 25.6,
        }
    }

    mock_result = {
        "agent_analyses": [
            {
                "agent_name": "Warren Buffett",
                "agent_type": "value",
                "action": "buy",
                "confidence": 0.85,
                "reasoning": "优质公司",
                "key_metrics": {"total_score": 85},
                "price_target": None,
            },
        ],
        "final_decision": {
            "action": "buy",
            "consensus": 0.85,
            "participating_agents": ["Warren Buffett"],
            "summary": "建议买入",
        },
        "error": None,
    }

    with patch('app.cli.commands.analyze._get_tushare_service') as mock_get_service, \
         patch('app.cli.commands.analyze._get_workflow') as mock_get_workflow:

        mock_service_class = Mock()
        mock_service = Mock()
        mock_service.get_stock_data = Mock(return_value=mock_stock_data)
        mock_service_class.return_value = mock_service
        mock_get_service.return_value = mock_service_class

        mock_workflow_func = Mock()
        mock_workflow = Mock()
        mock_workflow.invoke = Mock(return_value=mock_result)
        mock_workflow_func.return_value = mock_workflow
        mock_get_workflow.return_value = mock_workflow_func

        result = runner.invoke(cli, ['analyze', '600519', '--verbose'], catch_exceptions=False)

        print(f"Exit code: {result.exit_code}")
        print(f"Output length: {len(result.output)}")

        if result.exception:
            print(f"Exception: {result.exception}")
            import traceback
            traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

        if result.exit_code != 0:
            print("Output:")
            print(result.output)

if __name__ == '__main__':
    debug_verbose()
