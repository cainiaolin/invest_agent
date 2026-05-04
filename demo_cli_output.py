"""Demo script to showcase CLI analyze command output"""
import sys
sys.path.insert(0, 'E:/claude code/invest_agent/invest_agent_by_graph')

from click.testing import CliRunner
from unittest.mock import Mock, patch
import json

def create_mock_data():
    """Create realistic mock data for demonstration"""
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
        }
    }

def create_mock_workflow_result():
    """Create realistic workflow result"""
    return {
        "agent_analyses": [
            {
                "agent_name": "Warren Buffett",
                "agent_type": "value",
                "action": "buy",
                "confidence": 0.85,
                "reasoning": "贵州茅台是优质消费品公司，具有强大的品牌护城河和定价能力。当前估值合理，长期持有价值显著。",
                "key_metrics": {"total_score": 85},
                "price_target": None,
            },
            {
                "agent_name": "Peter Lynch",
                "agent_type": "growth",
                "action": "buy",
                "confidence": 0.78,
                "reasoning": "公司保持稳定的营收增长，在高端白酒市场具有领先地位。成长性良好，值得长期投资。",
                "key_metrics": {"total_score": 78},
                "price_target": None,
            },
            {
                "agent_name": "Benjamin Graham",
                "agent_type": "value",
                "action": "hold",
                "confidence": 0.65,
                "reasoning": "当前价格略高于内在价值评估，建议等待更好的买入时机。关注安全边际。",
                "key_metrics": {"total_score": 65},
                "price_target": None,
            },
        ],
        "final_decision": {
            "action": "buy",
            "consensus": 0.76,
            "participating_agents": ["Warren Buffett", "Peter Lynch", "Benjamin Graham"],
            "summary": "多数投资大师建议买入，公司基本面优秀，具有长期投资价值。Graham建议关注估值安全边际。",
        },
        "error": None,
    }

def demo_basic_analyze():
    """Demo basic analyze command"""
    print("=" * 80)
    print("Demo 1: Basic Analyze Command")
    print("=" * 80)

    from app.cli.main import cli
    runner = CliRunner()

    mock_stock_data = create_mock_data()
    mock_workflow_result = create_mock_workflow_result()

    with patch('app.cli.commands.analyze._get_tushare_service') as mock_get_service, \
         patch('app.cli.commands.analyze._get_workflow') as mock_get_workflow:

        mock_service_class = Mock()
        mock_service = Mock()
        mock_service.get_stock_data = Mock(return_value=mock_stock_data)
        mock_service_class.return_value = mock_service
        mock_get_service.return_value = mock_service_class

        mock_workflow_func = Mock()
        mock_workflow = Mock()
        mock_workflow.invoke = Mock(return_value=mock_workflow_result)
        mock_workflow_func.return_value = mock_workflow
        mock_get_workflow.return_value = mock_workflow_func

        result = runner.invoke(cli, ['analyze', '600519'])

        # Save output to file to avoid encoding issues
        with open('cli_demo_output.txt', 'w', encoding='utf-8') as f:
            f.write(result.output)

        print("Command executed successfully!")
        print(f"Output length: {len(result.output)} characters")
        print("\nOutput saved to: cli_demo_output.txt")
        print("\nPreview of output:")
        print("-" * 80)

        # Print a safe preview
        lines = result.output.split('\n')
        for i, line in enumerate(lines[:20]):
            try:
                print(line)
            except:
                print(f"[Line {i}: encoding issue]")

        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")

def demo_vote_mode():
    """Demo vote mode"""
    print("\n" + "=" * 80)
    print("Demo 2: Vote Mode")
    print("=" * 80)

    from app.cli.main import cli
    runner = CliRunner()

    mock_stock_data = create_mock_data()
    mock_workflow_result = create_mock_workflow_result()

    with patch('app.cli.commands.analyze._get_tushare_service') as mock_get_service, \
         patch('app.cli.commands.analyze._get_workflow') as mock_get_workflow:

        mock_service_class = Mock()
        mock_service = Mock()
        mock_service.get_stock_data = Mock(return_value=mock_stock_data)
        mock_service_class.return_value = mock_service
        mock_get_service.return_value = mock_service_class

        mock_workflow_func = Mock()
        mock_workflow = Mock()
        mock_workflow.invoke = Mock(return_value=mock_workflow_result)
        mock_workflow_func.return_value = mock_workflow
        mock_get_workflow.return_value = mock_workflow_func

        result = runner.invoke(cli, ['analyze', '600519', '--mode', 'vote'])

        print("Vote mode executed successfully!")
        print(f"Exit code: {result.exit_code}")

def demo_specific_agents():
    """Demo with specific agents"""
    print("\n" + "=" * 80)
    print("Demo 3: Specific Agents")
    print("=" * 80)

    from app.cli.main import cli
    runner = CliRunner()

    mock_stock_data = create_mock_data()
    mock_workflow_result = create_mock_workflow_result()

    with patch('app.cli.commands.analyze._get_tushare_service') as mock_get_service, \
         patch('app.cli.commands.analyze._get_workflow') as mock_get_workflow:

        mock_service_class = Mock()
        mock_service = Mock()
        mock_service.get_stock_data = Mock(return_value=mock_stock_data)
        mock_service_class.return_value = mock_service
        mock_get_service.return_value = mock_service_class

        mock_workflow_func = Mock()
        mock_workflow = Mock()
        mock_workflow.invoke = Mock(return_value=mock_workflow_result)
        mock_workflow_func.return_value = mock_workflow
        mock_get_workflow.return_value = mock_workflow_func

        result = runner.invoke(cli, ['analyze', '600519', '--agents', 'buffet,lynch'])

        print("Specific agents mode executed successfully!")
        print(f"Exit code: {result.exit_code}")

def demo_verbose_mode():
    """Demo verbose mode"""
    print("\n" + "=" * 80)
    print("Demo 4: Verbose Mode")
    print("=" * 80)

    from app.cli.main import cli
    runner = CliRunner()

    mock_stock_data = create_mock_data()
    mock_workflow_result = create_mock_workflow_result()

    with patch('app.cli.commands.analyze._get_tushare_service') as mock_get_service, \
         patch('app.cli.commands.analyze._get_workflow') as mock_get_workflow:

        mock_service_class = Mock()
        mock_service = Mock()
        mock_service.get_stock_data = Mock(return_value=mock_stock_data)
        mock_service_class.return_value = mock_service
        mock_get_service.return_value = mock_service_class

        mock_workflow_func = Mock()
        mock_workflow = Mock()
        mock_workflow.invoke = Mock(return_value=mock_workflow_result)
        mock_workflow_func.return_value = mock_workflow
        mock_get_workflow.return_value = mock_workflow_func

        result = runner.invoke(cli, ['analyze', '600519', '--verbose'])

        # Save verbose output
        with open('cli_demo_verbose.txt', 'w', encoding='utf-8') as f:
            f.write(result.output)

        print("Verbose mode executed successfully!")
        print(f"Output length: {len(result.output)} characters")
        print("\nOutput saved to: cli_demo_verbose.txt")

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("CLI ANALYZE COMMAND DEMONSTRATION")
    print("=" * 80)

    try:
        demo_basic_analyze()
        demo_vote_mode()
        demo_specific_agents()
        demo_verbose_mode()

        print("\n" + "=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - cli_demo_output.txt (basic output)")
        print("  - cli_demo_verbose.txt (verbose output)")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
