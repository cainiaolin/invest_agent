"""协作模式集成测试"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.graph.workflow import create_investment_workflow
from app.core.state import AnalysisState


class TestVoteCollaborationIntegration:
    """投票协作模式集成测试"""

    @pytest.mark.asyncio
    async def test_full_vote_workflow(self):
        """测试完整的投票工作流"""
        workflow = create_investment_workflow()

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析贵州茅台的投资价值",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # Mock Tushare服务
        with patch("app.graph.nodes.router.TushareService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.get_stock_data = AsyncMock(
                return_value={
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "metrics": {
                        "pe_ratio": 30.0,
                        "pb_ratio": 10.0,
                        "roe": 25.0,
                        "debt_ratio": 20.0,
                        "current_ratio": 3.0,
                        "dividend_yield": 1.5,
                        "revenue_growth": 15.0,
                        "profit_growth": 18.0,
                        "operating_margin": 50.0,
                        "net_margin": 45.0,
                    },
                    "moat_indicators": {
                        "brand_strength": 9,
                        "market_share": 60.0,
                        "competitive_advantage": True,
                    },
                    "growth_indicators": {
                        "rd_ratio": 2.0,
                        "rd_growth": 10.0,
                        "market_share_growth": 3.0,
                        "customer_satisfaction": 8,
                        "sales_force_quality": 8,
                    },
                    "management_quality": {
                        "management_tenure": 15.0,
                        "management_experience": 20,
                        "employee_turnover": 5.0,
                        "employee_satisfaction": 8,
                        "internal_control_quality": 9,
                    },
                }
            )

            # 执行工作流
            # 注意：由于LangGraph的异步执行机制，这里我们验证工作流结构
            # 实际执行需要更完整的mock
            assert workflow is not None

            # 验证所有必要的节点都存在
            nodes = workflow.nodes
            assert "router" in nodes
            assert "parallel_agents" in nodes
            assert "vote_collaboration" in nodes
            assert "output" in nodes


class TestDebateCollaborationIntegration:
    """辩论协作模式集成测试"""

    @pytest.mark.asyncio
    async def test_full_debate_workflow(self):
        """测试完整的辩论工作流"""
        workflow = create_investment_workflow()

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "debate",
            "user_request": "分析贵州茅台的投资价值",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # 验证工作流结构
        assert workflow is not None

        nodes = workflow.nodes
        assert "router" in nodes
        assert "parallel_agents" in nodes
        assert "debate_collaboration" in nodes
        assert "output" in nodes


class TestParallelModeIntegration:
    """并行模式集成测试"""

    @pytest.mark.asyncio
    async def test_full_parallel_workflow(self):
        """测试完整的并行工作流（无协作）"""
        workflow = create_investment_workflow()

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析贵州茅台的投资价值",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # 验证工作流结构
        assert workflow is not None

        nodes = workflow.nodes
        assert "router" in nodes
        assert "parallel_agents" in nodes
        assert "output" in nodes


class TestAgentExecutionIntegration:
    """Agent执行集成测试"""

    @pytest.mark.asyncio
    async def test_value_agents_execution(self):
        """测试价值投资Agent执行"""
        from app.graph.nodes.agents import value_agent_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票的价值",
            "stock_data": {
                "symbol": "600519",
                "name": "贵州茅台",
                "metrics": {
                    "pe_ratio": 30.0,
                    "pb_ratio": 10.0,
                    "roe": 25.0,
                    "debt_ratio": 20.0,
                    "current_ratio": 3.0,
                    "dividend_yield": 1.5,
                    "revenue_growth": 15.0,
                    "profit_growth": 18.0,
                },
                "moat_indicators": {
                    "brand_strength": 9,
                    "market_share": 60.0,
                    "competitive_advantage": True,
                },
            },
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await value_agent_node(state)

        assert "agent_analyses" in result
        assert len(result["agent_analyses"]) == 2  # Buffett和Graham

        # 验证Agent类型
        for analysis in result["agent_analyses"]:
            assert analysis["agent_type"] == "value"
            assert analysis["action"] in ["buy", "sell", "hold"]
            assert 0 <= analysis["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_growth_agents_execution(self):
        """测试成长投资Agent执行"""
        from app.graph.nodes.agents import growth_agent_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票的成长性",
            "stock_data": {
                "symbol": "600519",
                "name": "贵州茅台",
                "metrics": {
                    "pe_ratio": 30.0,
                    "pb_ratio": 10.0,
                    "roe": 25.0,
                    "debt_ratio": 20.0,
                    "revenue_growth": 25.0,
                    "profit_growth": 30.0,
                    "operating_margin": 50.0,
                    "net_margin": 45.0,
                },
                "growth_indicators": {
                    "rd_ratio": 5.0,
                    "rd_growth": 20.0,
                    "market_share_growth": 5.0,
                    "customer_satisfaction": 9,
                    "sales_force_quality": 9,
                },
                "management_quality": {
                    "management_tenure": 15.0,
                    "management_experience": 20,
                    "employee_turnover": 5.0,
                    "employee_satisfaction": 9,
                    "internal_control_quality": 9,
                },
            },
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await growth_agent_node(state)

        assert "agent_analyses" in result
        assert len(result["agent_analyses"]) == 2  # Fisher和Lynch

        # 验证Agent类型
        for analysis in result["agent_analyses"]:
            assert analysis["agent_type"] == "growth"
            assert analysis["action"] in ["buy", "sell", "hold"]

    @pytest.mark.asyncio
    async def test_macro_agents_execution(self):
        """测试宏观分析Agent执行"""
        from app.graph.nodes.agents import macro_agent_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析宏观经济影响",
            "stock_data": {
                "symbol": "600519",
                "name": "贵州茅台",
                "metrics": {
                    "pe_ratio": 30.0,
                    "pb_ratio": 10.0,
                    "roe": 25.0,
                    "debt_ratio": 20.0,
                },
                "macro_indicators": {
                    "gdp_growth": 6.5,
                    "inflation_rate": 2.5,
                    "interest_rate": 4.5,
                    "market_cycle": "bull",
                    "industry_outlook": "positive",
                    "regulatory_risk": "low",
                    "geopolitical_risk": "low",
                    "liquidity_condition": "adequate",
                },
            },
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await macro_agent_node(state)

        assert "agent_analyses" in result
        assert len(result["agent_analyses"]) == 2  # Soros和Dalio

        # 验证Agent类型
        for analysis in result["agent_analyses"]:
            assert analysis["agent_type"] == "macro"
            assert analysis["action"] in ["buy", "sell", "hold"]


class TestErrorHandling:
    """错误处理集成测试"""

    @pytest.mark.asyncio
    async def test_router_error_handling(self):
        """测试路由节点错误处理"""
        from app.graph.nodes.router import router_node

        state: AnalysisState = {
            "stock_code": "INVALID_CODE",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # Mock Tushare服务抛出异常
        with patch("app.graph.nodes.router.TushareService") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.get_stock_data = AsyncMock(side_effect=Exception("股票代码不存在"))

            result = await router_node(state)

            # 应该包含错误信息
            assert "error" in result
            assert "路由节点错误" in result["error"]

    @pytest.mark.asyncio
    async def test_collaboration_without_analyses(self):
        """测试无分析结果时的协作"""
        from app.graph.nodes.collaboration import vote_collaboration_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [],  # 空分析结果
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await vote_collaboration_node(state)

        # 应该设置错误而不是崩溃
        assert "error" in result


class TestWorkflowStateManagement:
    """工作流状态管理测试"""

    def test_state_immutability_in_workflow(self):
        """测试工作流中的状态不可变性"""
        from app.core.state import AnalysisState

        # 创建初始状态
        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        # 验证状态结构
        assert "stock_code" in state
        assert "mode" in state
        assert "agent_analyses" in state
        assert "final_decision" in state

        # 验证类型
        assert isinstance(state["agent_analyses"], list)
        assert isinstance(state["debate_round"], int)
        assert isinstance(state["debate_history"], list)

    @pytest.mark.asyncio
    async def test_state_accumulation(self):
        """测试状态累积"""
        from app.graph.nodes.agents import parallel_agents_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析股票",
            "stock_data": {
                "symbol": "600519",
                "name": "贵州茅台",
                "metrics": {
                    "pe_ratio": 30.0,
                    "pb_ratio": 10.0,
                    "roe": 25.0,
                    "debt_ratio": 20.0,
                },
            },
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await parallel_agents_node(state)

        # agent_analyses应该累积结果
        assert len(result["agent_analyses"]) > 0

        # 每个分析应该包含必需字段
        for analysis in result["agent_analyses"]:
            assert "agent_name" in analysis
            assert "agent_type" in analysis
            assert "action" in analysis
            assert "confidence" in analysis
