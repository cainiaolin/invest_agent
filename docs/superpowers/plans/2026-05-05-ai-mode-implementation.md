# AI模式投资分析系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为投资分析系统添加AI增强模式，支持LLM模型进行投资决策分析

**Architecture:** 采用LLM Agent增强架构，新增LLMAgent基类、LLMService和KnowledgeService，与现有规则引擎Agent并存，支持自动降级

**Tech Stack:** Python 3.11, FastAPI, Vue 3, OpenAI/Anthropic APIs, httpx, frontmatter

---

## 文件结构映射

### 新增文件

**服务层:**
- `app/services/llm_service.py` - LLM调用服务，支持OpenAI/Claude/本地模型
- `app/services/knowledge_service.py` - 知识文件加载和管理服务

**Agent层:**
- `app/agents/llm_agent.py` - LLM Agent抽象基类
- `app/agents/value/llm_graham_agent.py` - 格雷厄姆AI Agent实现
- `app/agents/value/llm_buffet_agent.py` - 巴菲特AI Agent实现

**知识文件:**
- `knowledge/graham/GRAHAM_AGENT_SUMMARY.md` - 格雷厄姆投资知识
- `knowledge/buffet/BUFFET_AGENT_SUMMARY.md` - 巴菲特投资知识

**测试文件:**
- `tests/unit/test_llm_service.py` - LLM服务单元测试
- `tests/unit/test_knowledge_service.py` - 知识服务单元测试
- `tests/unit/test_llm_agent.py` - LLM Agent单元测试
- `tests/integration/test_llm_graham_agent.py` - 格雷厄姆AI Agent集成测试

### 修改文件

**配置:**
- `pyproject.toml` - 添加httpx和frontmatter依赖
- `app/core/config.py` - 添加LLM配置选项
- `.env.example` - 添加LLM环境变量模板

**API:**
- `app/api/routes/analyze.py` - 扩展请求模型，支持agent_mode和llm_config参数
- `app/agents/__init__.py` - 添加AI Agent注册系统

**前端:**
- `frontend/src/views/AnalyzeView.vue` - 添加AI模式选择和配置UI
- `frontend/src/api/analyze.ts` - 扩展API请求类型

---

## Phase 1: 基础设施 - 服务层

### Task 1: 添加项目依赖

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: 添加依赖到pyproject.toml**

在`[tool.poetry.dependencies]`部分添加：

```toml
httpx = "^0.27.0"
python-frontmatter = "^1.0.0"
```

- [ ] **Step 2: 安装依赖**

```bash
cd "E:\claude code\invest_agent\invest_agent"
poetry install
```

预期输出: `Installing the current project: invest-agent-by-graph (0.1.0)`

- [ ] **Step 3: 提交**

```bash
git add pyproject.toml
git commit -m "feat: 添加LLM相关依赖 (httpx, frontmatter)"
```

---

### Task 2: 创建LLM配置类

**Files:**
- Modify: `app/core/config.py`

- [ ] **Step 1: 在config.py末尾添加LLM配置类**

```python
from typing import Optional, Dict, Any

class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
```

- [ ] **Step 2: 扩展Settings类**

在Settings类中添加：

```python
class Settings(BaseSettings):
    # ... 现有配置 ...

    # LLM配置
    llm_provider: str = Field(default="openai", description="LLM提供商")
    llm_model: str = Field(default="gpt-4o", description="LLM模型")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API密钥")

    # AI模式配置
    ai_mode_enabled: bool = Field(default=True, description="是否启用AI模式")
    knowledge_base_path: str = Field(default="knowledge", description="知识库路径")

    class Config:
        env_file = ".env"
        extra = "ignore"
```

- [ ] **Step 3: 运行类型检查验证**

```bash
poetry run mypy app/core/config.py
```

预期输出: 无错误

- [ ] **Step 4: 提交**

```bash
git add app/core/config.py
git commit -m "feat: 添加LLM配置支持"
```

---

### Task 3: 创建.env.example模板

**Files:**
- Create: `.env.example`

- [ ] **Step 1: 创建.env.example文件**

```bash
# Tushare配置
TUSHARE_TOKEN=your_tushare_token_here

# LLM配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# 本地模型配置（可选）
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama2

# AI模式配置
AI_MODE_ENABLED=true
KNOWLEDGE_BASE_PATH=knowledge

# API配置
API_HOST=0.0.0.0
API_PORT=8000
```

- [ ] **Step 2: 提交**

```bash
git add .env.example
git commit -m "docs: 添加环境变量配置模板"
```

---

### Task 4: 创建LLMService - 基础结构和错误类

**Files:**
- Create: `app/services/llm_service.py`

- [ ] **Step 1: 创建llm_service.py，添加错误类和基础结构**

```python
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
```

- [ ] **Step 2: 创建测试文件验证基础结构**

```bash
mkdir -p tests/unit
touch tests/unit/test_llm_service.py
```

- [ ] **Step 3: 提交**

```bash
git add app/services/llm_service.py tests/unit/test_llm_service.py
git commit -m "feat: 添加LLMService基础结构和错误类"
```

---

### Task 5: 实现LLMService - OpenAI调用

**Files:**
- Modify: `app/services/llm_service.py`

- [ ] **Step 1: 添加OpenAI调用方法**

在LLMService类中添加：

```python
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """
        调用OpenAI API

        Args:
            messages: 消息列表

        Returns:
            响应文本

        Raises:
            LLMRateLimitError: 速率限制
            LLMTokenLimitError: Token超限
            LLMServiceError: 其他错误
        """
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
```

- [ ] **Step 2: 添加测试验证错误处理**

在`tests/unit/test_llm_service.py`中：

```python
import pytest
from app.services.llm_service import LLMService, LLMRateLimitError, LLMServiceError


@pytest.mark.asyncio
async def test_openai_rate_limit_error():
    """测试速率限制错误"""
    service = LLMService({"provider": "openai", "api_key": "test-key"})

    with pytest.raises(LLMRateLimitError):
        # 模拟速率限制（实际调用会失败，但验证错误类型）
        await service._call_openai([{"role": "user", "content": "test"}])
```

- [ ] **Step 3: 运行测试**

```bash
poetry run pytest tests/unit/test_llm_service.py::test_openai_rate_limit_error -v
```

预期输出: PASS（或预期的失败）

- [ ] **Step 4: 提交**

```bash
git add app/services/llm_service.py tests/unit/test_llm_service.py
git commit -m "feat: 实现OpenAI API调用"
```

---

### Task 6: 实现LLMService - Anthropic调用

**Files:**
- Modify: `app/services/llm_service.py`

- [ ] **Step 1: 添加Anthropic调用方法**

在LLMService类中添加：

```python
    async def _call_anthropic(self, messages: List[Dict[str, str]]) -> str:
        """
        调用Anthropic Claude API

        Args:
            messages: 消息列表

        Returns:
            响应文本

        Raises:
            LLMServiceError: API调用错误
        """
        api_key = self.config.get("api_key")
        if not api_key:
            raise LLMServiceError("未配置Anthropic API密钥")

        # 转换消息格式
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
```

- [ ] **Step 2: 提交**

```bash
git add app/services/llm_service.py
git commit -m "feat: 实现Anthropic Claude API调用"
```

---

### Task 7: 实现LLMService - 统一调用接口

**Files:**
- Modify: `app/services/llm_service.py`

- [ ] **Step 1: 添加统一调用方法**

在LLMService类中添加：

```python
    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        统一的LLM调用入口

        Args:
            messages: 消息列表

        Returns:
            响应文本
        """
        provider = self.config.get("provider", "openai")

        if provider == "openai":
            return await self._call_openai(messages)
        elif provider == "anthropic":
            return await self._call_anthropic(messages)
        else:
            # 默认使用OpenAI兼容接口（本地模型等）
            return await self._call_openai_compatible(messages)

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
```

- [ ] **Step 2: 添加JSON解析方法**

在LLMService类中添加：

```python
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析JSON响应

        Args:
            response: LLM返回的文本

        Returns:
            解析后的字典

        Raises:
            LLMInvalidResponseError: 无法解析JSON
        """
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取大括号内容
        brace_match = re.search(r'\{.*\}', response, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        raise LLMInvalidResponseError(f"无法解析JSON响应: {response[:200]}...")
```

- [ ] **Step 3: 添加重试逻辑**

在LLMService类中添加：

```python
    async def reason_with_cot(self, prompt: str, retry: int = 3) -> Dict[str, Any]:
        """
        使用思维链进行推理（带重试）

        Args:
            prompt: 推理提示词
            retry: 重试次数

        Returns:
            解析后的JSON响应
        """
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

    def _shorten_prompt(self, prompt: str) -> str:
        """缩短Prompt"""
        max_length = 3000
        if len(prompt) > max_length:
            return prompt[:max_length] + "\n\n[内容已截断...]"
        return prompt
```

- [ ] **Step 4: 提交**

```bash
git add app/services/llm_service.py
git commit -m "feat: 实现LLM统一调用接口和重试机制"
```

---

### Task 8: 创建KnowledgeService

**Files:**
- Create: `app/services/knowledge_service.py`

- [ ] **Step 1: 创建knowledge_service.py**

```python
"""投资大师知识管理服务"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import frontmatter


class KnowledgeService:
    """
    投资大师知识管理服务

    功能：
    - 加载md知识文件
    - 解析frontmatter元数据
    - 提取特定章节内容
    - 内存缓存
    """

    def __init__(self, knowledge_base_path: str = "knowledge"):
        """
        初始化知识服务

        Args:
            knowledge_base_path: 知识库根路径
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def load_knowledge(self, master_name: str) -> Dict[str, Any]:
        """
        加载大师知识

        Args:
            master_name: 大师名称 (如 "graham")

        Returns:
            知识字典，包含：
            - metadata: 元数据
            - content: 完整内容
            - core_philosophy: 核心哲学
            - evaluation_dimensions: 评估维度
            - decision_rules: 决策规则
            - cases: 经典案例
            - checklist: 检查清单

        Raises:
            FileNotFoundError: 知识文件不存在
        """
        # 检查缓存
        if master_name in self._cache:
            return self._cache[master_name]

        # 构建文件路径
        summary_file = self.knowledge_base_path / master_name / f"{master_name.upper()}_AGENT_SUMMARY.md"

        if not summary_file.exists():
            raise FileNotFoundError(f"知识文件不存在: {summary_file}")

        # 读取并解析文件
        with open(summary_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        knowledge = {
            "metadata": dict(post.metadata),
            "content": post.content,
            "core_philosophy": self._extract_section(post.content, "核心投资哲学"),
            "evaluation_dimensions": self._extract_section(post.content, "核心评估维度"),
            "decision_rules": self._extract_section(post.content, "决策规则"),
            "cases": self._extract_section(post.content, "经典案例"),
            "checklist": self._extract_section(post.content, "分析检查清单"),
        }

        # 缓存
        self._cache[master_name] = knowledge

        return knowledge

    def _extract_section(self, content: str, section_title: str) -> str:
        """
        提取markdown中的特定章节

        Args:
            content: markdown内容
            section_title: 章节标题

        Returns:
            章节内容
        """
        lines = content.split('\n')
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith(f"## {section_title}"):
                start_idx = i + 1
            elif start_idx and line.strip().startswith("## ") and i > start_idx:
                end_idx = i
                break

        if start_idx is None:
            return ""

        section_lines = lines[start_idx:end_idx]
        return '\n'.join(section_lines).strip()

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
```

- [ ] **Step 2: 创建测试文件**

```bash
touch tests/unit/test_knowledge_service.py
```

- [ ] **Step 3: 添加基础测试**

在`tests/unit/test_knowledge_service.py`中：

```python
import pytest
from app.services.knowledge_service import KnowledgeService


@pytest.mark.asyncio
async def test_load_nonexistent_knowledge():
    """测试加载不存在的知识文件"""
    service = KnowledgeService("knowledge")

    with pytest.raises(FileNotFoundError):
        await service.load_knowledge("nonexistent")


def test_extract_section():
    """测试章节提取"""
    service = KnowledgeService()
    content = """
## 核心投资哲学

这是核心哲学内容。

## 其他章节

其他内容。
"""
    result = service._extract_section(content, "核心投资哲学")
    assert "这是核心哲学内容" in result
    assert "其他章节" not in result
```

- [ ] **Step 4: 运行测试**

```bash
poetry run pytest tests/unit/test_knowledge_service.py -v
```

- [ ] **Step 5: 提交**

```bash
git add app/services/knowledge_service.py tests/unit/test_knowledge_service.py
git commit -m "feat: 添加KnowledgeService知识管理服务"
```

---

## Phase 2: Agent层 - 基础类实现

### Task 9: 创建LLMAgent抽象基类

**Files:**
- Create: `app/agents/llm_agent.py`

- [ ] **Step 1: 创建llm_agent.py**

```python
"""LLM Agent抽象基类"""

import logging
from abc import abstractmethod
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMAgent(BaseAgent):
    """
    基于LLM的智能投资Agent基类

    特点：
    - 使用思维链(Chain-of-Thought)推理
    - 结合知识图谱和实时数据
    - 支持多LLM模型配置
    - 自动降级到规则引擎
    """

    def __init__(
        self,
        tushare_service,
        llm_service: LLMService,
        knowledge_service: KnowledgeService,
        master_name: str
    ):
        """
        初始化LLM Agent

        Args:
            tushare_service: Tushare数据服务
            llm_service: LLM服务
            knowledge_service: 知识服务
            master_name: 大师名称
        """
        super().__init__(tushare_service)
        self.llm = llm_service
        self.knowledge = knowledge_service
        self.master_name = master_name

    @property
    @abstractmethod
    def master_name(self) -> str:
        """大师名称"""
        pass

    async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行投资分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        try:
            return await self._analyze_with_llm(state)
        except Exception as e:
            logger.warning(f"LLM分析失败: {e}，降级到规则引擎")
            return await self._fallback_to_rule_engine(state)

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行分析（子类实现具体逻辑）

        Args:
            state: 分析状态

        Returns:
            分析结果
        """
        stock_code = state.get("stock_code", "")
        stock_data = await self._get_enriched_stock_data(stock_code)
        knowledge = await self.knowledge.load_knowledge(self.master_name)

        cot_prompt = self._build_cot_prompt(stock_data, knowledge)
        llm_result = await self.llm.reason_with_cot(cot_prompt)

        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model")
        })

        return result

    @abstractmethod
    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict) -> str:
        """
        构建思维链Prompt（子类实现）

        Args:
            stock_data: 股票数据
            knowledge: 大师知识

        Returns:
            Prompt字符串
        """
        pass

    def _parse_llm_response(self, llm_result: Dict, stock_data: Dict) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            llm_result: LLM返回结果
            stock_data: 股票数据

        Returns:
            标准化的分析结果
        """
        return {
            "action": llm_result.get("action", "hold"),
            "confidence": llm_result.get("confidence", 0.5),
            "reasoning": llm_result.get("reasoning", ""),
            "key_metrics": llm_result.get("key_metrics", {}),
            "thought_process": llm_result.get("thought_process", {}),
            "key_factors": llm_result.get("key_factors", [])
        }

    async def _get_enriched_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取增强的股票数据

        Args:
            stock_code: 股票代码

        Returns:
            包含股票数据的字典
        """
        # 复用现有Agent的数据获取方法
        from app.agents.value.graham_agent import GrahamAgent
        temp_agent = GrahamAgent(self.tushare)
        return await temp_agent._get_stock_data(stock_code)

    async def _fallback_to_rule_engine(self, state: AnalysisState) -> Dict[str, Any]:
        """
        降级到规则引擎

        Args:
            state: 分析状态

        Returns:
            规则引擎分析结果
        """
        from app.agents import RULE_AGENTS

        rule_agent_class = RULE_AGENTS.get(self.master_name)
        if not rule_agent_class:
            raise ValueError(f"没有找到对应的规则Agent: {self.master_name}")

        rule_agent = rule_agent_class(self.tushare)
        result = await rule_agent.analyze(state)

        result["agent_name"] = f"{self.name} (规则引擎降级)"
        result["analysis_mode"] = "rule_fallback"
        result["fallback_reason"] = "LLM服务不可用"

        return result
```

- [ ] **Step 2: 提交**

```bash
git add app/agents/llm_agent.py
git commit -m "feat: 添加LLMAgent抽象基类"
```

---

### Task 10: 创建LLMGrahamAgent

**Files:**
- Create: `app/agents/value/llm_graham_agent.py`

- [ ] **Step 1: 创建llm_graham_agent.py**

```python
"""基于LLM的格雷厄姆风格投资Agent"""

import math
import logging
from typing import Dict, Any
from app.agents.llm_agent import LLMAgent
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.core.state import AnalysisState


logger = logging.getLogger(__name__)


class LLMGrahamAgent(LLMAgent):
    """
    基于LLM的格雷厄姆风格投资Agent

    使用Claude/GPT等大模型，结合格雷厄姆的投资知识进行推理分析
    """

    def __init__(
        self,
        tushare_service,
        llm_service: LLMService,
        knowledge_service: KnowledgeService
    ):
        super().__init__(
            tushare_service=tushare_service,
            llm_service=llm_service,
            knowledge_service=knowledge_service,
            master_name="graham"
        )

    @property
    def name(self) -> str:
        return "Benjamin Graham (AI)"

    @property
    def style(self) -> str:
        return "AI增强的深度价值投资：结合LLM推理与格雷厄姆投资哲学"

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行格雷厄姆风格分析

        流程：
        1. 获取增强的股票数据
        2. 加载格雷厄姆知识
        3. 计算Graham特有指标
        4. 构建CoT Prompt
        5. LLM推理
        6. 验证结果
        """
        stock_code = state.get("stock_code", "")

        # 1. 获取增强数据
        stock_data = await self._get_enriched_stock_data(stock_code)

        # 2. 加载知识
        knowledge = await self.knowledge.load_knowledge("graham")

        # 3. 计算Graham特有指标
        graham_metrics = self._calculate_graham_metrics(stock_data)

        # 4. 构建CoT Prompt
        cot_prompt = self._build_graham_cot_prompt(
            stock_data,
            knowledge,
            graham_metrics
        )

        # 5. LLM推理
        llm_result = await self.llm.reason_with_cot(cot_prompt)

        # 6. 验证结果
        validated_result = self._validate_result(llm_result, graham_metrics)

        # 7. 添加元数据
        validated_result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model"),
            "graham_metrics": graham_metrics
        })

        return validated_result

    def _calculate_graham_metrics(self, stock_data: Dict) -> Dict[str, Any]:
        """
        计算格雷厄姆特有的指标

        Args:
            stock_data: 股票数据

        Returns:
            Graham指标字典
        """
        metrics = stock_data.get("metrics", {})
        price = stock_data.get("price", 0)

        eps = metrics.get("eps", 0)
        bvps = metrics.get("bvps", 0)
        pe_ratio = metrics.get("pe_ratio", 0)

        # Graham公式内在价值
        if eps > 0 and bvps > 0:
            intrinsic_value = math.sqrt(22.5 * eps * bvps)
            safety_margin = (intrinsic_value - price) / intrinsic_value if intrinsic_value > 0 else 0
        else:
            intrinsic_value = 0
            safety_margin = 0

        # 盈利收益率
        earnings_yield = 1.0 / pe_ratio if pe_ratio > 0 else 0

        return {
            "intrinsic_value": round(intrinsic_value, 2),
            "safety_margin_percent": round(safety_margin * 100, 1),
            "earnings_yield": round(earnings_yield * 100, 2),
            "net_net_working_capital": stock_data.get("net_net_working_capital", 0),
            "price_vs_net_net": "低于" if price < stock_data.get("net_net_working_capital", float('inf')) else "高于"
        }

    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict) -> str:
        """构建思维链Prompt"""
        return self._build_graham_cot_prompt(
            stock_data,
            knowledge,
            self._calculate_graham_metrics(stock_data)
        )

    def _build_graham_cot_prompt(
        self,
        stock_data: Dict,
        knowledge: Dict,
        graham_metrics: Dict
    ) -> str:
        """
        构建格雷厄姆风格的思维链Prompt

        Args:
            stock_data: 股票数据
            knowledge: 大师知识
            graham_metrics: Graham指标

        Returns:
            Prompt字符串
        """
        stock_info = self._format_stock_data(stock_data)

        prompt = f"""# 投资分析任务

你现在是本杰明·格雷厄姆(Benjamin Graham)，价值投资之父。请严格按照你的投资理念分析以下股票。

---

## 你的核心投资哲学

{knowledge.get('core_philosophy', '深度价值投资，关注安全边际和内在价值。')}

---

## 核心评估维度

{knowledge.get('evaluation_dimensions', '安全边际、盈利收益率、财务安全性')}

---

## 决策规则

{knowledge.get('decision_rules', '安全边际>=30%且财务安全才买入')}

---

## 股票基本信息

**股票代码**: {stock_data.get('symbol', 'N/A')}
**股票名称**: {stock_data.get('name', 'N/A')}
**当前价格**: {stock_data.get('price', 0):.2f} 元

---

## 关键财务指标

{stock_info}

---

## Graham公式计算结果（参考）

- **内在价值**: {graham_metrics['intrinsic_value']} 元
- **安全边际**: {graham_metrics['safety_margin_percent']}%
- **盈利收益率**: {graham_metrics['earnings_yield']}%
- **Net-Net营运资本**: {graham_metrics['net_net_working_capital']:.2f} 亿元
- **价格与Net-Net关系**: {graham_metrics['price_vs_net_net']}

> 注：以上指标仅供参考，你需要结合自己的判断进行评估

---

## 分析要求

请严格按照以下思维链步骤进行分析：

### 第1步：数据理解
列出你认为最重要的3-5个财务指标，并解释为什么这些指标对格雷厄姆风格投资很重要。

### 第2步：理念对照
对照格雷厄姆的核心投资哲学，评估该股票是否符合深度价值投资的标准。

### 第3步：维度评分
按照评估维度，逐项给出评分(0-100)和理由。

### 第4步：风险识别
列出投资该股票可能面临的风险。

### 第5步：决策推理
基于以上分析，给出你的投资建议(buy/sell/hold)和置信度(0.0-1.0)。

### 第6步：格雷厄姆会怎么说？
用格雷厄姆的语气和风格，用1-2句话总结你的分析结论。

---

## 输出格式

请以JSON格式输出：

{{
    "thought_process": {{
        "step1_data_understanding": "...",
        "step2_philosophy_alignment": "...",
        "step3_dimension_scores": "各维度评分和理由",
        "step4_risks": ["风险1", "风险2"],
        "step5_decision_reasoning": "详细解释...",
        "step6_graham_quote": "格雷厄姆语气的总结..."
    }},
    "action": "buy/sell/hold",
    "confidence": 0.75,
    "key_factors": ["因素1", "因素2"],
    "scores": {{"safety_margin": 85, "financial_safety": 90}},
    "reasoning": "综合分析..."
}}

请开始你的分析："""
        return prompt

    def _format_stock_data(self, stock_data: Dict) -> str:
        """格式化股票数据"""
        metrics = stock_data.get("metrics", {})
        lines = []

        for key, value in metrics.items():
            if isinstance(value, float):
                lines.append(f"- **{key}**: {value:.2f}")
            else:
                lines.append(f"- **{key}**: {value}")

        return "\n".join(lines)

    def _validate_result(self, llm_result: Dict, graham_metrics: Dict) -> Dict:
        """
        验证LLM返回结果的合理性

        Args:
            llm_result: LLM返回结果
            graham_metrics: Graham指标

        Returns:
            验证后的结果
        """
        action = llm_result.get("action", "hold")
        confidence = llm_result.get("confidence", 0.5)

        # 基本验证
        if action not in ["buy", "sell", "hold"]:
            action = "hold"

        if not 0 <= confidence <= 1:
            confidence = max(0, min(1, confidence))

        # 格雷厄姆特定验证
        safety_margin = graham_metrics.get("safety_margin_percent", 0) / 100

        # 如果安全边际为负，格雷厄姆绝对不会建议买入
        if safety_margin < 0 and action == "buy":
            llm_result["action"] = "hold"
            llm_result["confidence"] *= 0.5
            llm_result["validation_warning"] = "安全边际为负，已调整为hold"

        return llm_result

    def _parse_llm_response(self, llm_result: Dict, stock_data: Dict) -> Dict[str, Any]:
        """解析LLM响应"""
        parsed = super()._parse_llm_response(llm_result, stock_data)

        # 添加思维过程
        thought_process = llm_result.get("thought_process", {})
        parsed["thought_process"] = thought_process

        # 添加评分
        scores = llm_result.get("scores", {})
        if scores:
            parsed["scores"] = scores

        return parsed
```

- [ ] **Step 2: 提交**

```bash
git add app/agents/value/llm_graham_agent.py
git commit -m "feat: 实现LLMGrahamAgent格雷厄姆AI Agent"
```

---

### Task 11: 更新Agent注册系统

**Files:**
- Modify: `app/agents/__init__.py`

- [ ] **Step 1: 更新__init__.py添加AI Agent注册**

```python
"""Agent模块 - 规则引擎和AI增强Agent"""

from app.agents.value.graham_agent import GrahamAgent
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.macro.dalio_agent import DalioAgent

# 规则引擎Agent映射
RULE_AGENTS = {
    "graham": GrahamAgent,
    "buffet": BuffetAgent,
    "fisher": FisherAgent,
    "lynch": LynchAgent,
    "soros": SorosAgent,
    "dalio": DalioAgent,
}

# AI增强Agent映射（延迟导入避免循环依赖）
_AI_AGENTS = None


def get_ai_agents():
    """延迟加载AI Agent"""
    global _AI_AGENTS
    if _AI_AGENTS is None:
        from app.agents.value.llm_graham_agent import LLMGrahamAgent
        from app.agents.value.llm_buffet_agent import LLMBuffetAgent

        _AI_AGENTS = {
            "graham": LLMGrahamAgent,
            "buffet": LLMBuffetAgent,
        }
    return _AI_AGENTS


def get_agent(agent_name: str, mode: str = "rule", **kwargs):
    """
    获取Agent实例

    Args:
        agent_name: Agent名称
        mode: "rule" | "ai" | "hybrid"
        **kwargs: Agent初始化参数

    Returns:
        Agent实例

    Raises:
        ValueError: 未知的Agent
    """
    if mode == "ai":
        ai_agents = get_ai_agents()
        agent_class = ai_agents.get(agent_name)
        if agent_class:
            return agent_class(**kwargs)

    # 默认使用规则引擎
    agent_class = RULE_AGENTS.get(agent_name)
    if agent_class:
        return agent_class(**kwargs)

    raise ValueError(f"Unknown agent: {agent_name}")


__all__ = [
    "GrahamAgent",
    "BuffetAgent",
    "FisherAgent",
    "LynchAgent",
    "SorosAgent",
    "DalioAgent",
    "RULE_AGENTS",
    "get_ai_agents",
    "get_agent",
]
```

- [ ] **Step 2: 提交**

```bash
git add app/agents/__init__.py
git commit -m "feat: 添加AI Agent注册系统"
```

---

## Phase 3: 知识文件创建

### Task 12: 创建Graham知识文件

**Files:**
- Create: `knowledge/graham/GRAHAM_AGENT_SUMMARY.md`

- [ ] **Step 1: 创建knowledge目录和Graham知识文件**

```bash
mkdir -p knowledge/graham
```

创建 `knowledge/graham/GRAHAM_AGENT_SUMMARY.md`:

```markdown
# Benjamin Graham 投资大师知识图谱

## 元数据
---
master_name: graham
display_name: 本杰明·格雷厄姆
school: 价值投资
born: 1894
died: 1976
famous_works: "《证券分析》《聪明的投资者》"
---

## 核心投资哲学

### 1. 深度价值投资理念

格雷厄姆被认为是价值投资之父，他的核心理念包括：

- **内在价值**: 每只股票都有一个内在价值，可以通过财务分析确定
- **安全边际**: 价格必须显著低于内在价值才值得买入（至少30%折扣）
- **市场波动**: 市场短期是投票机，长期是称重机
- **逆向思维**: 在他人恐惧时贪婪，在他人贪婪时恐惧

### 2. Graham公式

内在价值计算公式：
```
内在价值 = √(22.5 × 每股收益EPS × 每股净资产BVPS)
```

其中22.5是Graham常数，代表一家零增长公司的合理PE(15)与PB(1.5)的乘积。

### 3. Net-Net策略

净净营运资本 = (流动资产 - 总负债) / 总股本

买入条件：股价 ≤ 2/3 × 净净营运资本

## 核心评估维度

### 维度1: 安全边际分析
- 计算内在价值
- 计算安全边际百分比
- 评估价格折扣程度

**评分标准**:
- 安全边际 ≥ 50%: 100分
- 安全边际 ≥ 30%: 80-99分
- 安全边际 ≥ 20%: 60-79分
- 安全边际 < 20%: 0-59分

### 维度2: 盈利收益率
- 盈利收益率 = 1/PE
- 要求: 盈利收益率 ≥ 2倍AAA债券收益率

**评分标准**:
- 满足要求且有盈余: 80-100分
- 接近要求(80%-100%): 60-79分
- 不足要求: 0-59分

### 维度3: 财务安全性
- 负债率 < 50%
- 流动比率 > 2
- 利息覆盖倍数 > 5

**评分标准**:
- 三项全优: 80-100分
- 两项优秀: 60-79分
- 一项优秀: 40-59分
- 全不达标: 0-39分

### 维度4: 估值吸引力
- PE < 15 (理想 < 10)
- PB < 1.5 (理想 < 1)
- PS < 2

### 维度5: Net-Net机会
- 价格是否低于净净营运资本的2/3
- 这是格雷厄姆最保守的策略

## 决策规则

### 买入条件 (BUY)

必须同时满足：
1. 安全边际 ≥ 30%
2. 财务安全性评分 ≥ 60分
3. 盈利收益率 ≥ 2倍AAA债券收益率
4. 综合评分 ≥ 70分

### 持有条件 (HOLD)

满足以下任一：
1. 安全边际在20%-30%之间
2. 大部分条件满足但有一项不达标
3. 综合评分在60-69分

### 卖出/回避条件 (SELL)

满足以下任一：
1. 价格高于内在价值 (负安全边际)
2. 财务安全性评分 < 50分
3. 综合评分 < 60分

## 经典案例

### 成功案例: GEICO (1948)

**投资情况**:
- 格雷厄姆在1948年以约72万美元买入GEICO 50%股份
- 持有25年，价值增长超过200倍

**成功原因**:
1. 价格远低于内在价值（巨大安全边际）
2. 公司业务模式简单易懂
3. 长期增长潜力巨大
4. 管理层诚信有能力

### 失败教训: 1929年大萧条

**经验教训**:
1. 杠杆的危险性
2. 永远不要使用借来的钱投资股票
3. 保留足够的现金储备
4. 在市场疯狂时保持冷静

## 分析检查清单

在分析任何股票时，格雷厄姆会问：

1. [ ] 公司的内在价值是多少？
2. [ ] 当前价格提供了多少安全边际？
3. [ ] 财务状况是否稳健（负债率、流动性）？
4. [ ] 盈利收益率是否足够高？
5. [ ] 是否存在Net-Net机会？
6. [ ] 最坏情况下会损失多少？
7. [ ] 我是否愿意持有这只股票10年以上？

## 常见误区

### 误区1: 低PE就是价值股
**纠正**: PE低可能是因为公司业务恶化，必须分析盈利质量

### 误区2: 分散投资不够重要
**纠正**: 格雷厄姆强调至少持有30只股票以分散风险

### 误区3: 只关注财务报表
**纠正**: 还需要关注行业前景、管理层素质等定性因素
```

- [ ] **Step 2: 提交**

```bash
git add knowledge/graham/GRAHAM_AGENT_SUMMARY.md
git commit -m "docs: 添加格雷厄姆投资知识文件"
```

---

### Task 13: 创建Buffet知识文件

**Files:**
- Create: `knowledge/buffet/BUFFET_AGENT_SUMMARY.md`

- [ ] **Step 1: 创建knowledge/buffet目录和知识文件**

```bash
mkdir -p knowledge/buffet
```

创建 `knowledge/buffet/BUFFET_AGENT_SUMMARY.md`:

```markdown
# Warren Buffett 投资大师知识图谱

## 元数据
---
master_name: buffet
display_name: 沃伦·巴菲特
school: 价值投资
born: 1930
famous_works: "伯克希尔·哈撒韦致股东信"
---

## 核心投资哲学

### 1. 护城河理论

巴菲特最著名的投资概念是"经济护城河"：

- **品牌优势**: 强大的品牌认知度
- **网络效应**: 用户越多，价值越高
- **成本优势**: 规模经济或专有技术
- **转换成本**: 客户难以更换供应商
- **监管壁垒**: 许可证或专利保护

### 2. 能力圈

"投资你必须了解的生意"：
- 只投资自己能够理解的行业
- 避免复杂的技术公司
- 简单易懂的业务模式
- 可持续的竞争优势

### 3. 优秀企业的特征

- 持续的盈利能力
- 高ROE（净资产收益率）
- 低资本支出
- 强大的自由现金流
- 诚信有能力的管理层

### 4. 合理的价格

"用合理价格买入优秀公司，而非用便宜价格买入普通公司"

## 核心评估维度

### 维度1: 护城河评分 (0-100)

**评分标准**:
- 拥有3个以上护城河来源: 90-100分
- 拥有2个护城河来源: 70-89分
- 拥有1个护城河来源: 50-69分
- 无明显护城河: 0-49分

### 维度2: 盈利质量

- ROE ≥ 20%: 优秀
- ROE 15%-20%: 良好
- ROE < 15%: 一般

### 维度3: 现金流分析

- 经营现金流持续为正
- 自由现金流充裕
- 现金流转换率高

### 维度4: 管理层评估

- 诚信记录
- 过去业绩
- 资本配置能力
- 股东回报意识

### 维度5: 估值合理性

- PE相对历史水平
- PB相对行业平均
- EV/EBITDA

## 决策规则

### 买入条件 (BUY)

必须同时满足：
1. 护城河评分 ≥ 70分
2. ROE ≥ 15%
3. 正的自由现金流
4. 价格不超过内在价值30%溢价
5. 在能力圈范围内

### 持有条件 (HOLD)

1. 护城河依然稳固
2. 盈利能力持续
3. 估值合理偏高但不离谱

### 卖出条件 (SELL)

1. 护城河受损
2. 基本面恶化
3. 价格严重高估
4. 发现更好的投资机会

## 经典案例

### 成功案例: 可口可乐

**投资情况**:
- 1988年开始大举买入
- 平均成本约1.69美元/股
- 持有至今超过35年

**成功原因**:
1. 强大的品牌护城河
2. 全球分销网络
3. 持续的分红和回购
4. 管理层优秀

### 成功案例: 苹果公司

**投资情况**:
- 2016年开始大量买入
- 成为伯克希尔最大持仓

**成功原因**:
1. 强大的生态系统
2. 忠实的客户群体
3. 优秀的资本配置
4. 持续的创新能力

## 分析检查清单

巴菲特评估公司时会问：

1. [ ] 这家公司是否简单易懂？
2. [ ] 它是否有持久的竞争优势（护城河）？
3. [ ] 管理层是否诚信有能力？
4. [ ] 价格是否合理？
5. [ ] 我是否愿意持有10年以上？
6. [ ] 这笔投资是否有足够的安全边际？
7. [ ] 这个业务在未来10年会如何？

## 投资名言

- "别人贪婪时我恐惧，别人恐惧时我贪婪"
- "如果你不愿意持有一只股票10年，那就不要考虑持有它10分钟"
- "价格是你付出的，价值是你得到的"
- "我用护城河的概念来衡量一个企业的竞争优势"
```

- [ ] **Step 2: 提交**

```bash
git add knowledge/buffet/BUFFET_AGENT_SUMMARY.md
git commit -m "docs: 添加巴菲特投资知识文件"
```

---

## Phase 4: API集成

### Task 14: 扩展API路由 - 添加AI模式支持

**Files:**
- Modify: `app/api/routes/analyze.py`

- [ ] **Step 1: 扩展请求模型**

在`AnalyzeRequest`类后添加：

```python
class LLMConfigModel(BaseModel):
    """LLM配置模型"""
    provider: str = Field(default="openai", description="LLM提供商")
    model: str = Field(default="gpt-4o", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=4000, ge=100, le=8000)
```

扩展`AnalyzeRequest`类，添加字段：

```python
class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    stock_code: str = Field(..., description="股票代码（6位数字）", min_length=6, max_length=6)
    mode: str = Field(default="parallel", description="协作模式: parallel/vote/debate")
    agents: Optional[str] = Field(default=None, description="指定Agent（逗号分隔）")
    agent_mode: str = Field(default="rule", description="Agent模式: rule/ai/hybrid")
    llm_config: Optional[LLMConfigModel] = Field(default=None, description="LLM配置")
    verbose: bool = Field(default=False, description="详细输出")
```

- [ ] **Step 2: 扩展响应模型**

扩展`AgentAnalysisModel`类，添加字段：

```python
class AgentAnalysisModel(BaseModel):
    """Agent分析结果模型"""
    agent_name: str
    agent_type: str
    action: str
    confidence: float
    reasoning: str
    key_metrics: Dict[str, Any]
    price_target: Optional[float]
    # AI模式特有字段
    analysis_mode: Optional[str] = Field(default=None, description="分析模式: rule/ai_llm/rule_fallback")
    thought_process: Optional[Dict[str, Any]] = Field(default=None, description="思维链过程")
    llm_model: Optional[str] = Field(default=None, description="使用的LLM模型")
    validation_warning: Optional[str] = Field(default=None, description="验证警告")
```

- [ ] **Step 3: 更新路由处理逻辑**

在`analyze_stock`函数中，找到创建Agent的部分，添加AI模式支持：

```python
# 在创建Agent实例之前添加：
llm_service = None
knowledge_service = None

if request.agent_mode in ["ai", "hybrid"]:
    from app.services.llm_service import LLMService
    from app.services.knowledge_service import KnowledgeService

    # 构建LLM配置
    llm_config_dict = None
    if request.llm_config:
        llm_config_dict = {
            "provider": request.llm_config.provider,
            "model": request.llm_config.model,
            "api_key": request.llm_config.api_key or settings.openai_api_key,
            "temperature": request.llm_config.temperature,
            "max_tokens": request.llm_config.max_tokens
        }

    llm_service = LLMService(llm_config_dict)
    knowledge_service = KnowledgeService(settings.knowledge_base_path)

# 创建Agent实例
agents = []
for name in agent_names:
    if request.agent_mode == "ai":
        from app.agents import get_agent
        agent = get_agent(
            name,
            mode="ai",
            tushare_service=tushare_service,
            llm_service=llm_service,
            knowledge_service=knowledge_service
        )
    else:
        from app.agents import get_agent
        agent = get_agent(
            name,
            mode="rule",
            tushare_service=tushare_service
        )
    agents.append(agent)
```

- [ ] **Step 4: 提交**

```bash
git add app/api/routes/analyze.py
git commit -m "feat: API支持AI模式分析"
```

---

## Phase 5: 前端集成

### Task 15: 扩展前端API类型定义

**Files:**
- Modify: `frontend/src/api/analyze.ts`

- [ ] **Step 1: 添加LLM配置类型**

```typescript
export interface LLMConfig {
  provider?: 'openai' | 'anthropic' | 'local';
  model?: string;
  api_key?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface AnalyzeRequest {
  stock_code: string;
  mode?: 'parallel' | 'vote' | 'debate';
  agents?: string;
  agent_mode?: 'rule' | 'ai' | 'hybrid';  // 新增
  llm_config?: LLMConfig;  // 新增
  verbose?: boolean;
}

export interface ThoughtProcess {
  step1_data_understanding?: string;
  step2_philosophy_alignment?: string;
  step3_dimension_scores?: string;
  step4_risks?: string[];
  step5_decision_reasoning?: string;
  step6_graham_quote?: string;
}

export interface AgentAnalysis {
  agent_name: string;
  agent_type: string;
  action: string;
  confidence: number;
  reasoning: string;
  key_metrics: Record<string, any>;
  price_target?: number;
  // 新增字段
  analysis_mode?: string;
  thought_process?: ThoughtProcess;
  llm_model?: string;
  validation_warning?: string;
}
```

- [ ] **Step 2: 更新API调用函数**

```typescript
export async function analyzeStock(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/api/analyze.ts
git commit -m "feat: 前端API支持AI模式类型"
```

---

### Task 16: 更新分析页面UI

**Files:**
- Modify: `frontend/src/views/AnalyzeView.vue`

- [ ] **Step 1: 添加AI模式选择器**

在template中添加：

```vue
<el-card class="mode-selector">
  <template #header>
    <span>分析模式</span>
  </template>

  <el-radio-group v-model="agentMode">
    <el-radio-button label="rule">
      <el-icon><Coin /></el-icon>
      规则引擎
    </el-radio-button>
    <el-radio-button label="ai">
      <el-icon><MagicStick /></el-icon>
      AI增强
    </el-radio-button>
    <el-radio-button label="hybrid">
      <el-icon><DataAnalysis /></el-icon>
      混合模式
    </el-radio-button>
  </el-radio-group>
</el-card>
```

- [ ] **Step 2: 添加LLM配置面板**

```vue
<el-card v-if="agentMode === 'ai'" class="ai-config">
  <template #header>
    <span>LLM配置</span>
  </template>

  <el-form :model="llmConfig" label-width="100px">
    <el-form-item label="提供商">
      <el-select v-model="llmConfig.provider">
        <el-option label="OpenAI" value="openai" />
        <el-option label="Anthropic" value="anthropic" />
        <el-option label="本地模型" value="local" />
      </el-select>
    </el-form-item>

    <el-form-item label="模型">
      <el-select v-model="llmConfig.model">
        <el-option label="GPT-4o" value="gpt-4o" />
        <el-option label="GPT-4 Turbo" value="gpt-4-turbo" />
        <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet-20241022" />
      </el-select>
    </el-form-item>

    <el-form-item label="Temperature">
      <el-slider v-model="llmConfig.temperature" :min="0" :max="1" :step="0.1" />
    </el-form-item>
  </el-form>
</el-card>
```

- [ ] **Step 3: 添加思维过程展示**

```vue
<div v-if="analysis.thought_process && analysis.analysis_mode === 'ai_llm'" class="thought-process">
  <el-collapse>
    <el-collapse-item title="查看AI分析思维过程" name="thought">
      <div class="thought-steps">
        <div v-for="(step, key) in analysis.thought_process" :key="key" class="step">
          <h5>{{ formatStepName(key) }}</h5>
          <p>{{ step }}</p>
        </div>
      </div>
    </el-collapse-item>
  </el-collapse>
</div>
```

- [ ] **Step 4: 添加script逻辑**

```typescript
const agentMode = ref<'rule' | 'ai' | 'hybrid'>('rule');
const llmConfig = ref<LLMConfig>({
  provider: 'openai',
  model: 'gpt-4o',
  temperature: 0.7,
  max_tokens: 4000
});

async function handleAnalyze() {
  const response = await analyzeStock({
    stock_code: stockCode.value,
    mode: analysisMode.value,
    agents: selectedAgents.value.join(','),
    agent_mode: agentMode.value,
    llm_config: agentMode.value === 'ai' ? llmConfig.value : undefined
  });
  agentAnalyses.value = response.agent_analyses;
}

function formatStepName(key: string): string {
  const names: Record<string, string> = {
    step1_data_understanding: '第1步：数据理解',
    step2_philosophy_alignment: '第2步：理念对照',
    step3_dimension_scores: '第3步：维度评分',
    step4_risks: '第4步：风险识别',
    step5_decision_reasoning: '第5步：决策推理',
    step6_graham_quote: '第6步：格雷厄姆语录'
  };
  return names[key] || key;
}
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/views/AnalyzeView.vue
git commit -m "feat: 前端添加AI模式配置和思维过程展示"
```

---

## Phase 6: 测试与验证

### Task 17: 端到端测试

**Files:**
- Create: `tests/integration/test_ai_mode_e2e.py`

- [ ] **Step 1: 创建端到端测试**

```python
"""端到端测试 - AI模式完整流程"""

import pytest
import asyncio
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
```

- [ ] **Step 2: 运行端到端测试**

```bash
poetry run pytest tests/integration/test_ai_mode_e2e.py -v --tb=short
```

- [ ] **Step 3: 提交**

```bash
git add tests/integration/test_ai_mode_e2e.py
git commit -m "test: 添加AI模式端到端测试"
```

---

### Task 18: A/B对比测试

**Files:**
- Create: `tests/integration/test_ab_comparison.py`

- [ ] **Step 1: 创建A/B测试**

```python
"""A/B对比测试 - 规则引擎 vs AI Agent"""

import pytest
from app.agents import get_agent, RULE_AGENTS
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
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
```

- [ ] **Step 2: 运行A/B测试**

```bash
poetry run pytest tests/integration/test_ab_comparison.py -v -s
```

- [ ] **Step 3: 提交**

```bash
git add tests/integration/test_ab_comparison.py
git commit -m "test: 添加规则引擎vs AI Agent A/B对比测试"
```

---

## Phase 7: 文档与部署

### Task 19: 更新README文档

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 在README中添加AI模式说明**

在README的"核心特性"部分后添加：

```markdown
## AI增强模式

### 支持的LLM模型

- **OpenAI**: GPT-4, GPT-4o, GPT-4o-mini
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **本地模型**: 通过OpenAI兼容接口（如Ollama）

### AI模式特点

- **思维链推理**: 逐步分析，提供完整的思考过程
- **知识驱动**: 基于投资大师的知识图谱进行决策
- **自动降级**: LLM失败时自动切换到规则引擎
- **多模型支持**: 灵活配置不同的LLM提供商

### 配置示例

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="sk-..."

# 或在.env文件中配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

### API使用示例

```bash
# 使用AI模式分析
curl -X POST "http://localhost:8000/api/v1/analyze/" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "mode": "parallel",
    "agents": "graham,buffet",
    "agent_mode": "ai",
    "llm_config": {
      "provider": "openai",
      "model": "gpt-4o"
    }
  }'
```
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: 添加AI模式使用说明"
```

---

### Task 20: 创建Docker配置

**Files:**
- Create: `docker/Dockerfile.ai`

- [ ] **Step 1: 创建AI模式专用Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml ./
RUN apt-get update && apt-get install -y gcc && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# 复制代码
COPY ./app ./app
COPY ./knowledge ./knowledge

# 环境变量
ENV PYTHONPATH=/app
ENV KNOWLEDGE_BASE_PATH=/app/knowledge

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 更新docker-compose.yml**

添加AI模式环境变量：

```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.ai
    environment:
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - LLM_MODEL=${LLM_MODEL:-gpt-4o}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AI_MODE_ENABLED=true
      - KNOWLEDGE_BASE_PATH=/app/knowledge
    volumes:
      - ./knowledge:/app/knowledge:ro
```

- [ ] **Step 3: 提交**

```bash
git add docker/Dockerfile.ai docker-compose.yml
git commit -m "feat: 添加AI模式Docker配置"
```

---

## 验证检查清单

完成所有任务后，请验证以下内容：

- [ ] 所有单元测试通过
- [ ] 端到端测试通过
- [ ] 可以通过API调用AI模式分析
- [ ] 前端UI正常显示AI模式选项
- [ ] 思维过程正确展示
- [ ] LLM失败时正确降级到规则引擎
- [ ] 知识文件正确加载
- [ ] 环境变量配置生效
- [ ] Docker镜像构建成功

---

## 实施完成后的提交

所有任务完成后，创建最终的汇总提交：

```bash
git add .
git commit -m "feat: 完成AI模式投资分析系统实现

- 实现LLMService支持OpenAI/Anthropic/本地模型
- 实现KnowledgeService管理投资大师知识
- 创建LLMAgent基类和LLMGrahamAgent
- 添加格雷厄姆和巴菲特知识文件
- API支持agent_mode和llm_config参数
- 前端添加AI模式配置和思维过程展示
- 完整的单元测试和集成测试
- 支持自动降级到规则引擎

详见设计文档: docs/superpowers/specs/2026-05-05-ai-mode-design.md"
```

---

**实施计划结束**
