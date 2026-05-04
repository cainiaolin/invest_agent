"""分析股票命令"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import List, Dict, Any, Optional

console = Console()

# 延迟导入依赖
def _get_tushare_service():
    try:
        from app.services.tushare_service import TushareService
        return TushareService
    except ImportError:
        return None

def _get_workflow():
    try:
        from app.graph.workflow import create_investment_workflow
        return create_investment_workflow
    except ImportError:
        return None


@click.command()
@click.argument("stock_code", required=True)
@click.option(
    "--mode",
    type=click.Choice(["parallel", "vote", "debate"], case_sensitive=False),
    default="parallel",
    help="协作模式: parallel(并行) | vote(投票) | debate(辩论)",
)
@click.option(
    "--agents",
    default="all",
    help="指定Agent(逗号分隔)如: buffet,graham 或 all表示全部",
)
@click.option("--verbose", "-v", is_flag=True, help="显示详细分析信息")
def analyze(stock_code: str, mode: str, agents: str, verbose: bool):
    """
    分析指定股票

    STOCK_CODE: 股票代码，如 600519

    示例:
      invest-agent analyze 600519
      invest-agent analyze 600519 --mode vote
      invest-agent analyze 600519 --agents buffet,graham -v
    """
    try:
        # 显示开始信息
        console.print(
            f"\n[bold cyan]* 开始分析[/bold cyan] [bold yellow]{stock_code}[/bold yellow]\n"
        )

        # 获取股票数据
        stock_data = _fetch_stock_data(stock_code)
        if not stock_data:
            from rich.text import Text
            error_text = Text()
            error_text.append(f"错误：无法获取股票 {stock_code} 的数据", style="red")
            console.print(error_text)
            return

        # 显示股票基本信息
        _display_stock_info(stock_data)

        # 解析agents参数
        selected_agents = _parse_agents(agents)

        # 构建工作流输入状态
        initial_state = {
            "stock_code": stock_code,
            "mode": mode,
            "user_request": f"分析股票 {stock_code}",
            "stock_data": stock_data,
            "selected_agents": selected_agents,
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # 执行工作流
        workflow_creator = _get_workflow()
        if not workflow_creator:
            from rich.text import Text
            error_text = Text()
            error_text.append("错误：工作流模块不可用", style="red")
            console.print(error_text)
            return

        with console.status("[bold yellow]智能体分析中..."):
            workflow = workflow_creator()
            result = workflow.invoke(initial_state)

        # 检查错误
        if result.get("error"):
            from rich.text import Text
            error_text = Text()
            error_text.append(f"分析失败：{result['error']}", style="red")
            console.print(error_text)
            return

        # 显示分析结果
        _display_analysis_results(result, verbose)

    except Exception as e:
        # 使用text参数避免markup解析问题
        from rich.text import Text
        error_text = Text()
        error_text.append(f"\n分析失败：{str(e)}", style="red")
        console.print(error_text)
        if verbose:
            import traceback
            try:
                console.print(traceback.format_exc())
            except:
                error_text = Text()
                error_text.append("无法显示详细错误信息", style="red")
                console.print(error_text)
        raise  # Re-raise for testing


def _fetch_stock_data(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取股票数据

    Args:
        stock_code: 股票代码

    Returns:
        股票数据字典，失败返回None
    """
    try:
        ServiceClass = _get_tushare_service()
        if not ServiceClass:
            from rich.text import Text
            warning_text = Text()
            warning_text.append("警告：Tushare服务不可用", style="yellow")
            console.print(warning_text)
            return None

        service = ServiceClass()
        return service.get_stock_data(stock_code)
    except Exception as e:
        from rich.text import Text
        warning_text = Text()
        warning_text.append(f"警告：获取股票数据失败 - {str(e)}", style="yellow")
        console.print(warning_text)
        return None


def _parse_agents(agents_str: str) -> List[str]:
    """
    解析agents参数

    Args:
        agents_str: 逗号分隔的agent字符串

    Returns:
        Agent名称列表
    """
    if agents_str.lower() == "all":
        # 返回所有agent
        return [
            "Warren Buffett",
            "Benjamin Graham",
            "Philip Fisher",
            "Peter Lynch",
            "George Soros",
            "Ray Dalio",
        ]
    else:
        # 解析用户指定的agent
        agent_mapping = {
            "buffet": "Warren Buffett",
            "graham": "Benjamin Graham",
            "fisher": "Philip Fisher",
            "lynch": "Peter Lynch",
            "soros": "George Soros",
            "dalio": "Ray Dalio",
        }

        selected = []
        for agent_key in agents_str.lower().split(","):
            agent_key = agent_key.strip()
            if agent_key in agent_mapping:
                selected.append(agent_mapping[agent_key])
            else:
                from rich.text import Text
                warning_text = Text()
                warning_text.append(f"警告：未知的agent '{agent_key}'，已忽略", style="yellow")
                console.print(warning_text)

        return selected if selected else ["all"]


def _display_stock_info(stock_data: Dict[str, Any]):
    """
    显示股票基本信息

    Args:
        stock_data: 股票数据字典
    """
    info_table = Table(show_header=False, box=None)
    info_table.add_column("字段", style="cyan", width=12)
    info_table.add_column("值", style="white")

    info_table.add_row("股票代码", stock_data.get("symbol", "N/A"))
    info_table.add_row("股票名称", stock_data.get("name", "N/A"))
    info_table.add_row("当前价格", f"¥{stock_data.get('price', 0):.2f}")

    # 显示关键财务指标
    metrics = stock_data.get("metrics", {})
    if metrics:
        info_table.add_row("", "")  # 空行
        info_table.add_row("[bold]财务指标[/bold]", "", "")
        if "pe_ratio" in metrics:
            info_table.add_row("市盈率(PE)", f"{metrics['pe_ratio']:.2f}")
        if "pb_ratio" in metrics:
            info_table.add_row("市净率(PB)", f"{metrics['pb_ratio']:.2f}")
        if "roe" in metrics:
            info_table.add_row("ROE", f"{metrics['roe']:.2f}%")
        if "revenue_growth" in metrics:
            info_table.add_row("营收增长", f"{metrics['revenue_growth']:.2f}%")
        if "net_profit_growth" in metrics:
            info_table.add_row("净利润增长", f"{metrics['net_profit_growth']:.2f}%")

    console.print(Panel(info_table, title="股票信息", border_style="blue"))


def _display_analysis_results(result: Dict[str, Any], verbose: bool):
    """
    显示分析结果

    Args:
        result: 工作流返回结果
        verbose: 是否显示详细信息
    """
    # 1. 显示各Agent的分析结果表格
    agent_analyses = result.get("agent_analyses", [])
    if agent_analyses:
        _display_agents_table(agent_analyses)

    # 2. 显示最终决策
    final_decision = result.get("final_decision")
    if final_decision:
        _display_final_decision(final_decision)

    # 3. 详细模式：显示各Agent的详细分析
    if verbose and agent_analyses:
        _display_detailed_analyses(agent_analyses)


def _display_agents_table(agent_analyses: List[Dict[str, Any]]):
    """
    显示Agent分析结果表格

    Args:
        agent_analyses: Agent分析结果列表
    """
    table = Table(title="\n[bold]Agent分析结果[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("类型", style="blue", width=10)
    table.add_column("决策", style="bold", width=8)
    table.add_column("置信度", style="yellow", width=10)
    table.add_column("关键观点", style="white", width=40)

    # 决策颜色和图标映射 - 使用文字避免Windows GBK编码问题
    decision_style = {
        "buy": {"style": "green", "icon": "[UP]"},
        "sell": {"style": "red", "icon": "[DOWN]"},
        "hold": {"style": "yellow", "icon": "[HOLD]"},
    }

    for analysis in agent_analyses:
        agent_name = analysis.get("agent_name", "Unknown")
        agent_type = analysis.get("agent_type", "unknown")
        action = analysis.get("action", "hold")
        confidence = analysis.get("confidence", 0.0)
        reasoning = analysis.get("reasoning", "")

        # 截取reasoning前30个字符作为关键观点
        key_point = reasoning[:30] + "..." if len(reasoning) > 30 else reasoning

        style_info = decision_style.get(action.lower(), decision_style["hold"])
        action_display = f"[{style_info['style']}]{action.upper()}[/{style_info['style']}]"

        table.add_row(
            agent_name,
            agent_type.capitalize(),
            action_display,
            f"{confidence:.1%}",
            key_point,
        )

    console.print(table)


def _display_final_decision(decision: Dict[str, Any]):
    """
    显示最终决策

    Args:
        decision: 最终决策字典
    """
    action = decision.get("action", "hold")
    consensus = decision.get("consensus", 0.0)
    summary = decision.get("summary", "")
    participating_agents = decision.get("participating_agents", [])

    # 决策颜色和图标
    decision_info = {
        "buy": {"style": "green", "icon": "[UP]", "text": "建议买入"},
        "sell": {"style": "red", "icon": "[DOWN]", "text": "建议卖出"},
        "hold": {"style": "yellow", "icon": "[HOLD]", "text": "建议持有"},
    }

    info = decision_info.get(action.lower(), decision_info["hold"])

    # 构建决策面板内容
    content = f"""
[{info['style']}]{info['icon']} {info['text'].upper()}[/{info['style']}]

共识度: {consensus:.1%}

参与Agent: {', '.join(participating_agents)}

{summary}
"""

    console.print(Panel(content, title="最终决策", border_style=info['style']))


def _display_detailed_analyses(agent_analyses: List[Dict[str, Any]]):
    """
    显示详细分析信息

    Args:
        agent_analyses: Agent分析结果列表
    """
    from rich.text import Text
    title = Text()
    title.append("\n", style="")
    title.append("详细分析", style="bold cyan")
    title.append("\n", style="")
    console.print(title)

    for i, analysis in enumerate(agent_analyses, 1):
        agent_name = analysis.get("agent_name", "Unknown")
        agent_type = analysis.get("agent_type", "unknown")
        action = analysis.get("action", "hold")
        confidence = analysis.get("confidence", 0.0)
        reasoning = analysis.get("reasoning", "")
        key_metrics = analysis.get("key_metrics", {})

        # 决策样式
        decision_style = {
            "buy": "green",
            "sell": "red",
            "hold": "yellow",
        }.get(action.lower(), "white")

        # 构建详细分析内容
        content = f"""
[bold cyan]Agent:[/bold cyan] {agent_name}
[bold cyan]类型:[/bold cyan] {agent_type.capitalize()}
[bold cyan]决策:[/bold cyan] [{decision_style}]{action.upper()}[/{decision_style}]
[bold cyan]置信度:[/bold cyan] {confidence:.1%}

[bold yellow]分析理由:[/bold yellow]
{reasoning}
"""

        # 显示关键指标
        if key_metrics:
            content += "\n[bold yellow]关键指标:[/bold yellow]\n"
            for key, value in key_metrics.items():
                if key != "scores":  # 跳过详细的scores字典
                    try:
                        content += f"  - {key}: {value}\n"
                    except:
                        content += f"  - {key}: (unable to display value)\n"

        console.print(Panel(content, title=f"{i}. {agent_name}", border_style="cyan"))
        console.print()
