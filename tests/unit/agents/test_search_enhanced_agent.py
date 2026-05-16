import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any
import asyncio

from app.agents.search_enhanced_agent import SearchEnhancedAgent
from app.agents.llm_agent import LLMAgent
from app.models.search_strategy import SearchStrategy
from app.agents.search.fusion import InformationFusion
from app.services.llm_service import LLMService
from app.services.tushare_service import TushareService
from app.core.state import AnalysisState


class MockSearchEnhancedAgent(SearchEnhancedAgent):
    """用于测试的SearchEnhancedAgent模拟类"""

    def __init__(self, *args, **kwargs):
        # 直接调用SearchEnhancedAgent.__init__，跳过LLMAgent的抽象方法检查
        SearchEnhancedAgent.__init__(self, *args, **kwargs)

    @property
    def name(self) -> str:
        """Agent名称"""
        return "MockSearchAgent"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "Mock投资风格"

    def analyze_with_enhanced_context(self, state: Dict[str, Any], analysis_context: Dict[str, Any], search_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """抽象方法的实现，用于测试"""
        return {
            'analysis': f'mock_analysis_for_{state}',
            'search_enhanced': True,
            'search_strategy': self.search_strategy
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, search_context: str = "") -> str:
        if search_context:
            return f"mock_cot_prompt_with_search: {stock_data.get('stock_code', 'unknown')} - {search_context[:50]}"
        return f"mock_cot_prompt: {stock_data.get('stock_code', 'unknown')}"

    async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        """重写analyze方法用于测试"""
        # 这里我们简化实现，避免依赖复杂的状态管理
        stock_code = state.get("stock_code", "")
        return {
            "agent_name": self.name,
            "action": "buy",
            "confidence": 0.8,
            "reasoning": f"Mock analysis for {stock_code}",
            "search_enhanced": True,
            "search_strategy": self.search_strategy
        }

    def _parse_llm_response(self, response: Dict) -> Dict:
        return {
            'analysis': response.get('analysis', 'parsed_analysis'),
            'sentiment': response.get('sentiment', 'positive'),
            'action': 'buy',
            'confidence': 0.8,
            'reasoning': 'Mock reasoning'
        }


class TestSearchEnhancedAgent:
    """SearchEnhancedAgent单元测试"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_tushare_service = Mock(spec=TushareService)
        self.mock_search_service = Mock()
        self.mock_llm_service = Mock(spec=LLMService)
        self.mock_knowledge_service = Mock()
        self.master_name = "Test Master"

        # 模拟搜索策略
        self.mock_search_strategy = Mock(spec=SearchStrategy)
        self.mock_search_strategy.name = "test_strategy"
        self.mock_search_strategy.search_keywords = ["AAPL", "Apple"]

    def test_search_enhanced_agent_initialization(self):
        """测试SearchEnhancedAgent初始化"""
        # 创建实例
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name,
            search_strategy=self.mock_search_strategy
        )

        # 验证继承关系
        assert isinstance(agent, LLMAgent)

        # 验证属性设置
        assert agent.search_strategy == self.mock_search_strategy
        assert hasattr(agent, 'fusion')
        assert isinstance(agent.fusion, InformationFusion)

        # 验证父类初始化被调用
        assert agent.llm == self.mock_llm_service
        assert agent._master_name == self.master_name

    def test_search_enhanced_agent_default_strategy(self):
        """测试默认搜索策略"""
        # 不提供search_strategy，应该使用默认策略
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name
        )

        # 验证使用了默认策略
        assert agent.search_strategy is not None
        assert agent.search_strategy.search_basic_info is True
        assert isinstance(agent.search_strategy.search_keywords, list)

    def test_search_enhanced_agent_is_abstract(self):
        """测试SearchEnhancedAgent是抽象类"""
        from abc import ABC

        # 验证继承关系
        assert issubclass(MockSearchEnhancedAgent, LLMAgent)

        # 验证SearchEnhancedAgent确实有抽象方法
        assert hasattr(SearchEnhancedAgent, '_build_cot_prompt')

        # 验证SearchEnhancedAgent有抽象方法
        import inspect
        methods = inspect.getmembers(SearchEnhancedAgent, predicate=inspect.isfunction)
        abstract_methods = [name for name, method in methods if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__]
        assert 'analyze_with_enhanced_context' in abstract_methods

    def test_get_search_strategy(self):
        """测试get_search_strategy方法"""
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name,
            search_strategy=self.mock_search_strategy
        )

        # 获取搜索策略
        strategy = agent.get_search_strategy()

        # 验证返回正确的策略
        assert strategy == self.mock_search_strategy

    @patch('app.agents.search_enhanced_agent.InformationFusion')
    def test_get_search_context_with_search_service(self, mock_fusion_class):
        """测试_get_get_search_context方法，当有search_service时"""
        # 设置模拟 fusion
        mock_fusion = Mock()
        mock_fusion_class.return_value = mock_fusion
        mock_fusion.format_for_llm.return_value = "formatted_search_context"

        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name
        )

        # 创建搜索摘要对象
        from app.models.search import SearchSummary, SearchResult
        search_result = SearchResult(
            title="Apple News",
            url="https://example.com/apple",
            content="Apple stock news",
            source="news",
            reliability=0.8,
            relevance=0.9,
            timestamp="2024-01-01"
        )

        search_summary = SearchSummary(
            stock_code="AAPL",
            search_keywords=["Apple"],
            total_results=1,
            high_quality_count=1,
            medium_quality_count=0,
            low_quality_count=0,
            high_ratio=1.0,
            search_timestamp="2024-01-01T00:00:00",
            results_by_source={"news": [search_result]}
        )

        # 模拟搜索服务返回结果
        stock_code = "AAPL"
        stock_data = {"name": "Apple Inc.", "price": 150.0}

        self.mock_search_service.search_stock_info.return_value = search_summary

        # 获取搜索上下文
        context = agent._get_search_context(stock_code, stock_data)

        # 验证搜索服务被调用
        self.mock_search_service.search_stock_info.assert_called_once_with(stock_code, stock_data)

        # 验证fusion格式化被调用
        mock_fusion.format_for_llm.assert_called_once_with(search_summary, stock_data)

        # 验证返回格式化的上下文
        assert context == "formatted_search_context"

    @patch('app.agents.search_enhanced_agent.InformationFusion')
    def test_get_search_context_without_search_service(self, mock_fusion_class):
        """测试_get_get_search_context方法，当没有search_service时"""
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=None,  # 设置为None
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name
        )

        stock_code = "AAPL"
        stock_data = {"name": "Apple Inc.", "price": 150.0}

        # 获取搜索上下文
        context = agent._get_search_context(stock_code, stock_data)

        # 验证返回空字符串
        assert context == ""

    @patch('app.agents.search_enhanced_agent.InformationFusion')
    def test_get_search_context_exception_handling(self, mock_fusion_class):
        """测试_get_get_search_context方法的异常处理"""
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name
        )

        stock_code = "AAPL"
        stock_data = {"name": "Apple Inc.", "price": 150.0}

        # 模拟搜索服务抛出异常
        self.mock_search_service.search_stock_info.side_effect = Exception("Search failed")

        # 获取搜索上下文（应该捕获异常并返回空字符串）
        context = agent._get_search_context(stock_code, stock_data)

        # 验证返回空字符串
        assert context == ""

        # 验证搜索服务确实被调用了
        self.mock_search_service.search_stock_info.assert_called_once_with(stock_code, stock_data)

    def test_analyze_with_search_enhancement(self):
        """测试_analyze_with_search_enhancement方法"""
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name,
            search_strategy=self.mock_search_strategy
        )

        # 模拟状态对象
        state = {"stock_code": "AAPL"}
        stock_data = {"stock_code": "AAPL", "name": "Apple Inc."}
        knowledge = {"news": ["Apple news"]}

        # 模拟LLM服务的方法
        from unittest.mock import AsyncMock
        mock_result = {'analysis': 'enhanced_analysis', 'sentiment': 'positive'}
        agent.llm.reason_with_cot = Mock(return_value=mock_result)

        # 模拟搜索上下文获取
        agent._get_search_context = Mock(return_value="search_context")

        # 执行增强分析
        result = agent._analyze_with_search_enhancement(state, stock_data, knowledge)

        # 验证搜索上下文获取被调用
        agent._get_search_context.assert_called_once_with("AAPL", stock_data)

        # 验证LLM服务被调用
        expected_prompt = "mock_cot_prompt_with_search: AAPL - search_context"
        agent.llm.reason_with_cot.assert_called_once_with(expected_prompt)

        # 验证结果包含搜索增强信息
        assert result['analysis'] == 'enhanced_analysis'
        assert result['sentiment'] == 'positive'
        assert result['search_enhanced'] is True
        assert result['search_strategy'] == self.mock_search_strategy

    def test_analyze_with_enhanced_context_abstract_method(self):
        """测试analyze_with_enhanced_context抽象方法"""
        agent = MockSearchEnhancedAgent(
            tushare_service=self.mock_tushare_service,
            search_service=self.mock_search_service,
            llm_service=self.mock_llm_service,
            knowledge_service=self.mock_knowledge_service,
            master_name=self.master_name
        )

        state = "test_state"
        analysis_context = {"analysis": "basic_analysis"}
        search_summary = {"summary": "search_summary"}

        # 调用抽象方法（在我们的模拟类中已实现）
        result = agent.analyze_with_enhanced_context(state, analysis_context, search_summary)

        # 验证结果
        assert result['analysis'] == 'mock_analysis_for_test_state'
        assert result['search_enhanced'] is True
        assert result['search_strategy'] == agent.search_strategy


if __name__ == '__main__':
    pytest.main([__file__])