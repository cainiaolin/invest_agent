"""核心模块 - 配置和数据结构"""

from app.core.config import settings
from app.core.state import (
    AnalysisState,
    AgentAnalysis,
    Decision,
    DebateMessage,
)

__all__ = [
    "settings",
    "AnalysisState",
    "AgentAnalysis",
    "Decision",
    "DebateMessage",
]
