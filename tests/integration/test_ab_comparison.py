"""A/B对比测试 - 规则引擎 vs AI Agent"""

import pytest
from app.agents import get_agent
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.services.tushare_service import TushareService
from app.core.config import settings


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.openai_api_key, reason="需要OPENAI_API_KEY")
async def test_graham_rule_vs_ai_comparison():
    """对比格雷厄姆规则引擎和AI Agent"""

    stock_code = "600519"

    # 规则引擎分析
    rule_agent = get_agent(
        "graham",
        mode="rule",
        tushare_service=TushareService(settings.tushare_token)
    )
    rule_result = await rule_agent.analyze({"stock_code": stock_code})

    # AI Agent分析
    llm_service = LLMService({
        "provider": "openai",
        "api_key": settings.openai_api_key
    })
    knowledge_service = KnowledgeService("knowledge")

    ai_agent = get_agent(
        "graham",
        mode="ai",
        tushare_service=TushareService(settings.tushare_token),
        llm_service=llm_service,
        knowledge_service=knowledge_service
    )
    ai_result = await ai_agent.analyze({"stock_code": stock_code})

    # 对比结果
    comparison = {
        "stock_code": stock_code,
        "rule_engine": {
            "action": rule_result["action"],
            "confidence": rule_result["confidence"]
        },
        "ai_agent": {
            "action": ai_result["action"],
            "confidence": ai_result["confidence"]
        },
        "agreement": rule_result["action"] == ai_result["action"]
    }

    print(f"\nA/B测试结果:")
    print(f"规则引擎: {comparison['rule_engine']}")
    print(f"AI Agent: {comparison['ai_agent']}")
    print(f"一致性: {comparison['agreement']}")

    # 清理
    await llm_service.close()

    # 断言两者都返回了有效结果
    assert rule_result["action"] in ["buy", "sell", "hold"]
    assert ai_result["action"] in ["buy", "sell", "hold"]
