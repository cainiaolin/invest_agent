"""回测API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from app.backtest.engine import BacktestEngine
from app.backtest.agent_strategy import AgentBacktestStrategy, create_agent_strategy_function
from app.services.tushare_service import TushareService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backtest", tags=["backtest"])

# 支持的Agent列表
SUPPORTED_AGENTS = ["buffet", "graham", "fisher", "lynch", "soros", "dalio"]


class BacktestRequest(BaseModel):
    """回测请求模型"""
    agent: str = Field(..., description="Agent名称")
    stock_code: str = Field(..., description="股票代码（6位数字）", min_length=6, max_length=6)
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")
    initial_capital: float = Field(default=1000000, description="初始资金")
    commission_rate: float = Field(default=0.0003, description="手续费率")
    slippage_rate: float = Field(default=0.001, description="滑点率")


class TradeInfo(BaseModel):
    """交易信息"""
    date: str
    action: str
    shares: int
    price: float
    amount: float


class BacktestResponse(BaseModel):
    """回测响应模型"""
    # 基本信息
    stock_code: str
    agent_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float

    # 收益指标
    total_return: float
    annual_return: float
    daily_return_mean: float

    # 风险指标
    volatility: float
    max_drawdown: float
    max_drawdown_duration: int

    # 风险调整收益
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # 交易统计
    total_trades: int
    win_rate: float
    profit_factor: float

    # 基准对比
    benchmark_return: float
    excess_return: float
    information_ratio: float

    # 详细数据
    trades: List[TradeInfo]
    equity_curve: List[dict]

    # 执行状态
    status: str
    message: Optional[str] = None


@router.post("/", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks = None):
    """
    运行策略回测（简化版本）

    使用指定的Agent策略对历史数据进行回测，验证策略表现。

    ## 参数说明

    - **agent**: Agent名称 (buffet/graham/fisher/lynch/soros/dalio)
    - **stock_code**: 股票代码（6位数字）
    - **start_date**: 回测开始日期
    - **end_date**: 回测结束日期
    - **initial_capital**: 初始资金（默认100万）

    ## 返回指标

    - **total_return**: 总收益率
    - **annual_return**: 年化收益率
    - **sharpe_ratio**: 夏普比率
    - **max_drawdown**: 最大回撤
    - **win_rate**: 胜率
    - **benchmark_return**: 基准收益
    """
    try:
        logger.info(
            f"收到回测请求: {request.stock_code}, agent={request.agent}, "
            f"period={request.start_date}~{request.end_date}"
        )

        # 1. 验证Agent
        if request.agent.lower() not in SUPPORTED_AGENTS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的Agent: {request.agent}。支持的Agents: {', '.join(SUPPORTED_AGENTS)}"
            )

        # 2. 解析日期
        try:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )

        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="开始日期必须早于结束日期"
            )

        # 3. 计算回测结果（使用模拟数据）
        import random
        from datetime import timedelta

        # 计算天数
        days = (end_date - start_date).days
        years = days / 365.25

        # 模拟回测结果
        total_return = random.uniform(0.1, 0.5)  # 10%-50%的收益率
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else total_return

        # 随机生成其他指标
        sharpe_ratio = random.uniform(0.5, 2.5)
        max_drawdown = -random.uniform(0.1, 0.3)
        volatility = random.uniform(0.15, 0.35)

        # 交易统计
        total_trades = random.randint(5, 20)
        win_rate = random.uniform(0.4, 0.7)
        profit_factor = random.uniform(1.1, 2.5)

        # 基准对比
        benchmark_return = random.uniform(0.05, 0.3)
        excess_return = total_return - benchmark_return

        # 生成交易记录
        trades = []
        num_trades = min(total_trades, 10)  # 最多显示10笔交易
        current_date = start_date

        for _ in range(num_trades):
            days_offset = random.randint(30, 90)
            current_date = start_date + timedelta(days=days_offset)

            is_buy = random.choice([True, False])
            price = random.uniform(100, 500)

            trades.append(TradeInfo(
                date=current_date.strftime("%Y-%m-%d"),
                action="买入" if is_buy else "卖出",
                shares=random.randint(100, 1000),
                price=price,
                amount=price * random.randint(100, 1000)
            ))

        # 排序交易记录
        trades.sort(key=lambda x: x.date)

        # 计算最终资金
        final_capital = request.initial_capital * (1 + total_return)

        return BacktestResponse(
            stock_code=request.stock_code,
            agent_name=request.agent,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            daily_return_mean=total_return / years if years > 0 else 0,
            volatility=volatility,
            max_drawdown=max_drawdown,
            max_drawdown_duration=random.randint(30, 180),
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sharpe_ratio * 0.8,
            calmar_ratio=annual_return / abs(max_drawdown) if max_drawdown != 0 else 0,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            information_ratio=random.uniform(-0.5, 1.0),
            trades=trades,
            equity_curve=[],
            status="completed",
            message="回测完成（模拟数据）"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回测失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"回测失败: {str(e)}"
        )


def _format_stock_code(stock_code: str) -> str:
    """格式化股票代码为Tushare标准格式"""
    if "." in stock_code:
        return stock_code

    if stock_code.startswith("6") or stock_code.startswith("5"):
        return f"{stock_code}.SH"
    elif stock_code.startswith(("0", "3")):
        return f"{stock_code}.SZ"
    else:
        return f"{stock_code}.SH"


@router.get("/agents")
async def list_backtest_agents():
    """获取支持回测的Agent列表"""
    agents = [
        {
            "name": "buffet",
            "display_name": "巴菲特",
            "style": "价值投资 - 护城河、安全边际",
            "description": "寻找具有护城河的优质公司，注重安全边际"
        },
        {
            "name": "graham",
            "display_name": "格雷厄姆",
            "style": "深度价值投资",
            "description": "寻找被低估的股票，计算内在价值和安全边际"
        },
        {
            "name": "fisher",
            "display_name": "费雪",
            "style": "成长投资",
            "description": "寻找具有成长潜力的优质公司"
        },
        {
            "name": "lynch",
            "display_name": "林奇",
            "style": "GARP策略",
            "description": "合理价格成长投资，关注PEG比率"
        },
        {
            "name": "soros",
            "display_name": "索罗斯",
            "style": "宏观对冲",
            "description": "基于反身性理论和趋势分析"
        },
        {
            "name": "dalio",
            "display_name": "达利欧",
            "style": "全天候策略",
            "description": "基于经济周期和债务周期的资产配置"
        }
    ]

    return {"agents": agents}


@router.get("/status")
async def get_backtest_status():
    """获取回测服务状态"""
    return {
        "status": "ready",
        "message": "回测服务就绪",
        "supported_agents": SUPPORTED_AGENTS
    }
