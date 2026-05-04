"""投资智能体系统CLI入口"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from app.core.config import settings
from app.cli.commands.analyze import analyze
from app.cli.commands.screen import screen
from app.cli.commands.backtest import backtest

console = Console()


@click.group()
@click.version_option(version="0.3.0-beta")
def cli():
    """
    投资智能体系统

    基于LangGraph+Tushare的多Agent投资分析工具
    """
    pass


# 添加子命令
cli.add_command(analyze)
cli.add_command(screen)
cli.add_command(backtest)


@cli.command()
@click.option("--show-token", is_flag=True, help="显示Token（部分隐藏）")
def config(show_token: bool):
    """
    查看和验证配置

    检查环境变量和系统配置状态
    """
    console.print("\n:gear: 系统配置\n")

    # 创建配置表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    table.add_column("状态", style="yellow")

    # Tushare Token
    token_value = settings.tushare_token
    if show_token:
        token_display = token_value
    else:
        token_display = f"{token_value[:8]}...{token_value[-4:]}" if token_value else "未设置"
    token_status = ":white_check_mark:" if token_value else ":x:"

    table.add_row("Tushare Token", token_display, token_status)
    table.add_row("日志级别", settings.log_level, ":white_check_mark:")
    table.add_row("缓存TTL", f"{settings.cache_ttl}秒", ":white_check_mark:")

    console.print(table)

    # 测试连接
    console.print("\n:satellite: 测试Tushare连接...")
    try:
        from app.services.tushare_service import TushareService

        service = TushareService()
        # 尝试获取一条简单数据来验证连接
        test_data = service.get_stock_data("600000")
        if test_data:
            console.print("[green]:white_check_mark: 连接成功[/green]")
        else:
            console.print("[yellow]:warning: 连接成功但无数据[/yellow]")
    except Exception as e:
        console.print(f"[red]:x: 连接失败: {str(e)}[/red]")


@cli.command()
def version():
    """显示版本信息"""
    console.print("\n:information_source: 版本信息\n")

    version_info = """
[bold cyan]投资智能体系统[/bold cyan]
版本: [bold green]0.1.0-alpha[/bold green]

[bold]特性[/bold]
  • 多Agent投资分析
  • Tushare数据集成
  • 价值/成长/宏观投资策略
  • LangGraph工作流协作
  • CLI交互界面

[bold]技术栈[/bold]
  • Python 3.11+
  • LangGraph
  • Click
  • Rich
  • Pydantic
"""
    console.print(version_info)


if __name__ == "__main__":
    cli()
