"""
直接运行端到端测试（不依赖pytest）
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# 添加项目路径
sys.path.append('.')

from unittest.mock import patch
from app.agents.value.buffet_search_agent import BuffetSearchAgent
from app.models.search_strategy import SearchStrategy


async def test_buffet_search_enhanced_full_flow():
    """
    测试完整的搜索增强流程
    """
    print("开始测试BuffetSearchAgent完整流程...")

    # 1. 模拟数据获取
    mock_stock_data = {
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

    mock_knowledge = {
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

    mock_search_context = {
        'company_analysis': '贵州茅台在白酒行业具有绝对领导地位，品牌护城河宽阔',
        'industry_trends': '高端白酒需求稳定增长',
        'competitive_landscape': '与五粮液等竞争对手相比具有明显优势',
        'reliability_score': 0.85
    }

    mock_llm_response = {
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

    # 2. 创建服务mock
    mock_tushare = Mock()
    mock_tushare.get_stock_fundamentals = AsyncMock(return_value=mock_stock_data)

    mock_search = Mock()
    mock_search.web_search = AsyncMock(return_value=mock_search_context)

    mock_llm_service = Mock()
    mock_llm_service.reason_with_cot = AsyncMock(return_value=mock_llm_response)

    mock_knowledge_service = Mock()
    mock_knowledge_service.load_knowledge = AsyncMock(return_value=mock_knowledge)

    # 3. 创建BuffetSearchAgent实例
    agent = BuffetSearchAgent(
        tushare_service=mock_tushare,
        search_service=mock_search,
        llm_service=mock_llm_service,
        knowledge_service=mock_knowledge_service
    )

    # 4. 执行分析（使用patch来避免内部调用问题）
    state = {
        'stock_code': '600519',
        'current_price': 1500.0,
        'market_status': '正常',
        'analysis_type': 'full_analysis'
    }

    with patch.object(agent, '_get_enriched_stock_data', return_value=mock_stock_data):
        result = await agent.analyze(state)

    # 5. 验证结果
    print("验证结果...")
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

    # 验证结果质量
    assert result['confidence'] > 0.5  # 置信度应该较高
    assert len(result['key_factors']) > 0  # 应该有关键因素分析

    # 验证方法调用
    mock_tushare.get_stock_fundamentals.assert_called_once_with('600519')
    mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
    mock_search.web_search.assert_called_once()
    mock_llm_service.reason_with_cot.assert_called_once()

    print("测试通过！BuffetSearchAgent完整流程测试成功")
    print(f"结果: {result['action']}, 置信度: {result['confidence']}")
    return result


async def test_search_fallback_mechanism():
    """
    测试搜索服务失败时的降级机制
    """
    print("\n开始测试搜索服务降级机制...")

    # 1. 模拟数据获取
    mock_stock_data = {
        'symbol': '000001',
        'name': '平安银行',
        'price': 10.5,
        'pe': 5.2,
        'pb': 0.8,
        'roe': 8.5,
        'market_cap': '2000亿'
    }

    mock_knowledge = {
        'investment_philosophy': '寻找具有持久竞争优势的企业',
        'key_principles': ['护城河理论', '安全边际'],
        'case_studies': []
    }

    mock_llm_response = {
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

    # 2. 创建会失败的搜索服务
    class FailingSearchService:
        async def web_search(self, query):
            raise Exception("搜索服务暂时不可用")

    failing_search = FailingSearchService()

    # 3. 创建其他服务mock
    mock_tushare = Mock()
    mock_tushare.get_stock_fundamentals = AsyncMock(return_value=mock_stock_data)

    mock_llm_service = Mock()
    mock_llm_service.reason_with_cot = AsyncMock(return_value=mock_llm_response)

    mock_knowledge_service = Mock()
    mock_knowledge_service.load_knowledge = AsyncMock(return_value=mock_knowledge)

    # 4. 创建BuffetSearchAgent实例
    agent = BuffetSearchAgent(
        tushare_service=mock_tushare,
        search_service=failing_search,
        llm_service=mock_llm_service,
        knowledge_service=mock_knowledge_service
    )

    # 5. 执行分析（使用patch来避免内部调用问题）
    state = {
        'stock_code': '000001',
        'current_price': 10.5,
        'market_status': '正常',
        'analysis_type': 'full_analysis'
    }

    with patch.object(agent, '_get_enriched_stock_data', return_value=mock_stock_data):
        result = await agent.analyze(state)

    # 6. 验证降级机制生效
    assert result['analysis_mode'] in ['ai_llm', 'rule_fallback']
    assert result['has_search_data'] == False  # 搜索应该失败

    # 验证基础功能仍然正常工作
    required_fields = [
        'agent_name', 'action', 'confidence', 'reasoning'
    ]

    for field in required_fields:
        assert field in result, f"缺少必需字段: {field}"

    assert result['agent_name'] == 'Buffett'
    assert result['action'] in ['BUY', 'HOLD', 'SELL']
    assert 0 <= result['confidence'] <= 1
    assert isinstance(result['reasoning'], str)

    # 验证方法调用
    mock_tushare.get_stock_fundamentals.assert_called_once_with('000001')
    mock_knowledge_service.load_knowledge.assert_called_once_with('Buffett')
    mock_llm_service.reason_with_cot.assert_called_once()

    print("测试通过！搜索服务降级机制测试成功")
    print(f"降级模式: {result['analysis_mode']}, 结果: {result['action']}")
    return result


async def test_buffet_search_strategy():
    """
    测试巴菲特搜索策略配置
    """
    print("\n开始测试巴菲特搜索策略配置...")

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

    print("测试通过！巴菲特搜索策略配置测试成功")
    print(f"策略配置: 时间范围={strategy.time_horizon}天, 可信度要求={strategy.min_reliability}")
    return strategy


async def main():
    """
    运行所有测试
    """
    print("开始端到端测试...")

    try:
        # 测试1: 完整流程
        result1 = await test_buffet_search_enhanced_full_flow()

        # 测试2: 降级机制
        result2 = await test_search_fallback_mechanism()

        # 测试3: 策略配置
        strategy = await test_buffet_search_strategy()

        print("\n🎉 所有测试通过！")
        print(f"完整流程测试: {result1['action']} (置信度: {result1['confidence']})")
        print(f"降级机制测试: {result2['action']} (模式: {result2['analysis_mode']})")
        print(f"策略配置测试: 时间范围={strategy.time_horizon}天")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())

    if success:
        print("\n端到端测试全部通过！")
        exit(0)
    else:
        print("\n端到端测试失败！")
        exit(1)