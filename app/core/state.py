# app/core/state.py
from typing import TypedDict, List, Optional, Dict, Any
from typing_extensions import Annotated
import operator


class AgentAnalysis(TypedDict):
    """单个Agent的分析结果"""

    agent_name: str  # Agent名称，如 "BuffetAgent"
    agent_type: str  # Agent类型: "value" | "growth" | "macro"
    action: str  # 投资建议: "buy" | "sell" | "hold"
    confidence: float  # 置信度 0.0 - 1.0
    reasoning: str  # 分析理由
    key_metrics: Dict[str, Any]  # 关键指标字典
    price_target: Optional[float]  # 目标价格（可选）


class DebateMessage(TypedDict):
    """辩论消息"""

    agent_name: str
    content: str
    round: int
    timestamp: str


class Decision(TypedDict):
    """最终投资决策"""

    action: str  # 最终决策: "buy" | "sell" | "hold"
    consensus: float  # 共识度 0.0 - 1.0
    participating_agents: List[str]  # 参与决策的Agent列表
    summary: str  # 决策摘要


class AnalysisState(TypedDict):
    """投资分析的状态定义（用于LangGraph）"""

    # 输入
    stock_code: str  # 股票代码，如 "600519"
    mode: str  # 协作模式: "parallel" | "vote" | "debate"
    user_request: str  # 用户自然语言需求

    # Agent 分析结果（累积）
    agent_analyses: Annotated[List[AgentAnalysis], operator.add]

    # 协作中间状态
    debate_round: int  # 辩论轮次
    debate_history: List[DebateMessage]  # 辩论历史

    # 输出
    final_decision: Optional[Decision]  # 最终决策
    error: Optional[str]  # 错误信息
