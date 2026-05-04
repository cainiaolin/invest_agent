# tests/unit/core/test_state.py
import pytest
from app.core.state import AnalysisState, AgentAnalysis, Decision


def test_agent_analysis_creation():
    """测试AgentAnalysis创建"""
    analysis = AgentAnalysis(
        agent_name="TestAgent",
        agent_type="value",
        action="buy",
        confidence=0.85,
        reasoning="测试理由",
        key_metrics={"score": 8.5},
        price_target=100.0
    )

    assert analysis.agent_name == "TestAgent"
    assert analysis.action == "buy"
    assert analysis.confidence == 0.85
    assert analysis.price_target == 100.0


def test_agent_analysis_optional_price_target():
    """测试可选的价格目标"""
    analysis = AgentAnalysis(
        agent_name="TestAgent",
        agent_type="value",
        action="hold",
        confidence=0.6,
        reasoning="无目标价",
        key_metrics={},
        price_target=None
    )

    assert analysis.price_target is None


def test_analysis_state_creation():
    """测试AnalysisState创建"""
    state = AnalysisState(
        stock_code="600519",
        mode="parallel",
        user_request="分析这只股票",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None
    )

    assert state["stock_code"] == "600519"
    assert state["mode"] == "parallel"
    assert len(state["agent_analyses"]) == 0


def test_decision_creation():
    """测试Decision创建"""
    decision = Decision(
        action="buy",
        consensus=0.75,
        participating_agents=["BuffetAgent", "GrahamAgent"],
        summary="建议买入"
    )

    assert decision.action == "buy"
    assert decision.consensus == 0.75
    assert len(decision.participating_agents) == 2
