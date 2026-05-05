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
    - DeepSeek: deepseek-v4-flash, deepseek-v4-pro
    - 智谱AI: glm-4-flash, glm-4-plus, glm-4-air
    - 本地模型: 通过OpenAI兼容接口
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化LLM服务

        Args:
            config: LLM配置字典
        """
        if config:
            # 如果提供了config，但api_key为None，则自动获取
            if not config.get("api_key"):
                provider = config.get("provider", settings.llm_provider)
                config["api_key"] = self._get_api_key_for_provider(provider)
            self.config = config
        else:
            self.config = self._get_default_config()
        self._client_cache: Optional[httpx.AsyncClient] = None

    def _get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """根据provider获取API密钥"""
        if provider == "openai":
            return settings.openai_api_key
        elif provider == "anthropic":
            return settings.anthropic_api_key
        elif provider == "deepseek":
            return settings.deepseek_api_key
        elif provider == "glm":
            return settings.glm_api_key
        return None

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
        return self._get_api_key_for_provider(settings.llm_provider)

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

    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """调用OpenAI API"""
        api_key = self.config.get("api_key")
        if not api_key:
            raise LLMServiceError("未配置OpenAI API密钥")

        try:
            response = await self._client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.get("model", "gpt-4o"),
                    "messages": messages,
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 4000),
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise LLMRateLimitError("OpenAI API速率限制")
            elif e.response.status_code == 400:
                raise LLMTokenLimitError("Token超限")
            else:
                raise LLMServiceError(f"OpenAI API错误: {e.response.status_code}")
        except httpx.RequestError as e:
            raise LLMServiceError(f"网络错误: {str(e)}")

    async def _call_anthropic(self, messages: List[Dict[str, str]]) -> str:
        """调用Anthropic Claude API"""
        api_key = self.config.get("api_key")
        if not api_key:
            raise LLMServiceError("未配置Anthropic API密钥")

        # Convert message format
        system_msg = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        try:
            response = await self._client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.config.get("model", "claude-3-5-sonnet-20241022"),
                    "max_tokens": self.config.get("max_tokens", 4000),
                    "system": system_msg,
                    "messages": user_messages
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise LLMRateLimitError("Anthropic API速率限制")
            elif e.response.status_code == 400:
                raise LLMTokenLimitError("Token超限")
            else:
                raise LLMServiceError(f"Anthropic API错误: {e.response.status_code}")
        except httpx.RequestError as e:
            raise LLMServiceError(f"网络错误: {str(e)}")

    async def _call_deepseek(self, messages: List[Dict[str, str]]) -> str:
        """调用DeepSeek API（OpenAI兼容）"""
        api_key = self.config.get("api_key")
        if not api_key:
            raise LLMServiceError("未配置DeepSeek API密钥")

        base_url = self.config.get("base_url", "https://api.deepseek.com")

        try:
            response = await self._client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.get("model", "deepseek-v4-flash"),
                    "messages": messages,
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 4000),
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise LLMRateLimitError("DeepSeek API速率限制")
            elif e.response.status_code == 400:
                raise LLMTokenLimitError("Token超限")
            else:
                raise LLMServiceError(f"DeepSeek API错误: {e.response.status_code}")
        except httpx.RequestError as e:
            raise LLMServiceError(f"网络错误: {str(e)}")

    async def _call_glm(self, messages: List[Dict[str, str]]) -> str:
        """调用智谱AI GLM API（OpenAI兼容）"""
        api_key = self.config.get("api_key")
        if not api_key:
            raise LLMServiceError("未配置智谱AI API密钥")

        base_url = self.config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")

        try:
            response = await self._client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.get("model", "glm-4-flash"),
                    "messages": messages,
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 4000)
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise LLMRateLimitError("智谱AI API速率限制")
            elif e.response.status_code == 400:
                raise LLMTokenLimitError("Token超限")
            else:
                raise LLMServiceError(f"智谱AI API错误: {e.response.status_code}")
        except httpx.RequestError as e:
            raise LLMServiceError(f"网络错误: {str(e)}")

    async def _call_openai_compatible(self, messages: List[Dict[str, str]]) -> str:
        """调用OpenAI兼容接口（本地模型）"""
        base_url = self.config.get("base_url", "http://localhost:11434/v1")

        try:
            response = await self._client.post(
                f"{base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.config.get("model", "llama2"),
                    "messages": messages,
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 4000)
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMServiceError(f"本地模型调用失败: {str(e)}")

    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """统一的LLM调用入口"""
        provider = self.config.get("provider", "openai")

        if provider == "openai":
            return await self._call_openai(messages)
        elif provider == "anthropic":
            return await self._call_anthropic(messages)
        elif provider == "deepseek":
            return await self._call_deepseek(messages)
        elif provider == "glm":
            return await self._call_glm(messages)
        else:
            return await self._call_openai_compatible(messages)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON code block
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to extract braces content
        brace_match = re.search(r'\{.*\}', response, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        raise LLMInvalidResponseError(f"无法解析JSON响应: {response[:200]}...")

    def _shorten_prompt(self, prompt: str) -> str:
        """缩短Prompt"""
        max_length = 3000
        if len(prompt) > max_length:
            return prompt[:max_length] + "\n\n[内容已截断...]"
        return prompt

    async def reason_with_cot(self, prompt: str, retry: int = 3) -> Dict[str, Any]:
        """使用思维链进行推理（带重试）"""
        messages = [
            {"role": "system", "content": "你是一位专业的投资分析师，擅长深度思考和严谨推理。"},
            {"role": "user", "content": prompt}
        ]

        for attempt in range(retry):
            try:
                response = await self._call_llm(messages)
                return self._parse_json_response(response)
            except LLMRateLimitError:
                if attempt < retry - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except LLMTokenLimitError:
                prompt = self._shorten_prompt(prompt)
            except LLMInvalidResponseError:
                if attempt >= retry - 1:
                    raise
            except LLMServiceError:
                raise

        raise LLMServiceError("重试次数耗尽")
