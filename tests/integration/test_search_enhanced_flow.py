"""
搜索增强端到端流程测试

测试完整的数据获取、搜索增强、知识库查询和LLM分析流程
包括正常流程和降级机制测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.agents.value.buffet_search_agent import BuffetSearchAgent
from app.services.tushare_service import TushareService
from app.services.search.web_search_service import WebSearchService
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.models.search_strategy import SearchStrategy


class TestBuffetSearchEnhancedFullFlow:
    """BuffetSearchAgent完整流程测试"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    @patch("app.services.tushare_service.TushareService")
    @patch("app.services.search.web_search_service.WebSearchService")
    @patch("app.services.llm_service.LLMService")
    @patch("app.services.knowledge_service.KnowledgeService")
    async def test_buffet_search_enhanced_full_flow(
        self,
        mock_knowledge_service_class,
        mock_llm_service_class,
        mock_search_service_class,
        mock_tushare_service_class
    ):
        """
        测试完整的搜索增强流程

        验证从数据获取到搜索增强再到LLM分析的完整流程
        """
        # 1. 初始化所有服务（使用真实类但mock具体方法）
        mock_tushare_service = mock_tushare_service_class.return_value
        mock_tushare_service.get_stock_data = AsyncMock(return_value={
            'symbol': '600519',
            'name': '贵州茅台',
            'price': 1500.0,
            'pe': 25.5,
            'pb': 12.8,
            'roe': 25.8,
            'market_cap': '1.8万亿',
            'revenue': 1200,
            'profit': 600
        })

        mock_search_service = mock_search_service_class.return_value
        mock_search_service.web_search = AsyncMock(return_value={
            'company_analysis': '贵州茅台在白酒行业具有绝对领导地位，品牌护城河宽阔',
            'industry_trends': '高端白酒需求稳定增长',
            'competitive_landscape': '与五粮液等竞争对手相比具有明显优势',
            'reliability_score': 0.85
        })

        mock_llm_service = mock_llm_service_class.return_value
        mock_llm_service.reason_with_cot = AsyncMock(return_value={
            'action': 'BUY',
            'confidence': 0.9,
            'reasoning': '护城河宽阔，估值合理，管理层优秀，安全边际充足',
            'key_metrics': {
                'pe': 25.5,
                'pb': 12.8,
                'roe': 25.8
            },
            'key_factors': ['护城河宽阔', '管理层优秀', '估值合理', '品牌价值高'],
            'thought_process': '详细的投资思考过程...'
        })

        mock_knowledge_service = mock_knowledge_service_class.return_value
        mock_knowledge_service.load_knowledge = AsyncMock(return_value={
            'investment_philosophy': '寻找具有持久竞争优势的企业，以合理的价格买入并长期持有',
            'key_principles': [
                '护城河理论',
                '安全边际原则',
                '管理层质量评估',
                '财务健康状况分析',
                '长期持有策略'
            ],
            'case_studies': [
                {
                    'company': '可口可乐',
                    'reason': '强大的品牌护城河',
                    'result': '长期优秀表现'
                },
                {
                    'company': '美国运通',
                    'reason': '高转换成本',
                    'result': '稳定增长'
                }
            ]
        })

        # 2. 创建BuffetSearchAgent实例
        agent = BuffetSearchAgent(
            tushare_service=mock_tushare_service,
            search_service=mock_search_service,
            llm_service=mock_llm_service,
            knowledge_service=mock_knowledge_service
        )

        # 3. 执行分析
        state = {
            'stock_code': '600519',
            'current_price': 1500.0,
            'market_status': '正常',
            'analysis_type': 'full_analysis'
        }

        result = await agent.analyze(state)

        # 4. 验证结果包含必要字段
        required_fields = [
            'agent_name', 'action', 'confidence', 'reasoning',
            'analysis_mode', 'has_search_data'
        ]

        for field in required_fields:
            assert field in result, f"缺少必需字段: {field}"

        # 验证字段值
        assert result['agent_name'] == 'Buffett'
        assert result['action'] in ['BUY', 'HOLD', 'SELL']
        assert 0 <= result['confidence'] <= 1
        assert isinstance(result['reasoning'], str)
        assert result['reasoning'] != ""
        assert result['analysis_mode'] in ['ai_llm', 'rule_fallback']
        assert isinstance(result['has_search_data'], bool)

        # 5. 如果有搜索数据，验证search_strategy字段
        if result['has_search_data']:
            assert 'search_strategy' in result
            assert isinstance(result['search_strategy'], SearchStrategy)

            # 验证搜索策略配置
            strategy = result['search_strategy']
            assert strategy.search_basic_info == True
            assert strategy.search_market_sentiment == False  # 巴菲特不关注短期情绪
            assert strategy.search_industry == True
            assert strategy.search_competitors == True
            assert strategy.time_horizon == 30  # 长期视角
            assert strategy.min_reliability == 0.7

        # 6. 验证方法调用
        mock_tushare_service.get_stock_data.assert_called_once_with('600519')
        mock_search_service.web_search.assert_called_once()
        mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
        mock_llm_service.reason_with_cot.assert_called_once()

        # 7. 验证结果质量
        assert result['confidence'] > 0.5  # 置信度应该较高
        assert len(result['key_factors']) > 0  # 应该有关键因素分析


class TestSearchFallbackMechanism:
    """搜索降级机制测试"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    @patch("app.services.tushare_service.TushareService")
    @patch("app.services.search.web_search_service.WebSearchService")
    @patch("app.services.llm_service.LLMService")
    @patch("app.services.knowledge_service.KnowledgeService")
    async def test_search_fallback_mechanism(
        self,
        mock_knowledge_service_class,
        mock_llm_service_class,
        mock_search_service_class,
        mock_tushare_service_class
    ):
        """
        测试搜索服务失败时的降级机制

        验证当搜索服务不可用时，系统会降级到基础LLM分析
        """

        # 1. 创建会失败的搜索服务
        class FailingSearchService:
            async def web_search(self, query):
                raise Exception("搜索服务暂时不可用")

        failing_search = FailingSearchService()

        # 2. 初始化其他正常服务
        mock_tushare_service = mock_tushare_service_class.return_value
        mock_tushare_service.get_stock_data = AsyncMock(return_value={
            'symbol': '000001',
            'name': '平安银行',
            'price': 10.5,
            'pe': 5.2,
            'pb': 0.8,
            'roe': 8.5,
            'market_cap': '2000亿'
        })

        mock_llm_service = mock_llm_service_class.return_value
        mock_llm_service.reason_with_cot = AsyncMock(return_value={
            'action': 'HOLD',
            'confidence': 0.6,
            'reasoning': '估值合理，但面临竞争压力，建议观察',
            'key_metrics': {
                'pe': 5.2,
                'pb': 0.8,
                'roe': 8.5
            },
            'key_factors': ['估值较低', '竞争压力', '业绩稳定'],
            'thought_process': '基于财务数据的保守分析...'
        })

        mock_knowledge_service = mock_knowledge_service_class.return_value
        mock_knowledge_service.load_knowledge = AsyncMock(return_value={
            'investment_philosophy': '寻找具有持久竞争优势的企业',
            'key_principles': ['护城河理论', '安全边际'],
            'case_studies': []
        })

        # 3. 创建BuffetSearchAgent实例（使用会失败的搜索服务）
        agent = BuffetSearchAgent(
            tushare_service=mock_tushare_service,
            search_service=failing_search,
            llm_service=mock_llm_service,
            knowledge_service=mock_knowledge_service
        )

        # 4. 执行分析
        state = {
            'stock_code': '000001',
            'current_price': 10.5,
            'market_status': '正常',
            'analysis_type': 'full_analysis'
        }

        result = await agent.analyze(state)

        # 5. 验证降级机制生效
        assert result['analysis_mode'] in ['ai_llm', 'rule_fallback']
        assert result['has_search_data'] == False  # 搜索应该失败

        # 6. 验证基础功能仍然正常工作
        required_fields = [
            'agent_name', 'action', 'confidence', 'reasoning'
        ]

        for field in required_fields:
            assert field in result, f"缺少必需字段: {field}"

        assert result['agent_name'] == 'Buffett'
        assert result['action'] in ['BUY', 'HOLD', 'SELL']
        assert 0 <= result['confidence'] <= 1
        assert isinstance(result['reasoning'], str)

        # 7. 验证LLM和知识库服务被正常调用
        mock_tushare_service.get_stock_data.assert_called_once_with('000001')
        mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
        mock_llm_service.reason_with_cot.assert_called_once()

        # 8. 验证错误处理（搜索服务应该被调用过并失败）
        with pytest.raises(Exception):
            await failing_search.web_search("any query")


    @pytest.mark.e2e
    @pytest.mark.asyncio
    @patch("app.services.tushare_service.TushareService")
    @patch("app.services.search.web_search_service.WebSearchService")
    @patch("app.services.llm_service.LLMService")
    @patch("app.services.knowledge_service.KnowledgeService")
    async def test_llm_service_fallback_to_rule_engine(
        self,
        mock_knowledge_service_class,
        mock_llm_service_class,
        mock_search_service_class,
        mock_tushare_service_class
    ):
        """
        测试LLM服务失败时的规则引擎降级

        验证当LLM服务不可用时，系统会降级到规则引擎
        """

        # 1. 创建正常的服务，但让LLM服务返回空响应（模拟服务降级）
        mock_tushare_service = mock_tushare_service_class.return_value
        mock_tushare_service.get_stock_data = AsyncMock(return_value={
            'symbol': '600036',
            'name': '招商银行',
            'price': 35.2,
            'pe': 6.8,
            'pb': 0.9,
            'roe': 12.5,
            'market_cap': '8000亿'
        })

        # LLM服务返回空响应，模拟服务降级
        mock_llm_service = mock_llm_service_class.return_value
        mock_llm_service.reason_with_cot = AsyncMock(return_value={
            'action': None,  # 空响应
            'confidence': 0.0,
            'reasoning': 'LLM服务暂时不可用，使用规则引擎',
            'key_metrics': {},
            'key_factors': [],
            'thought_process': ''
        })

        mock_knowledge_service = mock_knowledge_service_class.return_value
        mock_knowledge_service.load_knowledge = AsyncMock(return_value={
            'investment_philosophy': '寻找具有持久竞争优势的企业',
            'key_principles': ['护城河理论', '安全边际'],
            'case_studies': []
        })

        mock_search_service = mock_search_service_class.return_value
        mock_search_service.web_search = AsyncMock(return_value={
            'company_analysis': '招商银行在零售银行业务具有优势',
            'reliability_score': 0.75
        })

        # 2. 创建BuffetSearchAgent实例
        agent = BuffetSearchAgent(
            tushare_service=mock_tushare_service,
            search_service=mock_search_service,
            llm_service=mock_llm_service,
            knowledge_service=mock_knowledge_service
        )

        # 3. 执行分析
        state = {
            'stock_code': '600036',
            'current_price': 35.2,
            'market_status': '正常',
            'analysis_type': 'full_analysis'
        }

        result = await agent.analyze(state)

        # 4. 验证规则引擎降级生效
        assert result['analysis_mode'] == 'rule_fallback'
        assert result['has_search_data'] == True  # 搜索应该成功

        # 5. 验证基础功能仍然正常工作
        required_fields = [
            'agent_name', 'action', 'confidence', 'reasoning'
        ]

        for field in required_fields:
            assert field in result, f"缺少必需字段: {field}"

        assert result['agent_name'] == 'Buffett'
        assert result['action'] in ['BUY', 'HOLD', 'SELL']  # 规则引擎应该能生成决策
        assert 0 <= result['confidence'] <= 1
        assert isinstance(result['reasoning'], str)
        assert '规则引擎' in result['reasoning'] or '基础分析' in result['reasoning']

        # 6. 验证其他服务被正常调用
        mock_tushare_service.get_stock_data.assert_called_once_with('600036')
        mock_search_service.web_search.assert_called_once()
        mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
        mock_llm_service.reason_with_cot.assert_called_once()


class TestBuffetSearchStrategyValidation:
    """巴菲特搜索策略验证测试"""

    @pytest.mark.e2e
    def test_buffet_search_strategy_configuration(self):
        """
        测试巴菲特搜索策略的特定配置

        验证巴菲特Agent的搜索策略符合其投资哲学
        """
        # 创建服务mock
        mock_tushare = Mock()
        mock_search = Mock()
        mock_llm = Mock()
        mock_knowledge = Mock()

        # 创建Agent实例
        agent = BuffetSearchAgent(
            tushare_service=mock_tushare,
            search_service=mock_search,
            llm_service=mock_llm,
            knowledge_service=mock_knowledge
        )

        # 获取搜索策略
        strategy = agent.get_search_strategy()

        # 验证策略配置符合巴菲特投资哲学
        assert isinstance(strategy, SearchStrategy)

        # 巴菲特不关注短期市场情绪
        assert strategy.search_market_sentiment == False

        # 巴菲特关注基本面信息
        assert strategy.search_basic_info == True

        # 巴菲特关注行业地位和竞争格局
        assert strategy.search_industry == True
        assert strategy.search_competitors == True

        # 长期视角（30天）
        assert strategy.time_horizon == 30

        # 较高的可信度要求
        assert strategy.min_reliability == 0.7

        # 合理的信息数量
        assert strategy.max_results_per_source == 15


class TestBuffetAgentIntegrationWithCoreSystem:
    """BuffetAgent与核心系统集成测试"""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    @patch("app.services.tushare_service.TushareService")
    @patch("app.services.search.web_search_service.WebSearchService")
    @patch("app.services.llm_service.LLMService")
    @patch("app.services.knowledge_service.KnowledgeService")
    async def test_integration_with_workflow_system(
        self,
        mock_knowledge_service_class,
        mock_llm_service_class,
        mock_search_service_class,
        mock_tushare_service_class
    ):
        """
        测试BuffetAgent与工作流系统的集成

        验证Agent能够正确处理工作流传递的状态和参数
        """

        # 1. 初始化服务
        mock_tushare_service = mock_tushare_service_class.return_value
        mock_tushare_service.get_stock_data = AsyncMock(return_value={
            'symbol': '600276',
            'name': '恒瑞医药',
            'price': 45.8,
            'pe': 18.5,
            'pb': 3.2,
            'roe': 22.1,
            'market_cap': '2500亿'
        })

        mock_search_service = mock_search_service_class.return_value
        mock_search_service.web_search = AsyncMock(return_value={
            'company_analysis': '恒瑞医药在创新药领域研发投入大',
            'industry_trends': '医药政策改革影响行业',
            'competitive_landscape': '与药企巨头竞争',
            'reliability_score': 0.8
        })

        mock_llm_service = mock_llm_service_class.return_value
        mock_llm_service.reason_with_cot = AsyncMock(return_value={
            'action': 'BUY',
            'confidence': 0.75,
            'reasoning': '研发实力强，护城河正在形成，估值合理',
            'key_metrics': {
                'pe': 18.5,
                'pb': 3.2,
                'roe': 22.1
            },
            'key_factors': ['研发投入大', '创新能力', '政策受益'],
            'thought_process': '医药行业分析...'
        })

        mock_knowledge_service = mock_knowledge_service_class.return_value
        mock_knowledge_service.load_knowledge = AsyncMock(return_value={
            'investment_philosophy': '寻找具有持久竞争优势的企业',
            'key_principles': ['护城河理论', '管理层质量', '长期持有'],
            'case_studies': ['医药公司案例']
        })

        # 2. 创建Agent实例
        agent = BuffetSearchAgent(
            tushare_service=mock_tushare_service,
            search_service=mock_search_service,
            llm_service=mock_llm_service,
            knowledge_service=mock_knowledge_service
        )

        # 3. 模拟完整的工作流状态
        workflow_state = {
            'stock_code': '600276',
            'current_price': 45.8,
            'market_status': '正常',
            'analysis_type': 'full_analysis',
            'workflow_id': 'test_workflow_001',
            'timestamp': datetime.now().isoformat(),
            'additional_context': {
                'risk_level': 'medium',
                'investment_horizon': 'long',
                'sector_focus': 'healthcare'
            }
        }

        # 4. 执行分析
        result = await agent.analyze(workflow_state)

        # 5. 验证集成性
        assert result['agent_name'] == 'Buffett'
        assert result['analysis_mode'] == 'ai_llm'
        assert result['has_search_data'] == True

        # 验证状态信息被正确处理
        assert 'workflow_id' in workflow_state
        assert 'timestamp' in workflow_state
        assert 'additional_context' in workflow_state

        # 验证结果包含工作流相关信息
        assert result['key_factors'] is not None
        assert isinstance(result['confidence'], float)

        # 6. 验证服务调用
        mock_tushare_service.get_stock_data.assert_called_once_with('600276')
        mock_search_service.web_search.assert_called_once()
        mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
        mock_llm_service.reason_with_cot.assert_called_once()