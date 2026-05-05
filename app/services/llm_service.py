"""LLM服务 - 统一的LLM调用接口"""

import json
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings


class LLMServiceError(Exception):
    """LLM服务错误基类"""
    pass


class LLMRateLimitError(LLMServiceError):
    """速率限制错误"""
    pass


class LLMTokenLimitError(LLMServiceError):
    """Token超限错误"""
    pass


class LLMInvalidResponseError(LLMServiceError):
    """无效响应错误"""
    pass


class LLMService:
    """
    统一的LLM调用服务

    支持的模型：
    - OpenAI: GPT-4, GPT-4o, GPT-4o-mini
    - Anthropic: Claude 3.5 Sonnet, Claude 3 Opus
    - 本地模型: 通过OpenAI兼容接口
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化LLM服务

        Args:
            config: LLM配置字典
        """
        self.config = config or self._get_default_config()
        self._client_cache: Optional[httpx.AsyncClient] = None

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "api_key": self._get_api_key(),
            "temperature": 0.7,
            "max_tokens": 4000
        }

    def _get_api_key(self) -> Optional[str]:
        """根据provider获取API密钥"""
        provider = settings.llm_provider
        if provider == "openai":
            return settings.openai_api_key
        elif provider == "anthropic":
            return settings.anthropic_api_key
        return None

    @property
    def _client(self) -> httpx.AsyncClient:
        """获取或创建HTTP客户端"""
        if self._client_cache is None:
            self._client_cache = httpx.AsyncClient(timeout=60.0)
        return self._client_cache

    async def close(self):
        """关闭HTTP客户端"""
        if self._client_cache:
            await self._client_cache.aclose()
            self._client_cache = None
