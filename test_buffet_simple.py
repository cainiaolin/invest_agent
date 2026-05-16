"""
简单的BuffetSearchAgent测试脚本
"""

import asyncio
from unittest.mock import Mock
from app.agents.value.buffet_search_agent import BuffetSearchAgent


async def test_basic_functionality():
    """测试基本功能"""
    print("测试开始...")

    # 创建模拟服务
    mock_tushare = Mock()
    mock_search = Mock()
    mock_llm = Mock()
    mock_knowledge = Mock()

    # 创建Agent
    agent = BuffetSearchAgent(
        tushare_service=mock_tushare,
        search_service=mock_search,
        llm_service=mock_llm,
        knowledge_service=mock_knowledge
    )

    # 测试基本属性
    print(f"Name: {agent.name}")
    print(f"Style: {agent.style}")

    # 测试搜索策略
    strategy = agent.get_search_strategy()
    print(f"Search Strategy:")
    print(f"  search_basic_info: {strategy.search_basic_info}")
    print(f"  search_market_sentiment: {strategy.search_market_sentiment}")
    print(f"  search_industry: {strategy.search_industry}")
    print(f"  search_competitors: {strategy.search_competitors}")
    print(f"  time_horizon: {strategy.time_horizon}")
    print(f"  min_reliability: {strategy.min_reliability}")
    print(f"  max_results_per_source: {strategy.max_results_per_source}")

    # 测试COT prompt构建
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

    prompt = agent._build_cot_prompt(stock_data, knowledge)
    print(f"\nCOT Prompt Length: {len(prompt)}")
    print(f"Prompt Preview: {prompt[:200]}...")

    print("\n所有基本测试通过！")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())