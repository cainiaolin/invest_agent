"""选股命令"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()


@click.command()
@click.argument("universe", default="all")
@click.option("--agents", default="all", help="指定Agent（逗号分隔或'all'）")
@click.option("--top", default=20, help="返回前N只股票", type=int)
@click.option("--industry", help="指定行业")
def screen(universe: str, agents: str, top: int, industry: str):
    """
    智能选股 - 扫描市场寻找投资机会

    示例:
        invest-agent screen all --agents buffet --top 20
        invest-agent screen industry:白酒 --agents fisher,lynch
    """
    console.print(f"\n:search: 智能选股")
    console.print(f"股票池: {universe}")
    console.print(f"Agent: {agents}")
    console.print(f"Top: {top}\n")

    if industry:
        universe = f"industry:{industry}"

    with console.status("[bold green]正在扫描市场...", spinner="dots"):
        # TODO: 实现实际的选股逻辑
        # 1. 解析Agent选择
        # 2. 调用MarketScanner
        # 3. 显示结果

        # 模拟结果
        results = [
            {
                "stock_code": "600519",
                "stock_name": "贵州茅台",
                "total_score": 92.5,
                "buy_votes": 2,
                "total_agents": 3,
                "agent_scores": {}
            },
            {
                "stock_code": "000858",
                "stock_name": "五粮液",
                "total_score": 88.3,
                "buy_votes": 2,
                "total_agents": 3,
                "agent_scores": {}
            }
        ]

    # 显示结果
    table = Table(title=f"选股结果 (Top {len(results)})")
    table.add_column("排名", style="cyan")
    table.add_column("股票代码", style="bold")
    table.add_column("股票名称")
    table.add_column("综合评分", justify="right", style="green")
    table.add_column("买入票数", justify="right")
    table.add_column("推荐", style="magenta")

    for i, result in enumerate(results, 1):
        # 推荐级别
        if result["total_score"] >= 85:
            recommendation = "🟢 强烈推荐"
        elif result["total_score"] >= 75:
            recommendation = "🟡 推荐"
        else:
            recommendation = "⚪ 观望"

        table.add_row(
            str(i),
            result["stock_code"],
            result["stock_name"],
            f"{result['total_score']:.1f}",
            result["buy_votes"],
            recommendation
        )

    console.print("\n")
    console.print(table)

    # 统计信息
    console.print(f"\n[dim]扫描了 {top*2} 只股票，返回前 {len(results)} 只[/dim]")
