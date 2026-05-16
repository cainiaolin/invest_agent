"""
搜索增强端到端流程测试（简化版）

测试完整的数据获取、搜索增强、知识库查询和LLM分析流程
包括正常流程和降级机制测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime


class TestBuffetSearchEnhancedFullFlow:
    """BuffetSearchAgent完整流程测试"""

    @pytest.mark.asyncio
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_enriched_stock_data')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.knowledge')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.llm')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_search_context')
    async def test_buffet_search_enhanced_full_flow(
        self,
        mock_search_context,
        mock_llm,
        mock_knowledge,
        mock_stock_data
    ):
        """
        测试完整的搜索增强流程

        验证从数据获取到搜索增强再到LLM分析的完整流程
        """
        # 1. 模拟数据获取
        mock_stock_data.return_value = {
            'symbol': '600519',
            'name': '贵州茅台',
            'price': 1500.0,
            'pe': 25.5,
            'pb': 12.8,
            'roe': 25.8,
            'market_cap': '1.8万亿',
            'revenue': 1200,
            'profit': 600
        }

        mock_knowledge.load_knowledge.return_value = {
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
        }

        mock_search_context.return_value = {
            'company_analysis': '贵州茅台在白酒行业具有绝对领导地位，品牌护城河宽阔',
            'industry_trends': '高端白酒需求稳定增长',
            'competitive_landscape': '与五粮液等竞争对手相比具有明显优势',
            'reliability_score': 0.85
        }

        # 2. 模拟LLM响应
        mock_llm.reason_with_cot.return_value = {
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
        }

        # 3. 创建BuffetSearchAgent实例
        from app.agents.value.buffet_search_agent import BuffetSearchAgent

        # 创建服务mock
        mock_tushare = Mock()
        mock_search = Mock()
        mock_llm_service = Mock()
        mock_knowledge_service = Mock()

        agent = BuffetSearchAgent(
            tushare_service=mock_tushare,
            search_service=mock_search,
            llm_service=mock_llm_service,
            knowledge_service=mock_knowledge_service
        )

        # 4. 执行分析
        state = {
            'stock_code': '600519',
            'current_price': 1500.0,
            'market_status': '正常',
            'analysis_type': 'full_analysis'
        }

        result = await agent.analyze(state)

        # 5. 验证结果包含必要字段
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

        # 6. 验证结果质量
        assert result['confidence'] > 0.5  # 置信度应该较高
        assert len(result['key_factors']) > 0  # 应该有关键因素分析

        # 7. 验证方法调用
        mock_stock_data.assert_called_once_with('600519')
        mock_knowledge.load_knowledge.assert_called_once_with('Buffett')
        mock_search_context.assert_called_once()
        mock_llm.reason_with_cot.assert_called_once()


class TestSearchFallbackMechanism:
    """搜索降级机制测试"""

    @pytest.mark.asyncio
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_enriched_stock_data')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.knowledge')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.llm')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_search_context')
    async def test_search_fallback_mechanism(
        self,
        mock_search_context,
        mock_llm,
        mock_knowledge,
        mock_stock_data
    ):
        """
        测试搜索服务失败时的降级机制

        验证当搜索服务不可用时，系统会降级到基础LLM分析
        """
        # 1. 模拟数据获取
        mock_stock_data.return_value = {
            'symbol': '000001',
            'name': '平安银行',
            'price': 10.5,
            'pe': 5.2,
            'pb': 0.8,
            'roe': 8.5,
            'market_cap': '2000亿'
        }

        mock_knowledge.load_knowledge.return_value = {
            'investment_philosophy': '寻找具有持久竞争优势的企业',
            'key_principles': ['护城河理论', '安全边际'],
            'case_studies': []
        }

        # 搜索服务会失败
        mock_search_context.side_effect = Exception("搜索服务暂时不可用")

        # 2. 模拟LLM响应（降级后的基础分析）
        mock_llm.reason_with_cot.return_value = {
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
        }

        # 3. 创建BuffetSearchAgent实例
        from app.agents.value.buffet_search_agent import BuffetSearchAgent

        # 创建服务mock
        mock_tushare = Mock()
        mock_search = Mock()
        mock_llm_service = Mock()
        mock_knowledge_service = Mock()

        agent = BuffetSearchAgent(
            tushare_service=mock_tushare,
            search_service=mock_search,
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

        # 7. 验证方法调用
        mock_stock_data.assert_called_once_with('000001')
        mock_knowledge.load_knowledge.assert_called_once_with('Buffett')
        mock_search_context.assert_called_once()
        mock_llm.reason_with_cot.assert_called_once()


class TestBuffetSearchStrategyValidation:
    """巴菲特搜索策略验证测试"""

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
        from app.agents.value.buffet_search_agent import BuffetSearchAgent

        agent = BuffetSearchAgent(
            tushare_service=mock_tushare,
            search_service=mock_search,
            llm_service=mock_llm,
            knowledge_service=mock_knowledge
        )

        # 获取搜索策略
        strategy = agent.get_search_strategy()

        # 验证策略配置符合巴菲特投资哲学
        from app.models.search_strategy import SearchStrategy
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