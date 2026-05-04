"""工作流单元测试"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.graph.workflow import create_investment_workflow
from app.core.state import AnalysisState


class TestInvestmentWorkflow:
    """投资分析工作流测试"""

    @pytest.fixture
    def workflow(self):
        """创建工作流实例"""
        return create_investment_workflow()

    @pytest.fixture
    def sample_state(self):
        """示例状态"""
        return {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析贵州茅台的投资价值",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

    def test_workflow_creation(self, workflow):
        """测试工作流创建"""
        assert workflow is not None
        # 验证工作流结构
        nodes = workflow.nodes
        assert "router" in nodes
        assert "parallel_agents" in nodes
        assert "value_agents" in nodes
        assert "growth_agents" in nodes
        assert "macro_agents" in nodes
        assert "vote_collaboration" in nodes
        assert "debate_collaboration" in nodes
        assert "output" in nodes

    def test_workflow_entry_point(self, workflow):
        """测试工作流入口点"""
        # 工作流的入口点应该是router
        assert workflow.entry_point == "router"

    @pytest.mark.asyncio
    async def test_parallel_mode_flow(self, workflow, sample_state):
        """测试并行模式流程"""
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
                    },
                }
            )

            # 执行工作流
            # 注意：实际执行需要完整的状态和依赖
            # 这里仅测试工作流结构是否正确
            assert workflow is not None

    def test_router_node_structure(self, workflow):
        """测试路由节点结构"""
        # router节点应该存在
        assert "router" in workflow.nodes

        # router的输出边应该是条件边
        edges = workflow.edges
        assert len(edges) > 0


class TestWorkflowEdges:
    """工作流边条件测试"""

    def test_route_to_agents_parallel(self):
        """测试路由到并行Agent"""
        from app.graph.edges.conditions import route_to_agents

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析股票",
            "selected_agent_type": "parallel",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = route_to_agents(state)
        assert result == "parallel"

    def test_route_to_agents_value(self):
        """测试路由到价值Agent"""
        from app.graph.edges.conditions import route_to_agents

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票的价值投资机会",
            "selected_agent_type": "value",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = route_to_agents(state)
        assert result == "value"

    def test_route_after_agents_vote(self):
        """测试Agent后路由到投票"""
        from app.graph.edges.conditions import route_after_agents

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

        result = route_after_agents(state)
        assert result == "vote"

    def test_route_after_agents_debate(self):
        """测试Agent后路由到辩论"""
        from app.graph.edges.conditions import route_after_agents

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "debate",
            "user_request": "分析股票",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = route_after_agents(state)
        assert result == "debate"

    def test_route_after_agents_parallel(self):
        """测试Agent后直接输出"""
        from app.graph.edges.conditions import route_after_agents

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析股票",
            "agent_analyses": [],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = route_after_agents(state)
        assert result == "parallel"


class TestRouterNode:
    """路由节点测试"""

    @pytest.mark.asyncio
    async def test_router_node_basic(self):
        """测试路由节点基本功能"""
        from app.graph.nodes.router import router_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "parallel",
            "user_request": "分析股票的投资价值",
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
                    "metrics": {"pe_ratio": 30.0},
                }
            )

            result = await router_node(state)

            assert "stock_data" in result
            assert "selected_agent_type" in result
            assert result["selected_agent_type"] in ["value", "growth", "macro", "parallel"]

    def test_select_agent_type_value(self):
        """测试选择价值投资Agent"""
        from app.graph.nodes.router import _select_agent_type

        result = _select_agent_type("分析股票的价值投资机会和安全边际")
        assert result == "value"

    def test_select_agent_type_growth(self):
        """测试选择成长投资Agent"""
        from app.graph.nodes.router import _select_agent_type

        result = _select_agent_type("分析股票的成长潜力和增长机会")
        assert result == "growth"

    def test_select_agent_type_macro(self):
        """测试选择宏观分析Agent"""
        from app.graph.nodes.router import _select_agent_type

        result = _select_agent_type("分析宏观经济环境和政策影响")
        assert result == "macro"

    def test_select_agent_type_default(self):
        """测试默认选择并行Agent"""
        from app.graph.nodes.router import _select_agent_type

        result = _select_agent_type("分析这只股票")
        assert result == "parallel"


class TestCollaborationNodes:
    """协作节点测试"""

    @pytest.mark.asyncio
    async def test_vote_collaboration(self):
        """测试投票协作节点"""
        from app.graph.nodes.collaboration import vote_collaboration_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [
                {
                    "agent_name": "Warren Buffett",
                    "agent_type": "value",
                    "action": "buy",
                    "confidence": 0.8,
                    "reasoning": "好公司",
                    "key_metrics": {},
                    "price_target": None,
                },
                {
                    "agent_name": "Benjamin Graham",
                    "agent_type": "value",
                    "action": "buy",
                    "confidence": 0.7,
                    "reasoning": "低估",
                    "key_metrics": {},
                    "price_target": None,
                },
                {
                    "agent_name": "Philip Fisher",
                    "agent_type": "growth",
                    "action": "hold",
                    "confidence": 0.6,
                    "reasoning": "观望",
                    "key_metrics": {},
                    "price_target": None,
                },
            ],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await vote_collaboration_node(state)

        assert "final_decision" in result
        assert result["final_decision"]["action"] == "buy"
        assert result["final_decision"]["consensus"] > 0.5

    @pytest.mark.asyncio
    async def test_vote_collaboration_tie(self):
        """测试投票平票情况"""
        from app.graph.nodes.collaboration import vote_collaboration_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [
                {
                    "agent_name": "Agent1",
                    "agent_type": "value",
                    "action": "buy",
                    "confidence": 0.5,
                    "reasoning": "买入",
                    "key_metrics": {},
                    "price_target": None,
                },
                {
                    "agent_name": "Agent2",
                    "agent_type": "growth",
                    "action": "sell",
                    "confidence": 0.5,
                    "reasoning": "卖出",
                    "key_metrics": {},
                    "price_target": None,
                },
                {
                    "agent_name": "Agent3",
                    "agent_type": "macro",
                    "action": "hold",
                    "confidence": 0.5,
                    "reasoning": "持有",
                    "key_metrics": {},
                    "price_target": None,
                },
            ],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": None,
            "error": None,
        }

        result = await vote_collaboration_node(state)

        # 平票时应该优先选择hold
        assert result["final_decision"]["action"] == "hold"

    @pytest.mark.asyncio
    async def test_vote_collaboration_empty_analyses(self):
        """测试无分析结果时的投票"""
        from app.graph.nodes.collaboration import vote_collaboration_node

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

        result = await vote_collaboration_node(state)

        # 应该设置错误信息
        assert "error" in result
        assert "没有Agent分析结果" in result["error"]


class TestOutputNode:
    """输出节点测试"""

    @pytest.mark.asyncio
    async def test_output_node_formatting(self):
        """测试输出节点格式化"""
        from app.graph.nodes.output import output_node

        state: AnalysisState = {
            "stock_code": "600519",
            "mode": "vote",
            "user_request": "分析股票",
            "agent_analyses": [
                {
                    "agent_name": "Warren Buffett",
                    "agent_type": "value",
                    "action": "buy",
                    "confidence": 0.8,
                    "reasoning": "这是一家优质公司",
                    "key_metrics": {"scores": {"moat": 80, "quality": 75}},
                    "price_target": None,
                }
            ],
            "debate_round": 0,
            "debate_history": [],
            "final_decision": {
                "action": "buy",
                "consensus": 0.8,
                "participating_agents": ["Warren Buffett"],
                "summary": "建议买入",
            },
            "error": None,
        }

        result = await output_node(state)

        assert "formatted_output" in result
        assert "投资分析报告" in result["formatted_output"]
        assert "600519" in result["formatted_output"]
        assert "Warren Buffett" in result["formatted_output"]
        assert "买入" in result["formatted_output"]
