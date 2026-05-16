"""
BuffetSearchAgent集成测试

测试巴菲特投资哲学的搜索增强Agent功能
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.agents.value.buffet_search_agent import BuffetSearchAgent
from app.models.search_strategy import SearchStrategy
from app.agents.search_enhanced_agent import SearchEnhancedAgent


class TestBuffetSearchAgent:
    """BuffetSearchAgent测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建模拟的依赖服务
        self.mock_tushare = Mock()
        self.mock_search = Mock()
        self.mock_llm = Mock()
        self.mock_knowledge = Mock()

        # 创建Agent实例
        self.agent = BuffetSearchAgent(
            tushare_service=self.mock_tushare,
            search_service=self.mock_search,
            llm_service=self.mock_llm,
            knowledge_service=self.mock_knowledge
        )

    def test_buffet_search_agent_properties(self):
        """测试BuffetSearchAgent基本属性"""
        # 测试name属性
        assert self.agent.name == "Buffett"

        # 测试style属性
        assert self.agent.style == "价值投资 - 护城河与安全边际"

        # 测试继承关系
        assert isinstance(self.agent, SearchEnhancedAgent)

        # 测试基础方法存在
        assert hasattr(self.agent, 'get_search_strategy')
        assert hasattr(self.agent, '_build_cot_prompt')
        assert hasattr(self.agent, 'analyze_with_enhanced_context')

    def test_buffet_search_strategy(self):
        """测试巴菲特搜索策略配置"""
        strategy = self.agent.get_search_strategy()

        # 验证策略类型
        assert isinstance(strategy, SearchStrategy)

        # 验证搜索策略配置
        assert strategy.search_basic_info is True
        assert strategy.search_market_sentiment is False
        assert strategy.search_industry is True
        assert strategy.search_competitors is True
        assert strategy.time_horizon == 30
        assert strategy.min_reliability == 0.7
        assert strategy.max_results_per_source == 15

    def test_build_cot_prompt(self):
        """测试构建巴菲特风格的Chain of Thought Prompt"""
        # 模拟数据
        stock_data = {
            'name': '腾讯控股',
            'code': '00700.HK',
            'price': 320.5,
            'market_cap': '3000亿',
            'pe': 15.2,
            'pb': 2.1,
            'roe': 18.5
        }

        knowledge = {
            'investment_philosophy': '价值投资，寻找护城河宽阔的企业',
            'key_principles': ['安全边际', '护城河', '管理层质量', '长期持有'],
            'case_studies': ['可口可乐', '美国运通', '富国银行']
        }

        search_context = {
            'company_analysis': '腾讯在社交游戏领域具有领先地位',
            'industry_trends': '元宇宙和游戏行业快速发展',
            'competitive_landscape': '与字节跳动竞争激烈'
        }

        # 构建prompt
        prompt = self.agent._build_cot_prompt(stock_data, knowledge, search_context)

        # 验证prompt内容
        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # 验证包含巴菲特投资哲学
        assert '巴菲特' in prompt or '护城河' in prompt or '价值投资' in prompt

        # 验证包含搜索增强信息
        assert '腾讯' in prompt
        assert '社交' in prompt or '游戏' in prompt

        # 验证重点关注领域
        assert '护城河' in prompt
        assert '管理层' in prompt
        assert '财务质量' in prompt
        assert '估值' in prompt

    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_enriched_stock_data')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.knowledge')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent.llm')
    @patch('app.agents.value.buffet_search_agent.BuffetSearchAgent._get_search_context')
    async def test_analyze(self, mock_search_context, mock_llm, mock_knowledge, mock_stock_data):
        """测试分析功能"""
        # 模拟数据获取
        mock_stock_data.return_value = {
            'name': '腾讯控股',
            'code': '00700.HK',
            'price': 320.5,
            'market_cap': '3000亿',
            'pe': 15.2,
            'pb': 2.1,
            'roe': 18.5
        }

        mock_knowledge.load_knowledge.return_value = {
            'investment_philosophy': '价值投资，寻找护城河宽阔的企业',
            'key_principles': ['安全边际', '护城河', '管理层质量', '长期持有'],
            'case_studies': ['可口可乐', '美国运通', '富国银行']
        }

        mock_search_context.return_value = '腾讯在社交游戏领域具有领先地位'

        # 模拟LLM响应
        mock_llm.reason_with_cot.return_value = {
            'action': 'BUY',
            'confidence': 0.85,
            'reasoning': '护城河宽阔，估值合理',
            'key_metrics': {
                'pe': 15.2,
                'pb': 2.1,
                'roe': 18.5
            },
            'key_factors': ['护城河', '管理层优秀', '估值合理'],
            'thought_process': '详细的思考过程'
        }

        # 准备测试数据
        state = {
            'stock_code': '00700.HK',
            'current_price': 320.5,
            'market_status': '正常'
        }

        # 调用方法
        result = await self.agent.analyze(state)

        # 验证返回结果
        assert isinstance(result, dict)
        assert 'action' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        assert 'key_metrics' in result
        assert 'key_factors' in result
        assert 'thought_process' in result
        assert result['action'] == 'BUY'
        assert result['confidence'] == 0.85
        assert result['search_enhanced'] is True

        # 验证方法调用
        mock_stock_data.assert_called_once_with('00700.HK')
        mock_knowledge.load_knowledge.assert_called_once_with('Buffett')
        mock_search_context.assert_called_once_with('00700.HK', mock_stock_data.return_value)

    def test_cot_prompt_with_minimal_context(self):
        """测试最小上下文下的COT prompt构建"""
        stock_data = {
            'name': '测试公司',
            'code': 'TEST001',
            'price': 100.0
        }

        knowledge = {
            'investment_philosophy': '价值投资基础',
            'key_principles': ['护城河', '安全边际']
        }

        # 不提供搜索上下文
        prompt = self.agent._build_cot_prompt(stock_data, knowledge, "")

        # 验证prompt仍然能构建
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '测试公司' in prompt

    def test_cot_prompt_with_complex_knowledge(self):
        """测试复杂知识库下的COT prompt构建"""
        stock_data = {
            'name': '伯克希尔哈撒韦',
            'code': 'BRK.A',
            'price': 500000.0,
            'pe': 18.5,
            'pb': 1.2,
            'roe': 15.8
        }

        knowledge = {
            'investment_philosophy': '寻找具有持久竞争优势的企业',
            'key_principles': [
                '护城河理论',
                '管理层质量评估',
                '财务健康状况分析',
                '安全边际计算',
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
            ],
            'risk_factors': [
                '估值过高风险',
                '行业变革风险',
                '管理层变动风险'
            ]
        }

        search_context = {
            'company_analysis': '保险业务稳定，现金充足',
            'industry_trends': '保险行业竞争加剧',
            'competitive_landscape': '与其他保险巨头竞争'
        }

        prompt = self.agent._build_cot_prompt(stock_data, knowledge, search_context)

        # 验证复杂知识被正确整合
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # 应该是较长的prompt

        # 验证包含关键元素
        assert '伯克希尔哈撒韦' in prompt
        assert '护城河' in prompt
        assert '可口可乐' in prompt or '美国运通' in prompt
        assert '保险' in prompt
        assert '管理层' in prompt
        assert '估值' in prompt