"""端到端测试 - AI模式完整流程"""

import pytest
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.agents.value.llm_graham_agent import LLMGrahamAgent
from app.services.tushare_service import TushareService
from app.core.config import settings


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.openai_api_key, reason="需要OPENAI_API_KEY")
async def test_llm_graham_full_analysis():
    """测试完整的LLM格雷厄姆分析流程"""

    # 准备服务
    llm_service = LLMService({
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": settings.openai_api_key,
        "temperature": 0.7
    })

    knowledge_service = KnowledgeService("knowledge")
    tushare_service = TushareService(settings.tushare_token)

    # 创建Agent
    agent = LLMGrahamAgent(
        tushare_service=tushare_service,
        llm_service=llm_service,
        knowledge_service=knowledge_service
    )

    # 执行分析
    state = {"stock_code": "600519"}
    result = await agent.analyze(state)

    # 验证结果
    assert "agent_name" in result
    assert "Benjamin Graham" in result["agent_name"]
    assert "action" in result
    assert result["action"] in ["buy", "sell", "hold"]
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
    assert "analysis_mode" in result
    assert result["analysis_mode"] == "ai_llm"

    # 如果有思维过程，验证其结构
    if "thought_process" in result:
        assert isinstance(result["thought_process"], dict)

    # 清理
    await llm_service.close()


@pytest.mark.asyncio
async def test_knowledge_loading():
    """测试知识文件加载"""
    knowledge_service = KnowledgeService("knowledge")

    graham_knowledge = await knowledge_service.load_knowledge("graham")

    assert "metadata" in graham_knowledge
    assert graham_knowledge["metadata"]["master_name"] == "graham"
    assert "core_philosophy" in graham_knowledge
    assert "decision_rules" in graham_knowledge
