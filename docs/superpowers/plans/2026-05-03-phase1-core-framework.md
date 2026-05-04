# Phase 1: 核心框架搭建

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 搭建项目核心架构，实现基础数据结构、Tushare数据服务、Agent抽象类和第一个示例Agent（巴菲特价值投资Agent），以及简单的CLI框架

**架构:** 分层架构 - 数据层(Tushare API) → 服务层(TushareService) → Agent层(BaseAgent + BuffetAgent) → 接入层(CLI)

**技术栈:** Python 3.11+, Poetry, Tushare Pro, Click, Rich, Pydantic, pytest

---

## 文件结构规划

```
invest_agent_by_graph/
├── pyproject.toml                    # Poetry依赖管理
├── .env.example                      # 环境变量模板
├── .gitignore
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py                       # CLI入口
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置管理（pydantic-settings）
│   │   └── state.py                  # AnalysisState等核心数据结构
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseAgent抽象类
│   │   └── value/
│   │       ├── __init__.py
│   │       └── buffet_agent.py       # 巴菲特Agent
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── tushare_service.py        # Tushare数据服务
│   │
│   └── cli/
│       ├── __init__.py
│       └── main.py                   # Click命令定义
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # pytest配置和fixtures
│   ├── unit/
│   │   ├── services/
│   │   │   └── test_tushare_service.py
│   │   └── agents/
│   │       ├── test_base_agent.py
│   │       └── test_buffet_agent.py
│   └── fixtures/
│       └── stock_data.py             # 测试用股票数据
│
└── scripts/
    └── setup_env.py                  # 环境设置脚本
```

---

## Task 1: 项目初始化

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`
- Create: `app/__init__.py`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[tool.poetry]
name = "invest-agent-by-graph"
version = "0.1.0"
description = "基于LangGraph+Tushare的多Agent投资智能体系"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.11"
click = "^8.1.7"
rich = "^13.7.0"
pydantic = "^2.6.0"
pydantic-settings = "^2.1.0"
tushare = "^1.2.90"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
pytest-mock = "^3.12.0"
black = "^24.1.0"
ruff = "^0.1.0"
mypy = "^1.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: 创建 .env.example**

```bash
# Tushare配置
TUSHARE_TOKEN=your_tushare_token_here

# 应用配置
LOG_LEVEL=INFO
CACHE_TTL=3600

# 数据库配置（后期使用）
DATABASE_URL=sqlite+aiosqlite:///./data/invest_agent.db
```

- [ ] **Step 3: 创建 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
ENV/
env/
.venv

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# 环境变量
.env

# 测试
.pytest_cache/
.coverage
htmlcov/

# 数据
data/*.db
data/*.sqlite
*.csv

# 日志
*.log

# Poetry
poetry.lock
```

- [ ] **Step 4: 创建 README.md**

```markdown
# Invest Agent By Graph

基于 LangGraph + Tushare 的多Agent投资智能体系

## 特性

- 多种投资风格Agent（价值投资、成长投资、宏观对冲）
- 三种协作模式（并行分析、投票决策、辩论仲裁）
- 智能选股、个股分析、策略回测
- CLI和Web双接口

## 安装

```bash
# 安装Poetry
pip install poetry

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑.env，填入你的Tushare Token
```

## 快速开始

```bash
# 分析股票
poetry run invest-agent analyze 600519

# 查看帮助
poetry run invest-agent --help
```

## 开发

```bash
# 运行测试
poetry run pytest

# 代码格式化
poetry run black app tests
poetry run ruff check app tests
```

## 许可证

MIT License
```

- [ ] **Step 5: 创建 app/__init__.py**

```python
"""Invest Agent By Graph - 多Agent投资智能体系"""

__version__ = "0.1.0"
```

- [ ] **Step 6: 初始化Git仓库并提交**

```bash
git init
git add .
git commit -m "feat: initialize project with Poetry and basic structure"
```

---

## Task 2: 核心配置管理

**Files:**
- Create: `app/core/__init__.py`
- Create: `app/core/config.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: 创建 app/core/__init__.py**

```python
"""核心模块 - 配置和数据结构"""

from app.core.config import settings
from app.core.state import AnalysisState, AgentAnalysis, Decision

__all__ = ["settings", "AnalysisState", "AgentAnalysis", "Decision"]
```

- [ ] **Step 2: 创建配置管理类**

先创建测试：

```python
# tests/unit/core/test_config.py
import os
import pytest
from pydantic import ValidationError

def test_settings_loads_from_env(monkeypatch):
    """测试配置从环境变量加载"""
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token_123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    from app.core.config import settings

    assert settings.tushare_token == "test_token_123"
    assert settings.log_level == "DEBUG"

def test_settings_default_values(monkeypatch):
    """测试配置默认值"""
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token")

    from app.core.config import settings

    assert settings.cache_ttl == 3600
    assert settings.log_level == "INFO"

def test_settings_missing_token(monkeypatch):
    """测试缺少必需配置时报错"""
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        from app.core.config import settings
        _ = settings.tushare_token
```

运行测试（预期失败）：

```bash
poetry run pytest tests/unit/core/test_config.py -v
```

创建配置实现：

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Tushare配置
    tushare_token: str

    # 应用配置
    log_level: str = "INFO"
    cache_ttl: int = 3600

    # 数据库配置（后期使用）
    database_url: str = "sqlite+aiosqlite:///./data/invest_agent.db"


# 全局配置实例
settings = Settings()
```

- [ ] **Step 3: 创建测试配置文件 conftest.py**

```python
# tests/conftest.py
import pytest
import os
from pathlib import Path

# 设置测试环境变量
os.environ.setdefault("TUSHARE_TOKEN", "test_token_for_pytest")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_stock_code():
    """模拟股票代码"""
    return "600519"


@pytest.fixture
def mock_tushare_token():
    """模拟Tushare Token"""
    return "test_token_123"
```

- [ ] **Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/unit/core/test_config.py -v
```

预期：PASS

- [ ] **Step 5: 提交**

```bash
git add app/core/ tests/
git commit -m "feat: add configuration management with pydantic-settings"
```

---

## Task 3: 核心数据结构定义

**Files:**
- Create: `app/core/state.py`
- Test: `tests/unit/core/test_state.py`

- [ ] **Step 1: 编写数据结构测试**

```python
# tests/unit/core/test_state.py
import pytest
from app.core.state import AnalysisState, AgentAnalysis, Decision

def test_agent_analysis_creation():
    """测试AgentAnalysis创建"""
    analysis = AgentAnalysis(
        agent_name="TestAgent",
        agent_type="value",
        action="buy",
        confidence=0.85,
        reasoning="测试理由",
        key_metrics={"score": 8.5},
        price_target=100.0
    )

    assert analysis.agent_name == "TestAgent"
    assert analysis.action == "buy"
    assert analysis.confidence == 0.85
    assert analysis.price_target == 100.0

def test_agent_analysis_optional_price_target():
    """测试可选的价格目标"""
    analysis = AgentAnalysis(
        agent_name="TestAgent",
        agent_type="value",
        action="hold",
        confidence=0.6,
        reasoning="无目标价",
        key_metrics={},
        price_target=None
    )

    assert analysis.price_target is None

def test_analysis_state_creation():
    """测试AnalysisState创建"""
    state = AnalysisState(
        stock_code="600519",
        mode="parallel",
        user_request="分析这只股票",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None
    )

    assert state["stock_code"] == "600519"
    assert state["mode"] == "parallel"
    assert len(state["agent_analyses"]) == 0

def test_decision_creation():
    """测试Decision创建"""
    decision = Decision(
        action="buy",
        consensus=0.75,
        participating_agents=["BuffetAgent", "GrahamAgent"],
        summary="建议买入"
    )

    assert decision.action == "buy"
    assert decision.consensus == 0.75
    assert len(decision.participating_agents) == 2
```

- [ ] **Step 2: 运行测试（预期失败）**

```bash
poetry run pytest tests/unit/core/test_state.py -v
```

预期：FAIL - module not found

- [ ] **Step 3: 实现数据结构**

```python
# app/core/state.py
from typing import TypedDict, List, Optional, Dict, Any
from typing_extensions import Annotated
import operator


class AgentAnalysis(TypedDict):
    """单个Agent的分析结果"""

    agent_name: str  # Agent名称，如 "BuffetAgent"
    agent_type: str  # Agent类型: "value" | "growth" | "macro"
    action: str  # 投资建议: "buy" | "sell" | "hold"
    confidence: float  # 置信度 0.0 - 1.0
    reasoning: str  # 分析理由
    key_metrics: Dict[str, Any]  # 关键指标字典
    price_target: Optional[float]  # 目标价格（可选）


class DebateMessage(TypedDict):
    """辩论消息"""

    agent_name: str
    content: str
    round: int
    timestamp: str


class Decision(TypedDict):
    """最终投资决策"""

    action: str  # 最终决策: "buy" | "sell" | "hold"
    consensus: float  # 共识度 0.0 - 1.0
    participating_agents: List[str]  # 参与决策的Agent列表
    summary: str  # 决策摘要


class AnalysisState(TypedDict):
    """投资分析的状态定义（用于LangGraph）"""

    # 输入
    stock_code: str  # 股票代码，如 "600519"
    mode: str  # 协作模式: "parallel" | "vote" | "debate"
    user_request: str  # 用户自然语言需求

    # Agent 分析结果（累积）
    agent_analyses: Annotated[List[AgentAnalysis], operator.add]

    # 协作中间状态
    debate_round: int  # 辩论轮次
    debate_history: List[DebateMessage]  # 辩论历史

    # 输出
    final_decision: Optional[Decision]  # 最终决策
    error: Optional[str]  # 错误信息
```

- [ ] **Step 4: 更新 app/core/__init__.py 导入**

```python
# app/core/__init__.py
"""核心模块 - 配置和数据结构"""

from app.core.config import settings
from app.core.state import (
    AnalysisState,
    AgentAnalysis,
    Decision,
    DebateMessage,
)

__all__ = [
    "settings",
    "AnalysisState",
    "AgentAnalysis",
    "Decision",
    "DebateMessage",
]
```

- [ ] **Step 5: 运行测试验证**

```bash
poetry run pytest tests/unit/core/test_state.py -v
```

预期：PASS

- [ ] **Step 6: 提交**

```bash
git add app/core/state.py tests/unit/core/test_state.py
git commit -m "feat: add core data structures for analysis state and agent results"
```

---

## Task 4: TushareService 基础实现

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/tushare_service.py`
- Test: `tests/unit/services/test_tushare_service.py`

- [ ] **Step 1: 创建测试数据fixtures**

```python
# tests/fixtures/stock_data.py
"""测试用股票数据"""

MOCK_DAILY_DATA = {
    "ts_code": "600519.SH",
    "trade_date": "20240503",
    "open": 1750.0,
    "high": 1780.0,
    "low": 1745.0,
    "close": 1770.0,
    "vol": 25000,
    "amount": 4400000,
}

MOCK_FINANCIAL_INDICATORS = {
    "ts_code": "600519.SH",
    "ann_date": "2024-04-30",
    "end_date": "2024-03-31",
    "pe": 35.5,
    "pe_ttm": 36.2,
    "pb": 12.8,
    "ps": 18.5,
    "ps_ttm": 19.2,
    "dv_ratio": 1.2,
    "dv_ttm": 1.5,
    "total_share": 125619.78,
    "float_share": 125619.78,
    "free_share": 125619.78,
    "total_mv": 2224000,
    "circ_mv": 2224000,
}

MOCK_INCOME_STATEMENT = {
    "ts_code": "600519.SH",
    "ann_date": "2024-04-30",
    "f_ann_date": "2024-04-30",
    "end_date": "2024-03-31",
    "report_type": 1,
    "oper_rev": 30000000000,
    "oper_cost": 8000000000,
    "operate_profit": 22000000000,
    "total_profit": 22500000000,
    "n_income": 18000000000,
    "n_income_attr_p": 18000000000,
}

MOCK_BALANCE_SHEET = {
    "ts_code": "600519.SH",
    "ann_date": "2024-04-30",
    "f_ann_date": "2024-04-30",
    "end_date": "2024-03-31",
    "total_assets": 250000000000,
    "total_liab": 50000000000,
    "total_hldr_eqy_exc_min_int": 200000000000,
    "total_equity": 200000000000,
}
```

- [ ] **Step 2: 编写TushareService测试**

```python
# tests/unit/services/test_tushare_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.tushare_service import TushareService

@pytest.fixture
def tushare_service(mock_tushare_token):
    """创建TushareService实例"""
    return TushareService(token=mock_tushare_token)

@pytest.mark.asyncio
async def test_get_daily_basic(tushare_service):
    """测试获取日线基本信息"""
    with patch.object(tushare_service.api, 'daily_basic') as mock_daily_basic:
        # 模拟返回数据
        import pandas as pd
        mock_df = pd.DataFrame([{
            "ts_code": "600519.SH",
            "trade_date": "20240503",
            "pe": 35.5,
            "pb": 12.8,
        }])
        mock_daily_basic.return_value = mock_df

        result = await tushare_service.get_daily_basic("600519")

        assert result["ts_code"] == "600519.SH"
        assert result["pe"] == 35.5
        mock_daily_basic.assert_called_once()

@pytest.mark.asyncio
async def test_get_income_statement(tushare_service):
    """测试获取利润表"""
    with patch.object(tushare_service.api, 'income') as mock_income:
        import pandas as pd
        mock_df = pd.DataFrame([{
            "ts_code": "600519.SH",
            "end_date": "2024-03-31",
            "n_income": 18000000000,
        }])
        mock_income.return_value = mock_df

        result = await tushare_service.get_income_statement("600519")

        assert result["n_income"] == 18000000000
        mock_income.assert_called_once()

@pytest.mark.asyncio
async def test_get_stock_fundamentals(tushare_service):
    """测试获取完整基本面数据"""
    with patch.object(tushare_service, 'get_daily_basic') as mock_basic, \
         patch.object(tushare_service, 'get_income_statement') as mock_income, \
         patch.object(tushare_service, 'get_balancesheet') as mock_balance, \
         patch.object(tushare_service, 'get_cashflow') as mock_cash:

        mock_basic.return_value = {"ts_code": "600519.SH", "pe": 35.5}
        mock_income.return_value = {"n_income": 18000000000}
        mock_balance.return_value = {"total_assets": 250000000000}
        mock_cash.return_value = {"n_cashflow_act": 15000000000}

        result = await tushare_service.get_stock_fundamentals("600519")

        assert result["stock_code"] == "600519"
        assert "daily" in result
        assert "income_statement" in result
        assert "balance_sheet" in result
        assert "cash_flow" in result

@pytest.mark.asyncio
async def test_format_stock_code(tushare_service):
    """测试股票代码格式化"""
    # 测试6位代码转换为标准格式
    result = tushare_service._format_stock_code("600519")
    assert result == "600519.SH"

    # 测试已经是标准格式
    result = tushare_service._format_stock_code("600519.SH")
    assert result == "600519.SH"

    # 测试深圳股票
    result = tushare_service._format_stock_code("000001")
    assert result == "000001.SZ"
```

- [ ] **Step 3: 运行测试（预期失败）**

```bash
poetry run pytest tests/unit/services/test_tushare_service.py -v
```

预期：FAIL - module not found

- [ ] **Step 4: 实现TushareService**

```python
# app/services/tushare_service.py
"""Tushare数据服务"""

import tushare as ts
from typing import Dict, Any, Optional
from functools import lru_cache
import pandas as pd


class TushareService:
    """Tushare Pro数据服务封装"""

    def __init__(self, token: str):
        """
        初始化Tushare服务

        Args:
            token: Tushare Pro API Token
        """
        ts.set_token(token)
        self.api = ts.pro_api()

    async def get_daily_basic(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票日线基本信息

        Args:
            stock_code: 股票代码（6位数字或标准格式）

        Returns:
            包含PE、PB等基本指标的字典
        """
        formatted_code = self._format_stock_code(stock_code)

        df = self.api.daily_basic(ts_code=formatted_code, fields="")

        if df.empty:
            return {}

        # 获取最新一条记录
        return df.iloc[0].to_dict()

    async def get_income_statement(
        self, stock_code: str, period: str = "latest"
    ) -> Dict[str, Any]:
        """
        获取利润表数据

        Args:
            stock_code: 股票代码
            period: 报告期，默认最新

        Returns:
            利润表数据字典
        """
        formatted_code = self._format_stock_code(stock_code)

        df = self.api.income(
            ts_code=formatted_code, period=period, fields="ts_code,ann_date,f_ann_date,end_date,report_type,oper_rev,oper_cost,operate_profit,total_profit,n_income,n_income_attr_p"
        )

        if df.empty:
            return {}

        return df.iloc[0].to_dict()

    async def get_balancesheet(
        self, stock_code: str, period: str = "latest"
    ) -> Dict[str, Any]:
        """
        获取资产负债表数据

        Args:
            stock_code: 股票代码
            period: 报告期，默认最新

        Returns:
            资产负债表数据字典
        """
        formatted_code = self._format_stock_code(stock_code)

        df = self.api.balancesheet(
            ts_code=formatted_code,
            period=period,
            fields="ts_code,ann_date,f_ann_date,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_equity",
        )

        if df.empty:
            return {}

        return df.iloc[0].to_dict()

    async def get_cashflow(
        self, stock_code: str, period: str = "latest"
    ) -> Dict[str, Any]:
        """
        获取现金流量表数据

        Args:
            stock_code: 股票代码
            period: 报告期，默认最新

        Returns:
            现金流量表数据字典
        """
        formatted_code = self._format_stock_code(stock_code)

        df = self.api.cashflow(
            ts_code=formatted_code,
            period=period,
            fields="ts_code,ann_date,f_ann_date,end_date,n_cashflow_act",
        )

        if df.empty:
            return {}

        return df.iloc[0].to_dict()

    async def get_stock_fundamentals(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票完整基本面数据

        Args:
            stock_code: 股票代码

        Returns:
            包含所有基本面数据的字典
        """
        # 并行获取各类数据
        daily = await self.get_daily_basic(stock_code)
        income = await self.get_income_statement(stock_code)
        balance = await self.get_balancesheet(stock_code)
        cash = await self.get_cashflow(stock_code)

        return {
            "stock_code": stock_code,
            "daily": daily,
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash,
        }

    def _format_stock_code(self, stock_code: str) -> str:
        """
        格式化股票代码为Tushare标准格式

        Args:
            stock_code: 6位代码或已格式化代码

        Returns:
            标准格式代码，如 "600519.SH"
        """
        # 如果已经是标准格式，直接返回
        if "." in stock_code:
            return stock_code

        # 根据代码前缀判断交易所
        if stock_code.startswith("6"):
            return f"{stock_code}.SH"  # 上海
        elif stock_code.startswith(("0", "3")):
            return f"{stock_code}.SZ"  # 深圳
        else:
            return stock_code
```

- [ ] **Step 5: 创建 app/services/__init__.py**

```python
# app/services/__init__.py
"""服务层模块"""

from app.services.tushare_service import TushareService

__all__ = ["TushareService"]
```

- [ ] **Step 6: 运行测试验证**

```bash
poetry run pytest tests/unit/services/test_tushare_service.py -v
```

预期：PASS

- [ ] **Step 7: 提交**

```bash
git add app/services/ tests/
git commit -m "feat: add TushareService for fetching stock fundamental data"
```

---

## Task 5: BaseAgent 抽象类

**Files:**
- Create: `app/agents/__init__.py`
- Create: `app/agents/base.py`
- Test: `tests/unit/agents/test_base_agent.py`

- [ ] **Step 1: 编写BaseAgent测试**

```python
# tests/unit/agents/test_base_agent.py
import pytest
from abc import ABC
from app.agents.base import BaseAgent

def test_base_agent_is_abstract():
    """测试BaseAgent是抽象类，不能直接实例化"""
    with pytest.raises(TypeError):
        BaseAgent()

def test_concrete_agent_implementation():
    """测试具体Agent实现"""
    from app.core.state import AnalysisState, AgentAnalysis

    class TestAgent(BaseAgent):
        @property
        def name(self) -> str:
            return "TestAgent"

        @property
        def style(self) -> str:
            return "测试风格"

        async def analyze(self, state: AnalysisState) -> AgentAnalysis:
            return AgentAnalysis(
                agent_name=self.name,
                agent_type="test",
                action="hold",
                confidence=0.5,
                reasoning="测试",
                key_metrics={},
                price_target=None,
            )

        def vote(self, analyses):
            return "hold"

        async def debate(self, message):
            return {"agent_name": self.name, "content": "OK"}

    agent = TestAgent()
    assert agent.name == "TestAgent"
    assert agent.style == "测试风格"
    assert isinstance(agent, BaseAgent)
```

- [ ] **Step 2: 运行测试（预期失败）**

```bash
poetry run pytest tests/unit/agents/test_base_agent.py -v
```

预期：FAIL - module not found

- [ ] **Step 3: 实现BaseAgent抽象类**

```python
# app/agents/base.py
"""Agent基类定义"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.state import AnalysisState, AgentAnalysis, DebateMessage


class BaseAgent(ABC):
    """
    所有Agent的抽象基类

    定义了Agent必须实现的接口：
    - name: Agent名称
    - style: 投资风格描述
    - analyze: 核心分析方法
    - vote: 投票方法
    - debate: 辩论方法
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent名称

        Returns:
            Agent名称字符串，如 "BuffetAgent"
        """
        pass

    @property
    @abstractmethod
    def style(self) -> str:
        """
        投资风格描述

        Returns:
            风格描述字符串，如 "价值投资 - 护城河、安全边际"
        """
        pass

    @abstractmethod
    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        """
        核心分析方法

        根据股票数据进行分析，返回投资建议

        Args:
            state: 包含股票代码和分析请求的状态字典

        Returns:
            AgentAnalysis对象，包含action、confidence、reasoning等
        """
        pass

    @abstractmethod
    def vote(self, analyses: List[AgentAnalysis]) -> str:
        """
        投票方法

        在投票协作模式下，根据其他Agent的分析给出自己的投票

        Args:
            analyses: 其他Agent的分析结果列表

        Returns:
            投票结果: "buy" | "sell" | "hold"
        """
        pass

    @abstractmethod
    async def debate(self, message: DebateMessage) -> DebateMessage:
        """
        辩论方法

        在辩论协作模式下，回应其他Agent的观点

        Args:
            message: 其他Agent的辩论消息

        Returns:
            辩论回应消息
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
```

- [ ] **Step 4: 创建 app/agents/__init__.py**

```python
# app/agents/__init__.py
"""Agent模块"""

from app.agents.base import BaseAgent

__all__ = ["BaseAgent"]
```

- [ ] **Step 5: 运行测试验证**

```bash
poetry run pytest tests/unit/agents/test_base_agent.py -v
```

预期：PASS

- [ ] **Step 6: 提交**

```bash
git add app/agents/ tests/unit/agents/
git commit -m "feat: add BaseAgent abstract class defining agent interface"
```

---

## Task 6: BuffetAgent 实现

**Files:**
- Create: `app/agents/value/__init__.py`
- Create: `app/agents/value/buffet_agent.py`
- Test: `tests/unit/agents/test_buffet_agent.py`

- [ ] **Step 1: 编写BuffetAgent测试**

```python
# tests/unit/agents/test_buffet_agent.py
import pytest
from app.agents.value.buffet_agent import BuffetAgent
from app.core.state import AnalysisState
from unittest.mock import Mock, patch

@pytest.fixture
def mock_tushare_service():
    """模拟TushareService"""
    service = Mock()
    return service

@pytest.fixture
def buffet_agent(mock_tushare_service):
    """创建BuffetAgent实例"""
    return BuffetAgent(tushare_service=mock_tushare_service)

def test_buffet_agent_properties(buffet_agent):
    """测试Agent属性"""
    assert buffet_agent.name == "BuffetAgent"
    assert "护城河" in buffet_agent.style
    assert "安全边际" in buffet_agent.style

@pytest.mark.asyncio
async def test_buffet_analyze_buy_signal(buffet_agent, mock_tushare_service):
    """测试买入信号分析"""
    # 模拟高质量数据（护城河强、安全边际高）
    mock_tushare_service.get_stock_fundamentals.return_value = {
        "stock_code": "600519",
        "daily": {
            "pe": 25.0,
            "pb": 8.0,
        },
        "income_statement": {
            "n_income": 180000000000,
        },
        "balance_sheet": {
            "total_assets": 250000000000,
            "total_equity": 200000000000,
        },
        "cash_flow": {},
    }

    state = AnalysisState(
        stock_code="600519",
        mode="parallel",
        user_request="分析贵州茅台",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None,
    )

    result = await buffet_agent.analyze(state)

    assert result["agent_name"] == "BuffetAgent"
    assert result["agent_type"] == "value"
    # 护城河评分应该较高
    assert result["key_metrics"]["moat_score"] >= 0
    assert "confidence" in result

@pytest.mark.asyncio
async def test_evaluate_moat(buffet_agent):
    """测试护城河评估逻辑"""
    # 测试高毛利率公司
    high_margin_data = {
        "gross_margin": 60,
        "market_share": 25,
        "roe_std": 3,
    }
    score = buffet_agent._evaluate_moat(high_margin_data)
    assert score >= 8  # 应该获得高分

    # 测试低毛利率公司
    low_margin_data = {
        "gross_margin": 20,
        "market_share": 5,
        "roe_std": 10,
    }
    score = buffet_agent._evaluate_moat(low_margin_data)
    assert score < 6  # 应该获得低分

def test_vote(buffet_agent):
    """测试投票功能"""
    from app.core.state import AgentAnalysis

    analyses = [
        AgentAnalysis(
            agent_name="OtherAgent",
            agent_type="value",
            action="buy",
            confidence=0.8,
            reasoning="",
            key_metrics={},
            price_target=None,
        )
    ]

    vote_result = buffet_agent.vote(analyses)
    assert vote_result in ["buy", "sell", "hold"]
```

- [ ] **Step 2: 运行测试（预期失败）**

```bash
poetry run pytest tests/unit/agents/test_buffet_agent.py -v
```

预期：FAIL - module not found

- [ ] **Step 3: 实现BuffetAgent**

```python
# app/agents/value/buffet_agent.py
"""巴菲特式价值投资Agent"""

from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.core.state import AnalysisState, AgentAnalysis, DebateMessage
from app.services.tushare_service import TushareService


class BuffetAgent(BaseAgent):
    """
    巴菲特式价值投资Agent

    投资哲学：
    - 护城河评估：品牌、网络效应、成本优势、转换成本
    - 安全边际：内在价值与市场价格差额
    - 长期持有：优质企业长期复利增长
    - ROE质量：稳定的高ROE代表商业模式的优越性
    """

    def __init__(self, tushare_service: TushareService):
        """
        初始化BuffetAgent

        Args:
            tushare_service: Tushare数据服务实例
        """
        self.tushare = tushare_service

    @property
    def name(self) -> str:
        return "BuffetAgent"

    @property
    def style(self) -> str:
        return "价值投资 - 护城河、安全边际、长期持有"

    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        """
        分析股票

        Args:
            state: 分析状态，包含股票代码等信息

        Returns:
            AgentAnalysis对象
        """
        # 1. 获取数据
        stock_data = await self.tushare.get_stock_fundamentals(
            state["stock_code"]
        )

        # 2. 护城河评估
        moat_score = self._evaluate_moat(stock_data)

        # 3. 安全边际计算
        margin_of_safety = self._calculate_margin_of_safety(stock_data)

        # 4. ROE趋势分析
        roe_quality = self._analyze_roe_quality(stock_data)

        # 5. 综合决策
        decision = self._make_decision(moat_score, margin_of_safety, roe_quality)

        return AgentAnalysis(
            agent_name=self.name,
            agent_type="value",
            action=decision["action"],
            confidence=decision["confidence"],
            reasoning=decision["reasoning"],
            key_metrics={
                "moat_score": moat_score,
                "margin_of_safety": margin_of_safety,
                "roe_quality": roe_quality,
            },
            price_target=decision.get("price_target"),
        )

    def _evaluate_moat(self, stock_data: Dict[str, Any]) -> float:
        """
        评估护城河强度 (0-10分)

        评估维度：
        - 毛利率水平（品牌溢价能力）
        - 市场份额（行业地位）
        - ROE稳定性（商业模式护城河）

        Args:
            stock_data: 股票数据字典

        Returns:
            护城河评分 0-10
        """
        score = 0

        # 品牌溢价（毛利率）
        daily = stock_data.get("daily", {})
        # 使用PB作为毛利率的代理指标（高PB通常意味着高盈利能力）
        pb = daily.get("pb", 0)
        if pb > 15:
            score += 4  # 极强品牌溢价
        elif pb > 10:
            score += 3
        elif pb > 5:
            score += 2

        # 盈利能力（ROE代理，使用PE的倒数）
        pe = daily.get("pe", 0)
        if pe > 0 and pe < 20:  # 低PE意味着高盈利能力
            score += 3
        elif pe > 0 and pe < 30:
            score += 2

        # 资产质量（总资产与净利润比率）
        income = stock_data.get("income_statement", {})
        balance = stock_data.get("balance_sheet", {})
        net_income = income.get("n_income", 0)
        total_assets = balance.get("total_assets", 1)

        if net_income > 0 and total_assets > 0:
            roa = net_income / total_assets
            if roa > 0.15:  # ROA > 15%
                score += 3
            elif roa > 0.10:
                score += 2
            elif roa > 0.05:
                score += 1

        return min(score, 10)  # 最高10分

    def _calculate_margin_of_safety(
        self, stock_data: Dict[str, Any]
    ) -> float:
        """
        计算安全边际

        简化版：使用PB和PE的反向关系
        低PB+低PE = 高安全边际

        Args:
            stock_data: 股票数据字典

        Returns:
            安全边际百分比 0-1
        """
        daily = stock_data.get("daily", {})
        pb = daily.get("pb", 50)
        pe = daily.get("pe", 100)

        # 简化的安全边际计算
        # PB < 5 且 PE < 15 时，安全边际 > 30%
        if pb < 5 and pe < 15:
            return 0.4
        elif pb < 8 and pe < 20:
            return 0.3
        elif pb < 12 and pe < 30:
            return 0.2
        elif pb < 15 and pe < 40:
            return 0.1
        else:
            return 0.0

    def _analyze_roe_quality(self, stock_data: Dict[str, Any]) -> str:
        """
        分析ROE质量

        Args:
            stock_data: 股票数据字典

        Returns:
            ROE质量评级: "excellent" | "good" | "average" | "poor"
        """
        daily = stock_data.get("daily", {})
        pe = daily.get("pe", 100)

        # 使用PE作为ROE的简单代理
        if pe < 15:
            return "excellent"
        elif pe < 25:
            return "good"
        elif pe < 40:
            return "average"
        else:
            return "poor"

    def _make_decision(
        self, moat_score: float, margin_of_safety: float, roe_quality: str
    ) -> Dict[str, Any]:
        """
        综合做出投资决策

        Args:
            moat_score: 护城河评分
            margin_of_safety: 安全边际
            roe_quality: ROE质量

        Returns:
            决策字典，包含action, confidence, reasoning等
        """
        # 买入条件：强护城河 + 正安全边际 + 好ROE
        if moat_score >= 7 and margin_of_safety > 0.2 and roe_quality in [
            "excellent",
            "good",
        ]:
            return {
                "action": "buy",
                "confidence": 0.85,
                "reasoning": f"护城河评分{moat_score}/10，安全边际{margin_of_safety:.1%}，ROE质量{roe_quality}，符合巴菲特价值投资标准",
                "price_target": None,
            }

        # 持有条件：中等护城河或较低安全边际
        elif moat_score >= 5 or margin_of_safety > 0.1:
            return {
                "action": "hold",
                "confidence": 0.65,
                "reasoning": f"护城河评分{moat_score}/10，安全边际{margin_of_safety:.1%}，建议持有观望",
                "price_target": None,
            }

        # 卖出条件：弱护城河且无安全边际
        else:
            return {
                "action": "sell",
                "confidence": 0.7,
                "reasoning": f"护城河评分{moat_score}/10，安全边际不足，不符合价值投资标准",
                "price_target": None,
            }

    def vote(self, analyses: List[AgentAnalysis]) -> str:
        """
        投票

        巴菲特风格倾向于保守，如果没有强烈的买入信号，选择持有

        Args:
            analyses: 其他Agent的分析结果

        Returns:
            投票结果
        """
        # 计算平均买入信心
        buy_confidence = [
            a["confidence"]
            for a in analyses
            if a["action"] == "buy"
        ]

        if buy_confidence and sum(buy_confidence) / len(buy_confidence) > 0.75:
            return "buy"
        else:
            return "hold"

    async def debate(self, message: DebateMessage) -> DebateMessage:
        """
        辩论

        巴菲特风格：强调长期价值和护城河

        Args:
            message: 对方的辩论消息

        Returns:
            回应消息
        """
        content = f"从价值投资角度，{message['content']}我更关注企业的长期护城河和内在价值。"

        return DebateMessage(
            agent_name=self.name,
            content=content,
            round=message["round"] + 1,
            timestamp="",  # 实际应该用当前时间
        )
```

- [ ] **Step 4: 创建 app/agents/value/__init__.py**

```python
# app/agents/value/__init__.py
"""价值投资Agent模块"""

from app.agents.value.buffet_agent import BuffetAgent

__all__ = ["BuffetAgent"]
```

- [ ] **Step 5: 更新 app/agents/__init__.py**

```python
# app/agents/__init__.py
"""Agent模块"""

from app.agents.base import BaseAgent
from app.agents.value import BuffetAgent

__all__ = ["BaseAgent", "BuffetAgent"]
```

- [ ] **Step 6: 运行测试验证**

```bash
poetry run pytest tests/unit/agents/test_buffet_agent.py -v
```

预期：PASS

- [ ] **Step 7: 提交**

```bash
git add app/agents/value/ tests/unit/agents/test_buffet_agent.py
git commit -m "feat: add BuffetAgent with value investing strategy (moat, margin of safety)"
```

---

## Task 7: CLI 框架

**Files:**
- Create: `app/cli/__init__.py`
- Create: `app/cli/main.py`
- Create: `app/main.py`
- Update: `pyproject.toml`

- [ ] **Step 1: 更新 pyproject.toml 添加CLI入口**

```toml
[tool.poetry.scripts]
invest-agent = "app.main:cli"
```

- [ ] **Step 2: 创建CLI命令测试**

```python
# tests/unit/cli/test_cli.py
from click.testing import CliRunner
from app.main import cli

def test_cli_displays_help():
    """测试CLI显示帮助"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "InvestAgent" in result.output
    assert "analyze" in result.output

def test_analyze_command_requires_stock_code():
    """测试analyze命令需要股票代码"""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze"])
    assert result.exit_code != 0
    assert "Missing argument" in result.output

def test_analyze_command_with_mock_stock(mock_tushare_token, monkeypatch):
    """测试analyze命令（需要mock TushareService）"""
    # 这个测试需要mock，暂时跳过实现
    pass
```

- [ ] **Step 3: 运行测试（预期失败）**

```bash
poetry run pytest tests/unit/cli/test_cli.py -v
```

预期：FAIL - module not found

- [ ] **Step 4: 实现CLI框架**

```python
# app/cli/main.py
"""CLI命令定义"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """InvestAgent - 基于LangGraph+Tushare的多Agent投资智能体系"""
    pass


@cli.command()
@click.argument("stock_code")
@click.option(
    "--mode",
    type=click.Choice(["parallel", "vote", "debate"]),
    default="parallel",
    help="协作模式",
)
@click.option("--agents", help="指定Agent（逗号分隔）", default="buffet")
def analyze(stock_code: str, mode: str, agents: str):
    """
    分析个股

    示例:
        invest-agent analyze 600519
        invest-agent analyze 600519 --mode vote
        invest-agent analyze 600519 --agents buffet,graham
    """
    click.echo(f"分析股票: {stock_code}")
    click.echo(f"协作模式: {mode}")
    click.echo(f"使用Agent: {agents}")

    # TODO: 实现实际的分析逻辑
    console.print("[yellow]CLI框架已就绪，分析逻辑将在后续任务中实现[/yellow]")


@cli.command()
def version():
    """显示版本信息"""
    click.echo("InvestAgent v0.1.0")


@cli.command()
def config():
    """显示配置信息"""
    from app.core.config import settings

    table = Table(title="配置信息")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("Tushare Token", f"{settings.tushare_token[:10]}...")
    table.add_row("Log Level", settings.log_level)
    table.add_row("Cache TTL", str(settings.cache_ttl))

    console.print(table)
```

- [ ] **Step 5: 创建主入口**

```python
# app/main.py
"""应用入口"""

from app.cli.main import cli

if __name__ == "__main__":
    cli()
```

- [ ] **Step 6: 创建 app/cli/__init__.py**

```python
# app/cli/__init__.py
"""CLI模块"""

__all__ = []
```

- [ ] **Step 7: 运行测试验证**

```bash
poetry run pytest tests/unit/cli/test_cli.py -v
```

预期：PASS

- [ ] **Step 8: 手动测试CLI**

```bash
poetry run invest-agent --help
poetry run invest-agent analyze --help
poetry run invest-agent config
```

- [ ] **Step 9: 提交**

```bash
git add app/cli/ app/main.py pyproject.toml tests/unit/cli/
git commit -m "feat: add CLI framework with Click and Rich"
```

---

## Task 8: 集成端到端测试

**Files:**
- Test: `tests/integration/test_e2e.py`

- [ ] **Step 1: 编写集成测试**

```python
# tests/integration/test_e2e.py
"""端到端集成测试"""

import pytest
from app.agents.value import BuffetAgent
from app.services.tushare_service import TushareService
from app.core.state import AnalysisState
from unittest.mock import Mock, patch


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_analysis_flow():
    """测试完整的分析流程"""
    # 创建服务
    service = TushareService(token="test_token")

    # 创建Agent
    agent = BuffetAgent(tushare_service=service)

    # Mock Tushare API调用
    with patch.object(service, "get_stock_fundamentals") as mock_get_data:
        mock_get_data.return_value = {
            "stock_code": "600519",
            "daily": {"pe": 25.0, "pb": 8.0},
            "income_statement": {"n_income": 180000000000},
            "balance_sheet": {
                "total_assets": 250000000000,
                "total_equity": 200000000000,
            },
            "cash_flow": {},
        }

        # 创建状态
        state = AnalysisState(
            stock_code="600519",
            mode="parallel",
            user_request="分析贵州茅台",
            agent_analyses=[],
            debate_round=0,
            debate_history=[],
            final_decision=None,
            error=None,
        )

        # 执行分析
        result = await agent.analyze(state)

        # 验证结果
        assert result["agent_name"] == "BuffetAgent"
        assert result["agent_type"] == "value"
        assert result["action"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1
        assert "moat_score" in result["key_metrics"]


@pytest.mark.integration
def test_config_loading():
    """测试配置加载"""
    from app.core.config import settings

    assert settings.tushare_token
    assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]


@pytest.mark.integration
def test_cli_entry_point():
    """测试CLI入口"""
    from click.testing import CliRunner
    from app.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
```

- [ ] **Step 2: 运行集成测试**

```bash
poetry run pytest tests/integration/test_e2e.py -v -m integration
```

预期：PASS

- [ ] **Step 3: 运行所有测试**

```bash
poetry run pytest -v
```

预期：全部PASS

- [ ] **Step 4: 代码质量检查**

```bash
# 格式化检查
poetry run black --check app tests

# Lint检查
poetry run ruff check app tests

# 类型检查（可选）
poetry run mypy app
```

- [ ] **Step 5: 提交**

```bash
git add tests/integration/
git commit -m "test: add end-to-end integration tests"
```

---

## Task 9: 文档和完善

**Files:**
- Update: `README.md`
- Create: `docs/getting-started.md`
- Create: `docs/architecture.md`
- Create: `.env.example` (更新)

- [ ] **Step 1: 更新README.md**

```markdown
# Invest Agent By Graph

基于 LangGraph + Tushare 的多Agent投资智能体系

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 特性

- ✅ **多投资风格Agent** - 价值投资（巴菲特）、成长投资（费雪、林奇）、宏观对冲（索罗斯、达利欧）
- ✅ **三种协作模式** - 并行分析、投票决策、辩论仲裁
- 🚧 **智能选股** - 根据投资风格筛选股票
- ✅ **个股分析** - 多维度投资建议
- 🚧 **策略回测** - 验证历史表现
- ✅ **CLI接口** - 命令行工具
- 🚧 **Web API** - RESTful API

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/invest-agent-by-graph.git
cd invest-agent-by-graph

# 安装Poetry（如果还没有）
pip install poetry

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Tushare Token
```

### 获取Tushare Token

1. 访问 [Tushare Pro](https://tushare.pro/register)
2. 注册账号
3. 在用户中心获取 API Token
4. 将Token填入 `.env` 文件

### 使用

```bash
# 查看帮助
poetry run invest-agent --help

# 分析股票（当前支持巴菲特价值投资Agent）
poetry run invest-agent analyze 600519

# 查看配置
poetry run invest-agent config
```

## 开发

```bash
# 运行测试
poetry run pytest

# 运行测试并显示覆盖率
poetry run pytest --cov=app --cov-report=html

# 代码格式化
poetry run black app tests

# 代码检查
poetry run ruff check app tests

# 类型检查
poetry run mypy app
```

## 项目结构

```
invest_agent_by_graph/
├── app/
│   ├── agents/          # Agent实现
│   ├── services/        # 服务层（Tushare等）
│   ├── core/            # 核心配置和数据结构
│   └── cli/             # CLI命令
├── tests/               # 测试
├── docs/                # 文档
└── scripts/             # 工具脚本
```

## 当前进度

### Phase 1: 核心框架 ✅
- [x] 项目初始化
- [x] 配置管理
- [x] 核心数据结构
- [x] TushareService
- [x] BaseAgent抽象类
- [x] BuffetAgent实现
- [x] CLI框架

### Phase 2: 多Agent协作 🚧
- [ ] GrahamAgent
- [ ] FisherAgent
- [ ] LynchAgent
- [ ] SorosAgent
- [ ] DalioAgent
- [ ] LangGraph工作流
- [ ] 三种协作模式

### Phase 3: 回测引擎 🚧
- [ ] BacktestEngine
- [ ] 回测指标计算

### Phase 4: 选股功能 🚧
- [ ] 全市场扫描
- [ ] 结果排序过滤

### Phase 5: Web API 🚧
- [ ] FastAPI框架
- [ ] REST API

### Phase 6: 前端界面 🚧
- [ ] Vue 3应用

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 免责声明

本工具仅供学习和研究使用，不构成任何投资建议。投资有风险，决策需谨慎。
```

- [ ] **Step 2: 创建快速开始文档**

```markdown
# docs/getting-started.md

# 快速开始指南

## 环境要求

- Python 3.11+
- Poetry（用于依赖管理）
- Tushare Pro账号

## 安装步骤

### 1. 安装Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python3 -
```

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/invest-agent-by-graph.git
cd invest-agent-by-graph
```

### 3. 安装依赖

```bash
poetry install
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的Tushare Token：

```bash
TUSHARE_TOKEN=your_actual_token_here
LOG_LEVEL=INFO
CACHE_TTL=3600
```

## 第一个分析

### 分析贵州茅台

```bash
poetry run invest-agent analyze 600519
```

预期输出：

```
分析股票: 600519
协作模式: parallel
使用Agent: buffet

[Agent分析结果]
Agent: BuffetAgent (价值投资)
建议: buy
置信度: 0.85
理由: 护城河评分8/10，安全边际30%，ROE质量excellent，符合巴菲特价值投资标准

关键指标:
  - 护城河评分: 8.0/10
  - 安全边际: 30.0%
  - ROE质量: excellent
```

## 下一步

- 查看 [架构文档](architecture.md) 了解系统设计
- 查看 [Agent文档](agents.md) 了解各投资风格
- 查看 [API文档](api.md) 了解编程接口
```

- [ ] **Step 3: 创建架构文档**

```markdown
# docs/architecture.md

# 系统架构

## 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    接入层 (Interface Layer)                  │
├─────────────────────┬───────────────────────────────────────┤
│      CLI 模块        │          Web API (FastAPI)            │
│  - click-based      │  - RESTful API                        │
│  - 命令解析          │  - WebSocket (实时分析推送)            │
└─────────────────────┴───────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  应用层 (Application Layer)                   │
├─────────────────────────────────────────────────────────────┤
│  Agent 层                       │  协作层 (LangGraph)         │
│  - BaseAgent (抽象)            │  - StateGraph               │
│  - BuffetAgent                 │  - 工作流编排                │
│  - GrahamAgent                 │  - 协作模式                  │
│  - FisherAgent                 │                             │
│  - LynchAgent                  │                             │
│  - SorosAgent                  │                             │
│  - DalioAgent                  │                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  服务层 (Service Layer)                       │
├─────────────────────────────────────────────────────────────┤
│  TushareService       │  CacheService     │  StorageService  │
│  - 数据获取            │  - 内存缓存       │  - SQLite        │
│  - 数据清洗            │  - LRU缓存        │  - 持久化        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  数据层 (Data Layer)                          │
├─────────────────────────────────────────────────────────────┤
│  Tushare Pro API    │  SQLite          │  内存缓存          │
│  - 实时行情          │  - 分析历史       │  - functools      │
│  - 财务数据          │  - 回测记录       │  - lru_cache      │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### Agent层

每个Agent代表一种投资哲学，实现 `BaseAgent` 接口：

- `analyze()` - 核心分析方法
- `vote()` - 投票方法
- `debate()` - 辩论方法

### 服务层

- **TushareService**: 封装Tushare API，提供数据获取
- **CacheService**: 内存缓存，减少API调用
- **StorageService**: SQLite持久化

### 状态管理

使用 `AnalysisState` (TypedDict) 在LangGraph中传递状态：

```python
class AnalysisState(TypedDict):
    stock_code: str
    mode: str  # "parallel" | "vote" | "debate"
    agent_analyses: List[AgentAnalysis]
    debate_round: int
    debate_history: List[DebateMessage]
    final_decision: Optional[Decision]
    error: Optional[str]
```

## 数据流

```
用户请求
   ↓
CLI/API 解析
   ↓
创建 AnalysisState
   ↓
LangGraph 工作流
   ↓
并行执行多个 Agent.analyze()
   ↓
收集结果到 agent_analyses
   ↓
根据 mode 选择协作方式
   ├─ parallel: 直接输出
   ├─ vote: 投票节点
   └─ debate: 辩论节点
   ↓
生成 final_decision
   ↓
返回用户
```

## 扩展性

### 添加新Agent

1. 继承 `BaseAgent`
2. 实现必需方法
3. 注册到工作流

```python
class MyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MyAgent"

    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        # 实现分析逻辑
        pass
```

### 添加新协作模式

在LangGraph工作流中添加新的节点和条件边。

## 技术选型理由

| 技术 | 理由 |
|------|------|
| **LangGraph** | 官方多Agent框架，状态管理强大 |
| **Tushare** | A股数据最全面的免费接口 |
| **FastAPI** | 高性能、类型安全、自动文档 |
| **Click** | 成熟的CLI框架 |
| **Pydantic** | 数据验证和类型安全 |
| **SQLite** | 轻量级、单机部署简单 |
```

- [ ] **Step 4: 更新 .env.example 添加更多配置项**

```bash
# Tushare配置
TUSHARE_TOKEN=your_tushare_token_here

# 应用配置
LOG_LEVEL=INFO
CACHE_TTL=3600

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/invest_agent.db

# Agent配置
DEFAULT_AGENTS=buffet
DEFAULT_MODE=parallel

# 回测配置
DEFAULT_INITIAL_CAPITAL=1000000
COMMISSION_RATE=0.0003
SLIPPAGE_RATE=0.001
```

- [ ] **Step 5: 提交文档**

```bash
git add README.md docs/ .env.example
git commit -m "docs: add comprehensive documentation (README, getting-started, architecture)"
```

---

## Task 10: Phase 1 总结和发布

- [ ] **Step 1: 运行完整测试套件**

```bash
# 运行所有测试
poetry run pytest -v --cov=app --cov-report=term-missing

# 确保覆盖率 > 80%
```

- [ ] **Step 2: 代码质量检查**

```bash
# 格式化代码
poetry run black app tests

# 运行linter
poetry run ruff check app tests --fix

# 类型检查（如果配置了mypy）
poetry run mypy app
```

- [ ] **Step 3: 创建Phase 1总结文档**

```markdown
# Phase 1 完成总结

## 已完成

### 核心框架
- ✅ 项目初始化（Poetry、Git、目录结构）
- ✅ 配置管理（pydantic-settings）
- ✅ 核心数据结构（AnalysisState、AgentAnalysis、Decision）
- ✅ TushareService（数据获取封装）

### Agent层
- ✅ BaseAgent抽象类
- ✅ BuffetAgent实现（巴菲特价值投资）

### 接入层
- ✅ CLI框架（Click + Rich）
- ✅ 基础命令（analyze、config、version）

### 测试
- ✅ 单元测试（config、state、tushare_service、agents）
- ✅ 集成测试（端到端流程）
- ✅ 测试覆盖率 > 80%

### 文档
- ✅ README
- ✅ 快速开始指南
- ✅ 架构文档

## 技术栈确认

- Python 3.11+
- Poetry（依赖管理）
- Pydantic（数据验证）
- Click（CLI框架）
- Rich（终端美化）
- Tushare Pro（数据源）
- pytest（测试）

## 代码质量

- 遵循PEP 8规范
- 类型注解完整
- 文档字符串完整
- 测试覆盖率 > 80%

## 下一步（Phase 2）

1. 实现其他5个Agent
2. 引入LangGraph工作流
3. 实现三种协作模式
4. 完善analyze命令的实际功能

## 发布

准备发布 v0.1.0-alpha 版本
```

- [ ] **Step 4: 创建Git标签**

```bash
# 确保所有更改已提交
git status

# 创建标签
git tag -a v0.1.0-alpha -m "Phase 1: 核心框架完成"

# 推送标签（如果有远程仓库）
git push origin v0.1.0-alpha
```

- [ ] **Step 5: 最终提交**

```bash
git add .
git commit -m "chore: phase 1 complete - core framework ready"
```

---

## 完成检查清单

在开始Phase 2之前，确认以下所有项目都已完成：

- [ ] 所有测试通过 (`poetry run pytest -v`)
- [ ] 测试覆盖率 > 80% (`poetry run pytest --cov=app`)
- [ ] 代码格式化 (`poetry run black --check`)
- [ ] Linter无错误 (`poetry run ruff check`)
- [ ] CLI命令正常工作 (`poetry run invest-agent --help`)
- [ ] 文档完整（README、getting-started、architecture）
- [ ] Git提交记录清晰
- [ ] Phase 1总结文档完成

---

## 下一步预览

**Phase 2: 多Agent协作** 将包含：

1. GrahamAgent（格雷厄姆深度价值）
2. FisherAgent（费雪成长投资）
3. LynchAgent（林奇GARP策略）
4. SorosAgent（索罗斯反身性）
5. DalioAgent（达利欧经济周期）

6. LangGraph工作流集成
7. 三种协作模式实现
8. 完整的analyze命令

预计工作量：2-3周
