#!/usr/bin/env python3
"""
验证修复的脚本
"""
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_llm_buffet_agent():
    """测试LLMBuffetAgent的修复"""
    print("开始测试LLMBuffetAgent修复...")

    try:
        from app.agents.value.llm_buffet_agent import LLMBuffetAgent
        from app.core.state import AnalysisState

        # 创建模拟的依赖服务
        mock_tushare = Mock()
        mock_tushare.get_stock_fundamentals = AsyncMock(return_value={
            'symbol': '600000',
            'name': '浦发银行',
            'price': 10.0,
            'income': 1000000000,  # 添加缺失的字段
            'metrics': {
                'pe_ratio': 8.5,
                'pb_ratio': 0.9,
                'roe': 15.0,
                'debt_ratio': 30.0,
                'current_ratio': 2.5,
                'net_margin': 0.15,
            },
            'moat_indicators': {
                'brand_strength': 8,
                'market_share': 25.0,
                'competitive_advantage': True,
            },
        })

        mock_llm = Mock()
        mock_llm.reason_with_cot = AsyncMock(return_value={
            'action': 'BUY',
            'confidence': 0.85,
            'reasoning': '护城河宽阔，估值合理',
            'key_metrics': {
                'pe': 8.5,
                'pb': 0.9,
                'roe': 15.0
            },
            'key_factors': ['护城河', '管理层优秀', '估值合理'],
            'thought_process': '详细的思考过程'
        })
        mock_llm.config = {'model': 'test-model', 'provider': 'test'}

        mock_knowledge = Mock()
        mock_knowledge.load_knowledge = AsyncMock(return_value={
            'philosophy': '价值投资，寻找护城河宽阔的企业',
            'principles': ['安全边际', '护城河', '管理层质量', '长期持有']
        })

        # 创建Agent实例
        agent = LLMBuffetAgent(
            tushare_service=mock_tushare,
            llm_service=mock_llm,
            knowledge_service=mock_knowledge,
            master_name='Buffett'
        )

        # 准备测试数据
        state = AnalysisState({
            'stock_code': '600000',
            'current_price': 10.0,
            'market_status': '正常'
        })

        # 执行分析
        result = await agent.analyze(state)

        print("LLMBuffetAgent.analyze 成功执行")
        print(f"返回结果: {result}")

        # 验证关键结果
        assert 'action' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        assert result['action'] == 'BUY'
        assert result['confidence'] == 0.85

        print("所有验证通过!")
        return True

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sync_methods():
    """测试同步方法"""
    print("开始测试同步方法...")

    try:
        from app.agents.value.llm_buffet_agent import LLMBuffetAgent

        # 创建模拟的依赖服务
        mock_tushare = Mock()
        mock_llm = Mock()
        mock_knowledge = Mock()

        # 创建Agent实例
        agent = LLMBuffetAgent(
            tushare_service=mock_tushare,
            llm_service=mock_llm,
            knowledge_service=mock_knowledge,
            master_name='Buffett'
        )

        # 测试基本属性
        assert agent.name == "Warren Buffett (AI)"
        assert agent.style == "AI增强的质量成长投资：结合LLM推理与巴菲特护城河理论"

        print("同步方法测试通过!")
        return True

    except Exception as e:
        print(f"同步方法测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 修复验证脚本 ===")

    # 测试同步方法
    sync_result = test_sync_methods()

    # 测试异步方法
    async_result = asyncio.run(test_llm_buffet_agent())

    print(f"\n=== 最终结果 ===")
    print(f"同步方法测试: {'通过' if sync_result else '失败'}")
    print(f"异步方法测试: {'通过' if async_result else '失败'}")

    if sync_result and async_result:
        print("所有测试通过! 修复成功!")
    else:
        print("部分测试失败，需要进一步检查")