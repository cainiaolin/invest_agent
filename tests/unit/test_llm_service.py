"""测试LLM服务"""

import pytest
from app.services.llm_service import LLMService, LLMServiceError, LLMRateLimitError


@pytest.mark.asyncio
async def test_openai_rate_limit_error():
    """测试速率限制错误"""
    service = LLMService({"provider": "openai", "api_key": "test-key"})

    with pytest.raises(LLMServiceError):
        await service._call_openai([{"role": "user", "content": "test"}])

