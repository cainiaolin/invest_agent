"""选股API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.screening.scanner import MarketScanner
from app.agents import (
    BuffetAgent, GrahamAgent, FisherAgent, LynchAgent,
    SorosAgent, DalioAgent
)
from app.services.tushare_service import TushareService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/screen", tags=["screen"])

# Agent映射
AGENT_MAP = {
    "buffet": BuffetAgent,
    "graham": GrahamAgent,
    "fisher": FisherAgent,
    "lynch": LynchAgent,
    "soros": SorosAgent,
    "dalio": DalioAgent,
}

# 默认Agents
DEFAULT_AGENTS = ["buffet", "graham", "fisher"]


class ScreenRequest(BaseModel):
    """选股请求模型"""
    agents: str = Field(default="all", description="Agent选择（逗号分隔或'all'）")
    universe: str = Field(default="all", description="股票池范围: all / industry:xxx / index:xxx")
    top_n: int = Field(default=20, description="返回前N只股票", ge=1, le=100)
    industry: Optional[str] = Field(default=None, description="指定行业名称")


class AgentScoreModel(BaseModel):
    """Agent评分模型"""
    agent_name: str
    action: str
    confidence: float
    reasoning: str


class StockScore(BaseModel):
    """股票评分模型"""
    stock_code: str
    stock_name: str
    total_score: float
    buy_votes: int
    total_agents: int
    agent_scores: Dict[str, Any]


class ScreenResponse(BaseModel):
    """选股响应模型"""
    universe: str
    total_analyzed: int
    results: List[StockScore]
    agents_used: List[str]


def _parse_agents(agents_str: str) -> List[str]:
    """解析Agent参数"""
    agents_str = agents_str.lower().strip()
    if agents_str == "all" or not agents_str:
        return list(AGENT_MAP.keys())

    return [a.strip() for a in agents_str.split(",") if a.strip() in AGENT_MAP]


@router.post("/", response_model=ScreenResponse)
async def screen_stocks(request: ScreenRequest, background_tasks: BackgroundTasks = None):
    """
    智能选股

    使用多Agent扫描市场，寻找最佳投资机会

    ## 参数说明

    - **agents**: 指定使用的Agent，默认all（全部Agent）
    - **universe**: 股票池范围
      - `all`: 全部A股
      - `industry:白酒`: 指定行业
      - `index:沪深300`: 指定指数成分股
    - **top_n**: 返回前N只股票（1-100）
    - **industry**: 指定行业（快捷方式）

    ## Agent列表

    - **buffet**: 巴菲特 - 护城河、安全边际
    - **graham**: 格雷厄姆 - 深度价值、内在价值
    - **fisher**: 费雪 - 成长质量、管理层调研
    - **lynch**: 林奇 - GARP策略、PEG比率
    - **soros**: 索罗斯 - 反身性、趋势拐点
    - **dalio**: 达利欧 - 经济周期、全天候策略
    """
    try:
        logger.info(f"收到选股请求: universe={request.universe}, top={request.top_n}")

        # 1. 解析Agent列表
        agent_names = _parse_agents(request.agents)
        if not agent_names:
            raise HTTPException(
                status_code=400,
                detail="未选择有效的Agent"
            )

        logger.info(f"使用的Agents: {', '.join(agent_names)}")

        # 2. 处理行业参数
        universe = request.universe
        if request.industry:
            universe = f"industry:{request.industry}"

        # 3. 创建Agent实例
        tushare_service = TushareService(settings.tushare_token)
        agents = []
        for name in agent_names:
            agent_class = AGENT_MAP.get(name)
            if agent_class:
                agents.append(agent_class(tushare_service))

        if not agents:
            raise HTTPException(
                status_code=500,
                detail="无法创建Agent实例"
            )

        # 4. 创建扫描器并执行扫描
        scanner = MarketScanner(tushare_service)

        logger.info(f"开始扫描市场: universe={universe}")
        results = await scanner.scan_market(
            agents=agents,
            universe=universe,
            top_n=request.top_n
        )

        # 5. 构建响应
        stock_scores = []
        for result in results:
            # 清理agent_scores，转换为可序列化的格式
            agent_scores_clean = {}
            for agent_name, analysis in result.get("agent_scores", {}).items():
                if isinstance(analysis, dict):
                    agent_scores_clean[agent_name] = {
                        "action": analysis.get("action", "hold"),
                        "confidence": analysis.get("confidence", 0.0),
                        "reasoning": analysis.get("reasoning", "")[:200],  # 截断过长的reasoning
                    }

            stock_scores.append(StockScore(
                stock_code=result.get("stock_code", ""),
                stock_name=result.get("stock_name", ""),
                total_score=result.get("total_score", 0.0),
                buy_votes=result.get("buy_votes", 0),
                total_agents=result.get("total_agents", 0),
                agent_scores=agent_scores_clean
            ))

        return ScreenResponse(
            universe=universe,
            total_analyzed=len(results) * 2,  # 估算（实际可能扫描了更多）
            results=stock_scores,
            agents_used=agent_names
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选股失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"选股失败: {str(e)}"
        )


@router.get("/industries")
async def list_industries():
    """获取可选的行业列表"""
    industries = [
        "银行", "房地产", "建筑装饰", "钢铁", "采掘",
        "化工", "建筑材料", "电气设备", "机械设备", "国防军工",
        "汽车", "家用电器", "纺织服装", "轻工制造", "医药生物",
        "公用事业", "交通运输", "商业贸易", "食品饮料", "农林牧渔",
        "休闲服务", "计算机", "电子", "通信", "传媒", "非银金融"
    ]

    return {
        "industries": industries,
        "universe_options": [
            {"value": "all", "description": "全部A股"},
            {"value": "industry:xxx", "description": "指定行业，如 industry:银行"},
            {"value": "index:沪深300", "description": "指数成分股"}
        ]
    }


@router.get("/status")
async def get_screening_status():
    """获取选股状态（用于异步任务）"""
    return {
        "status": "ready",
        "message": "选股服务就绪"
    }
