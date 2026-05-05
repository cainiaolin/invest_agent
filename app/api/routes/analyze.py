"""股票分析API路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.graph.workflow import create_investment_workflow
from app.agents import (
    BuffetAgent, GrahamAgent, FisherAgent, LynchAgent,
    SorosAgent, DalioAgent
)
from app.services.tushare_service import TushareService
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])

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


async def _get_stock_data_async(stock_code: str) -> dict:
    """异步获取股票数据（用于兼容旧Agent接口）"""
    return {
        "symbol": stock_code,
        "name": f"股票{stock_code}",
        "metrics": {
            "pe_ratio": 15.0,
            "pb_ratio": 2.5,
            "roe": 18.0,
            "debt_ratio": 35.0,
            "current_ratio": 1.8,
            "dividend_yield": 2.5,
            "revenue_growth": 12.0,
            "profit_growth": 15.0,
        },
        "moat_indicators": {
            "brand_strength": 7,
            "market_share": 25.0,
            "competitive_advantage": True,
        }
    }


class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    stock_code: str = Field(..., description="股票代码（6位数字）", min_length=6, max_length=6)
    mode: str = Field(default="parallel", description="协作模式: parallel/vote/debate")
    agents: Optional[str] = Field(default=None, description="指定Agent（逗号分隔，如buffet,graham）")
    verbose: bool = Field(default=False, description="详细输出")
    agent_mode: str = Field(default="rule", description="Agent模式: rule/ai/hybrid")
    llm_config: Optional["LLMConfigModel"] = Field(default=None, description="LLM配置")


class LLMConfigModel(BaseModel):
    """LLM配置模型"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-4o", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API Base URL（用于DeepSeek/GLM等）")
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=4000, ge=100, le=8000)


class AgentAnalysisModel(BaseModel):
    """Agent分析结果模型"""
    agent_name: str
    agent_type: str
    action: str
    confidence: float
    reasoning: str
    key_metrics: Dict[str, Any]
    price_target: Optional[float]
    analysis_mode: Optional[str] = Field(default=None, description="分析模式: rule/ai_llm/rule_fallback")
    thought_process: Optional[Dict[str, Any]] = Field(default=None, description="思维链过程")
    llm_model: Optional[str] = Field(default=None, description="使用的LLM模型")
    validation_warning: Optional[str] = Field(default=None, description="验证警告")


class FinalDecisionModel(BaseModel):
    """最终决策模型"""
    action: str
    consensus: float
    summary: str


class StockInfo(BaseModel):
    """股票实时数据（来自 Tushare）"""
    stock_name: str = ""
    trade_date: str = ""
    close: float = 0.0
    pe_ttm: float = 0.0
    pb: float = 0.0
    total_mv: float = 0.0
    circ_mv: float = 0.0
    turnover_rate: float = 0.0
    volume_ratio: float = 0.0


class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    stock_code: str
    mode: str
    agent_analyses: List[AgentAnalysisModel]
    final_decision: Optional[FinalDecisionModel]
    formatted_output: Optional[str]
    error: Optional[str] = None
    stock_info: Optional[StockInfo] = None


def _parse_agents(agents_str: Optional[str]) -> List[str]:
    """解析Agent参数"""
    if not agents_str:
        return DEFAULT_AGENTS

    agents_str = agents_str.lower().strip()
    if agents_str == "all":
        return list(AGENT_MAP.keys())

    return [a.strip() for a in agents_str.split(",") if a.strip() in AGENT_MAP]


def _get_agent_type(agent_name: str) -> str:
    """获取Agent类型"""
    if agent_name in ["buffet", "graham"]:
        return "value"
    elif agent_name in ["fisher", "lynch"]:
        return "growth"
    elif agent_name in ["soros", "dalio"]:
        return "macro"
    return "unknown"


@router.post("/", response_model=AnalyzeResponse)
async def analyze_stock(request: AnalyzeRequest):
    """
    分析单个股票

    通过多Agent协作分析股票，提供投资建议

    ## 协作模式

    - **parallel**: 并行独立分析，所有Agent同时工作
    - **vote**: 投票决策制，多数Agent同意才执行
    - **debate**: 辩论仲裁制，Agent进行多轮辩论

    ## Agent列表

    - **buffet**: 巴菲特 - 护城河、安全边际
    - **graham**: 格雷厄姆 - 深度价值、内在价值
    - **fisher**: 费雪 - 成长质量、管理层调研
    - **lynch**: 林奇 - GARP策略、PEG比率
    - **soros**: 索罗斯 - 反身性、趋势拐点
    - **dalio**: 达利欧 - 经济周期、全天候策略
    """
    try:
        logger.info(f"收到分析请求: {request.stock_code}, mode={request.mode}")

        # 1. 验证mode
        valid_modes = ["parallel", "vote", "debate"]
        if request.mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"无效的协作模式: {request.mode}。支持的模式: {', '.join(valid_modes)}"
            )

        # 2. 解析Agent列表
        agent_names = _parse_agents(request.agents)
        if not agent_names:
            raise HTTPException(
                status_code=400,
                detail="未选择有效的Agent"
            )

        logger.info(f"使用的Agents: {', '.join(agent_names)}")

        # 3. 创建Agent实例
        tushare_service = TushareService(settings.tushare_token)

        # 3a. 获取 Tushare 实时股票数据
        stock_info = None
        try:
            daily_data = await tushare_service.get_daily_basic(request.stock_code)
            daily_df = daily_data.get("daily_basic")
            if daily_df is not None and not daily_df.empty:
                latest = daily_df.iloc[0]
                stock_info = StockInfo(
                    stock_name=f"{request.stock_code}",
                    trade_date=str(latest.get("trade_date", "")),
                    close=float(latest.get("close", 0)),
                    pe_ttm=float(latest.get("pe_ttm", 0) or 0),
                    pb=float(latest.get("pb", 0) or 0),
                    total_mv=float(latest.get("total_mv", 0) or 0),
                    circ_mv=float(latest.get("circ_mv", 0) or 0),
                    turnover_rate=float(latest.get("turnover_rate", 0) or 0),
                    volume_ratio=float(latest.get("volume_ratio", 0) or 0),
                )
        except Exception as e:
            logger.warning(f"获取Tushare实时数据失败", exc_info=True)

        # 3b. 初始化AI模式相关服务
        llm_service = None
        knowledge_service = None

        if request.agent_mode in ["ai", "hybrid"]:
            from app.services.llm_service import LLMService
            from app.services.knowledge_service import KnowledgeService

            # 构建LLM配置
            llm_config_dict = None
            if request.llm_config:
                # 使用前端提供的配置
                provider = request.llm_config.provider
                default_api_key = None
                if provider == "openai":
                    default_api_key = settings.openai_api_key
                elif provider == "anthropic":
                    default_api_key = settings.anthropic_api_key
                elif provider == "deepseek":
                    default_api_key = settings.deepseek_api_key
                elif provider == "glm":
                    default_api_key = settings.glm_api_key

                llm_config_dict = {
                    "provider": provider,
                    "model": request.llm_config.model,
                    "api_key": request.llm_config.api_key or default_api_key,
                    "base_url": request.llm_config.base_url,
                    "temperature": request.llm_config.temperature,
                    "max_tokens": request.llm_config.max_tokens
                }
            else:
                # 使用.env中的默认配置
                llm_config_dict = {
                    "provider": settings.llm_provider,
                    "model": settings.llm_model,
                    "api_key": None  # LLMService会从settings获取
                }

            llm_service = LLMService(llm_config_dict)
            knowledge_service = KnowledgeService(settings.knowledge_base_path)

        # 3c. 使用get_agent函数创建Agent
        from app.agents import get_agent

        agents = []
        for name in agent_names:
            if request.agent_mode == "ai":
                logger.info(f"创建AI Agent: {name}, mode={request.agent_mode}")
                agent = get_agent(
                    name,
                    mode="ai",
                    tushare_service=tushare_service,
                    llm_service=llm_service,
                    knowledge_service=knowledge_service
                )
                logger.info(f"AI Agent创建成功: {agent.__class__.__name__}")
            else:
                agent = get_agent(
                    name,
                    mode="rule",
                    tushare_service=tushare_service
                )
            agents.append(agent)

        if not agents:
            raise HTTPException(
                status_code=500,
                detail="无法创建Agent实例"
            )

        # 4. 直接调用Agent进行分析（不使用LangGraph工作流）
        from app.core.state import AnalysisState
        import inspect

        # 为每个Agent创建分析状态并执行分析
        agent_analyses_models = []
        final_decision = None

        for agent in agents:
            try:
                logger.info(f"开始分析，Agent: {agent.name}, class: {agent.__class__.__name__}")
                state = AnalysisState(
                    stock_code=request.stock_code,
                    mode=request.mode,
                    user_request="分析此股票的投资价值",
                    agent_analyses=[],
                    debate_round=0,
                    debate_history=[],
                    final_decision=None,
                    error=None
                )

                # 检查analyze方法是否是async的
                if inspect.iscoroutinefunction(agent.analyze):
                    analysis_result = await agent.analyze(state)
                else:
                    # 如果不是async，同步调用但传入stock_data（兼容旧接口）
                    stock_data = await _get_stock_data_async(request.stock_code)
                    analysis_result = agent.analyze(stock_data)
                    # 确保返回值包含agent_name
                    if "agent_name" not in analysis_result:
                        analysis_result["agent_name"] = agent.name

                # 安全提取key_metrics
                key_metrics_raw = analysis_result.get("key_metrics", {})
                if isinstance(key_metrics_raw, dict):
                    key_metrics = key_metrics_raw
                else:
                    # 如果是列表或其他类型，转换为空字典
                    logger.warning(f"Agent {agent.name} 返回的key_metrics类型错误: {type(key_metrics_raw)}")
                    key_metrics = {}

                agent_analysis = AgentAnalysisModel(
                    agent_name=agent.name,
                    agent_type=_get_agent_type(agent.name),
                    action=analysis_result.get("action", "hold"),
                    confidence=float(analysis_result.get("confidence", 0.0)),
                    reasoning=str(analysis_result.get("reasoning", "")),
                    key_metrics=key_metrics,
                    price_target=analysis_result.get("price_target"),
                    analysis_mode=analysis_result.get("analysis_mode"),
                    thought_process=analysis_result.get("thought_process"),
                    llm_model=analysis_result.get("llm_model"),
                    validation_warning=analysis_result.get("validation_warning")
                )
                agent_analyses_models.append(agent_analysis)

            except Exception as e:
                logger.error(f"Agent {agent.name} 构建响应失败: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                # 添加一个失败的分析记录
                agent_analyses_models.append(AgentAnalysisModel(
                    agent_name=agent.name,
                    agent_type=_get_agent_type(agent.name),
                    action="hold",
                    confidence=0.0,
                    reasoning=f"分析失败: {str(e)}",
                    key_metrics={},
                    price_target=None
                ))
                continue

        # 根据mode计算最终决策
        if request.mode == "vote" and agent_analyses_models:
            # 投票模式：多数决定
            buy_votes = sum(1 for a in agent_analyses_models if a.action == "buy")
            sell_votes = sum(1 for a in agent_analyses_models if a.action == "sell")
            total = len(agent_analyses_models)

            if buy_votes > total / 2:
                action = "buy"
            elif sell_votes > total / 2:
                action = "sell"
            else:
                action = "hold"

            consensus = max(buy_votes, sell_votes) / total if total > 0 else 0

            final_decision = FinalDecisionModel(
                action=action,
                consensus=consensus,
                summary=f"投票结果: {buy_votes}票买入, {sell_votes}票卖出, {total - buy_votes - sell_votes}票持有"
            )
        elif request.mode == "parallel" and agent_analyses_models:
            # 并行模式：综合建议
            buy_count = sum(1 for a in agent_analyses_models if a.action == "buy")
            avg_confidence = sum(a.confidence for a in agent_analyses_models) / len(agent_analyses_models)

            if buy_count >= len(agent_analyses_models) / 2 and avg_confidence > 0.6:
                action = "buy"
                summary = f"多个Agent建议买入，平均置信度{avg_confidence:.1%}"
            else:
                action = "hold"
                summary = "Agent意见分歧较大，建议谨慎观察"

            final_decision = FinalDecisionModel(
                action=action,
                consensus=avg_confidence,
                summary=summary
            )

        result = {
            "agent_analyses": agent_analyses_models,
            "final_decision": final_decision,
            "formatted_output": None,
            "error": None
        }

        # 5. 构建响应
        return AnalyzeResponse(
            stock_code=request.stock_code,
            mode=request.mode,
            agent_analyses=result["agent_analyses"],
            final_decision=result["final_decision"],
            formatted_output=result.get("formatted_output"),
            error=None,
            stock_info=stock_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/agents")
async def list_agents():
    """获取可用的Agent列表"""
    agents = [
        {
            "name": "buffet",
            "display_name": "巴菲特",
            "type": "value",
            "style": "价值投资 - 护城河、安全边际、长期持有",
            "key_metrics": ["护城河评分", "安全边际", "ROE质量"],
        },
        {
            "name": "graham",
            "display_name": "格雷厄姆",
            "type": "value",
            "style": "深度价值投资 - 安全边际、内在价值",
            "key_metrics": ["内在价值", "安全边际", "Net-Net"],
        },
        {
            "name": "fisher",
            "display_name": "费雪",
            "type": "growth",
            "style": "成长投资 - 质量成长、管理层调研",
            "key_metrics": ["成长质量", "管理层", "研发投入"],
        },
        {
            "name": "lynch",
            "display_name": "林奇",
            "type": "growth",
            "style": "GARP策略 - 合理价格成长",
            "key_metrics": ["PEG比率", "快速增长", "熟悉领域"],
        },
        {
            "name": "soros",
            "display_name": "索罗斯",
            "type": "macro",
            "style": "宏观对冲 - 反身性、趋势拐点",
            "key_metrics": ["反身性", "市场情绪", "趋势拐点"],
        },
        {
            "name": "dalio",
            "display_name": "达利欧",
            "type": "macro",
            "style": "全天候策略 - 经济周期、债务周期",
            "key_metrics": ["经济周期", "债务周期", "通胀率"],
        }
    ]

    return {
        "agents": agents,
        "default_agents": DEFAULT_AGENTS,
        "modes": [
            {"value": "parallel", "description": "并行独立分析"},
            {"value": "vote", "description": "投票决策制"},
            {"value": "debate", "description": "辩论仲裁制"}
        ]
    }
