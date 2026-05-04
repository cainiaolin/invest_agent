# Phase 2: 多Agent协作与LangGraph集成

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 实现5个新Agent（Graham、Fisher、Lynch、Soros、Dalio），集成LangGraph工作流，实现三种协作模式，完善analyze命令

**架构:** Agent层扩展 + LangGraph编排层引入

**技术栈:** Python 3.11+, LangGraph, LangChain, Phase 1成果

---

## Phase 1 成果回顾

Phase 1 已完成：
- ✅ 项目初始化和配置管理
- ✅ 核心数据结构 (AnalysisState, AgentAnalysis, Decision)
- ✅ TushareService 数据服务
- ✅ BaseAgent 抽象类
- ✅ BuffetAgent (巴菲特价值投资)
- ✅ CLI 框架
- ✅ 测试套件
- ✅ 文档

---

## 文件结构扩展

```
invest_agent_by_graph/
├── app/
│   ├── agents/
│   │   ├── base.py                    # ✅ Phase 1完成
│   │   ├── value/
│   │   │   ├── buffet_agent.py        # ✅ Phase 1完成
│   │   │   └── graham_agent.py        # 🆕 Phase 2
│   │   ├── growth/
│   │   │   ├── fisher_agent.py        # 🆕 Phase 2
│   │   │   └── lynch_agent.py         # 🆕 Phase 2
│   │   └── macro/
│   │       ├── soros_agent.py         # 🆕 Phase 2
│   │       └── dalio_agent.py         # 🆕 Phase 2
│   │
│   ├── graph/                         # 🆕 LangGraph工作流
│   │   ├── __init__.py
│   │   ├── workflow.py                # 主工作流定义
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # 路由节点
│   │   │   ├── agents.py              # Agent执行节点
│   │   │   ├── collaboration.py       # 协作节点（投票/辩论）
│   │   │   └── output.py              # 输出节点
│   │   └── edges/
│   │       ├── __init__.py
│   │       └── conditions.py          # 条件边函数
│   │
│   └── cli/
│       ├── main.py                     # ✅ Phase 1完成
│       └── commands/
│           ├── __init__.py
│           └── analyze.py             # 🆕 完整analyze命令
│
├── tests/
│   ├── unit/
│   │   ├── agents/                    # ✅ Phase 1完成
│   │   │   ├── test_graham_agent.py   # 🆕 Phase 2
│   │   │   ├── test_fisher_agent.py   # 🆕 Phase 2
│   │   │   ├── test_lynch_agent.py    # 🆕 Phase 2
│   │   │   ├── test_soros_agent.py    # 🆕 Phase 2
│   │   │   └── test_dalio_agent.py    # 🆕 Phase 2
│   │   └── graph/                     # 🆕 Phase 2
│   │       ├── test_workflow.py
│   │       ├── test_nodes.py
│   │       └── test_edges.py
│   └── integration/
│       └── test_collaboration.py      # 🆕 Phase 2
│
├── pyproject.toml                      # 🔄 更新依赖
└── docs/
    └── agents.md                       # 🆕 Agent文档
```

---

## Task 1: 更新项目依赖

**Files:**
- Update: `pyproject.toml`

- [ ] **Step 1: 添加LangGraph和LangChain依赖**

```toml
[tool.poetry.dependencies]
python = "^3.11"
click = "^8.1.7"
rich = "^13.7.0"
pydantic = "^2.6.0"
pydantic-settings = "^2.1.0"
tushare = "^1.2.90"
python-dotenv = "^1.0.0"
# 新增
langgraph = "^0.2.0"
langchain = "^0.3.0"
langchain-core = "^0.3.0"
```

- [ ] **Step 2: 安装新依赖**

```bash
poetry lock
poetry install
```

- [ ] **Step 3: 提交**

```bash
git add pyproject.toml poetry.lock
git commit -m "feat: add LangGraph and LangChain dependencies for Phase 2"
```

---

## Task 2: GrahamAgent（格雷厄姆深度价值）

**Files:**
- Create: `app/agents/value/graham_agent.py`
- Create: `tests/unit/agents/test_graham_agent.py`
- Update: `app/agents/value/__init__.py`
- Update: `app/agents/__init__.py`

- [ ] **Step 1: 编写测试**

```python
# tests/unit/agents/test_graham_agent.py
import pytest
from app.agents.value.graham_agent import GrahamAgent
from app.core.state import AnalysisState
from unittest.mock import Mock

@pytest.fixture
def mock_tushare_service():
    return Mock()

@pytest.fixture
def graham_agent(mock_tushare_service):
    return GrahamAgent(tushare_service=mock_tushare_service)

def test_graham_agent_properties(graham_agent):
    assert graham_agent.name == "GrahamAgent"
    assert "深度价值" in graham_agent.style
    assert "安全边际" in graham_agent.style

@pytest.mark.asyncio
async def test_graham_screening_criteria(graham_agent, mock_tushare_service):
    """测试格雷厄姆选股标准"""
    # 模拟被低估的优质股票
    mock_tushare_service.get_stock_fundamentals.return_value = {
        "daily": {"pe": 8.0, "pb": 1.2},  # 低PE、低PB
        "income_statement": {"n_income": 5000000000},
        "balance_sheet": {
            "total_assets": 50000000000,
            "total_liab": 10000000000,
            "total_equity": 40000000000,
        },
        "cash_flow": {},
    }

    state = AnalysisState(
        stock_code="000001",
        mode="parallel",
        user_request="深度价值分析",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None,
    )

    result = await graham_agent.analyze(state)

    assert result["agent_name"] == "GrahamAgent"
    assert result["agent_type"] == "value"
    assert result["key_metrics"]["value_score"] >= 0
```

- [ ] **Step 2: 实现GrahamAgent**

```python
# app/agents/value/graham_agent.py
"""格雷厄姆式深度价值投资Agent"""

from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.core.state import AnalysisState, AgentAnalysis, DebateMessage
from app.services.tushare_service import TushareService


class GrahamAgent(BaseAgent):
    """
    格雷厄姆式深度价值投资Agent
    
    投资哲学：
    - 深度价值：寻找被严重低估的优质公司
    - 安全第一：强调本金安全和下行保护
    - 格雷厄姆公式：内在价值 = √(22.5 × 最高EPS × 最低BVPS)
    - 净净 net-net：流动资产减去总负债低于市值
    - 盈利收益率：PE倒数 > 2倍AAA债券收益率
    """

    def __init__(self, tushare_service: TushareService):
        self.tushare = tushare_service

    @property
    def name(self) -> str:
        return "GrahamAgent"

    @property
    def style(self) -> str:
        return "深度价值投资 - 安全边际、内在价值、净净估值"

    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        # 1. 获取数据
        stock_data = await self.tushare.get_stock_fundamentals(state["stock_code"])

        # 2. 格雷厄姆价值评估
        intrinsic_value = self._graham_formula(stock_data)
        margin_of_safety = self._calculate_margin(stock_data, intrinsic_value)
        net_net_score = self._net_net_analysis(stock_data)
        earnings_yield = self._earnings_yield_analysis(stock_data)

        # 3. 决策逻辑（非常严格的价值标准）
        if (margin_of_safety > 0.5 and 
            net_net_score > 7 and 
            earnings_yield > 0.10):
            action = "buy"
            confidence = 0.90
        elif margin_of_safety > 0.3 or net_net_score > 5:
            action = "hold"
            confidence = 0.60
        else:
            action = "sell"
            confidence = 0.75

        return AgentAnalysis(
            agent_name=self.name,
            agent_type="value",
            action=action,
            confidence=confidence,
            reasoning=f"内在价值{intrinsic_value:.2f}，安全边际{margin_of_safety:.1%}，Net-Net评分{net_net_score}/10",
            key_metrics={
                "intrinsic_value": intrinsic_value,
                "margin_of_safety": margin_of_safety,
                "net_net_score": net_net_score,
                "earnings_yield": earnings_yield,
            },
            price_target=intrinsic_value * 0.7,
        )

    def _graham_formula(self, stock_data: Dict[str, Any]) -> float:
        """格雷厄姆公式计算内在价值"""
        daily = stock_data.get("daily", {})
        # 简化版本：使用合理PE和合理PB估算
        pe = daily.get("pe", 50)
        pb = daily.get("pb", 10)
        eps = 1.0 / pe if pe > 0 else 0
        bvps = 1.0 / pb if pb > 0 else 0

        # 格雷厄姆公式：√(22.5 × EPS × BVPS)
        if eps > 0 and bvps > 0:
            return (22.5 * eps * bvps) ** 0.5
        return 0

    def _calculate_margin(self, stock_data: Dict[str, Any], intrinsic_value: float) -> float:
        """计算安全边际"""
        daily = stock_data.get("daily", {})
        current_price = daily.get("close", intrinsic_value * 2)

        if current_price > 0:
            return max(0, (intrinsic_value - current_price) / intrinsic_value)
        return 0

    def _net_net_analysis(self, stock_data: Dict[str, Any]) -> float:
        """Net-Net分析（0-10分）"""
        balance = stock_data.get("balance_sheet", {})
        daily = stock_data.get("daily", {})

        total_assets = balance.get("total_assets", 0)
        total_liab = balance.get("total_liab", 0)
        market_cap = daily.get("total_mv", total_assets)

        # 净净 = (流动资产 - 总负债) / 市值
        # 简化：使用总资产代替流动资产
        if market_cap > 0:
            net_net = (total_assets - total_liab) / market_cap
            # Net-Net < 0.5 时极具吸引力
            if net_net < 0.5:
                return 10
            elif net_net < 0.8:
                return 8
            elif net_net < 1.0:
                return 6
            elif net_net < 1.5:
                return 4
            else:
                return 2
        return 0

    def _earnings_yield_analysis(self, stock_data: Dict[str, Any]) -> float:
        """盈利收益率分析"""
        daily = stock_data.get("daily", {})
        pe = daily.get("pe", 100)

        # 盈利收益率 = EPS / 价格 = 1 / PE
        if pe > 0:
            return 1.0 / pe
        return 0

    def vote(self, analyses: List[AgentAnalysis]) -> str:
        """格雷厄姆风格：极度保守"""
        # 只在强烈低估信号时买入
        buy_signals = [a for a in analyses if a["action"] == "buy" and a["confidence"] > 0.85]
        if len(buy_signals) >= 2:
            return "buy"
        return "hold"

    async def debate(self, message: DebateMessage) -> DebateMessage:
        """辩论：强调安全第一"""
        content = f"作为价值投资者，{message['content']}我的首要原则是不要亏损。让我们看看安全边际是否足够。"
        return DebateMessage(
            agent_name=self.name,
            content=content,
            round=message["round"] + 1,
            timestamp="",
        )
```

- [ ] **Step 3-7: 测试、更新模块导入、提交**

```bash
# 运行测试
poetry run pytest tests/unit/agents/test_graham_agent.py -v

# 更新 app/agents/value/__init__.py
# 添加: from app.agents.value.graham_agent import GrahamAgent

# 更新 app/agents/__init__.py  
# 添加: from app.agents.value import GrahamAgent

# 提交
git add app/agents/ tests/
git commit -m "feat: add GrahamAgent with deep value investing strategy"
```

---

## Task 3: FisherAgent（费雪成长投资）

**关键实现要点：**

费雪八大选股标准：
1. 盈利能力持久性（产品生命周期长）
2. 盈利增长意愿（管理层诚信，愿意分红）
3. 盈利增长能力（高ROE，持续 reinvestment）
4. 成本控制（高毛利，规模效应）
5. 研发投入（创新护城河）
6. 销售组织（渠道优势）
7. 员工关系（人才保留）
8. 内部控制（财务透明）

**实现结构：**

```python
class FisherAgent(BaseAgent):
    """费雪式成长投资Agent"""
    
    def _evaluate_growth_quality(self, stock_data) -> float:  # 0-10分
        """评估成长质量（8个维度）"""
        
    def _analyze_roe_trend(self, stock_data) -> str:
        """ROE趋势分析"""
        
    def _check_rnd_investment(self, stock_data) -> float:
        """研发投入分析"""
```

---

## Task 4: LynchAgent（林奇GARP策略）

**关键实现要点：**

林奇13条选股特征：
1. 业务简单易懂
2. 业务有枯燥乏味感（被忽视）
3. 业务有令人不悦或压抑感
4. 从利基市场退出（子公司独立）
5. 机构不持有（小盘股）
6. 有谣言（债务危机）
7. 处于零增长行业（但公司在增长）
8. 有护城河（品牌、特许经营权）
9. 人们需要不断购买的产品
10. 高回购买股票
11. 暂时性问题（可解决）
12. 高自由现金流
13. 快速增长行业中

**PEG策略：**
- PEG = PE / 增长率
- PEG < 1 = 被低估
- PEG 1-2 = 合理
- PEG > 2 = 被高估

---

## Task 5: SorosAgent（索罗斯反身性）

**关键实现要点：**

反身性理论：
1. 市场偏见影响价格
2. 价格影响基本面（自我强化）
3. 强化趋势最终会逆转
4. 在趋势逆转前获利

**实现逻辑：**
```python
class SorosAgent(BaseAgent):
    """索罗斯式宏观对冲Agent"""
    
    def _detect_reflexivity(self, stock_data) -> str:
        """检测反身性循环"""
        # 上涨趋势 + 正面预期 = 看多泡沫
        # 下跌趋势 + 负面预期 = 看空恐慌
        
    def _identify_trend_stage(self, stock_data) -> str:
        """识别趋势阶段"""
        # 早期 -> 加速 -> 成熟 -> 逆转
```

---

## Task 6: DalioAgent（达利欧经济周期）

**关键实现要点：**

全天候策略 + 经济周期判断：
1. 短期债务周期（5-10年）
2. 长期债务周期（50-75年）
3. 四个季节：通胀、衰退、萧条、复苏
4. 资产配置：股票、债券、黄金、商品

**实现逻辑：**
```python
class DalioAgent(BaseAgent):
    """达利欧式宏观对冲Agent"""
    
    def _analyze_economic_cycle(self, stock_data) -> str:
        """判断经济周期阶段"""
        
    def _portfolio_allocation(self) -> Dict[str, float]:
        """全天候资产配置"""
```

---

## Task 7: 创建LangGraph工作流

**Files:**
- Create: `app/graph/workflow.py`
- Create: `app/graph/nodes/router.py`
- Create: `app/graph/nodes/agents.py`
- Create: `app/graph/nodes/collaboration.py`
- Create: `app/graph/nodes/output.py`
- Create: `app/graph/edges/conditions.py`

- [ ] **Step 1: 创建路由节点**

```python
# app/graph/nodes/router.py
"""路由节点 - 决定使用哪些Agent"""

from app.core.state import AnalysisState

AGENT_REGISTRY = {
    "buffet": "BuffetAgent",
    "graham": "GrahamAgent",
    "fisher": "FisherAgent",
    "lynch": "LynchAgent",
    "soros": "SorosAgent",
    "dalio": "DalioAgent",
}

async def route_analysis(state: AnalysisState) -> AnalysisState:
    """
    路由分析请求到适当的Agent
    
    根据用户请求或默认配置选择Agent
    """
    user_request = state.get("user_request", "").lower()
    
    # 关键词匹配Agent选择
    if "价值" in user_request or "低估" in user_request:
        selected_agents = ["buffet", "graham"]
    elif "成长" in user_request or "增长" in user_request:
        selected_agents = ["fisher", "lynch"]
    elif "宏观" in user_request or "周期" in user_request:
        selected_agents = ["soros", "dalio"]
    else:
        # 默认使用所有Agent
        selected_agents = list(AGENT_REGISTRY.keys())
    
    # 保存选中的Agent列表到状态
    state["selected_agents"] = selected_agents
    
    return state
```

- [ ] **Step 2: 创建Agent执行节点**

```python
# app/graph/nodes/agents.py
"""Agent执行节点 - 并行运行多个Agent分析"""

from typing import Dict, Any
from app.core.state import AnalysisState
from app.agents import (
    BuffetAgent, GrahamAgent, FisherAgent, 
    LynchAgent, SorosAgent, DalioAgent
)
from app.services.tushare_service import TushareService

# Agent工厂
AGENT_FACTORY = {
    "buffet": BuffetAgent,
    "graham": GrahamAgent,
    "fisher": FisherAgent,
    "lynch": LynchAgent,
    "soros": SorosAgent,
    "dalio": DalioAgent,
}

async def execute_agent_analysis(state: AnalysisState, agent_name: str) -> dict:
    """执行单个Agent的分析"""
    tushare_service = TushareService(token="test_token")
    agent_class = AGENT_FACTORY[agent_name]
    agent = agent_class(tushare_service=tushare_service)
    
    analysis = await agent.analyze(state)
    return {"agent": agent_name, "result": analysis}
```

- [ ] **Step 3: 创建协作节点**

```python
# app/graph/nodes/collaboration.py
"""协作节点 - 实现三种协作模式"""

from app.core.state import AnalysisState, Decision

async def vote_collaboration(state: AnalysisState) -> AnalysisState:
    """投票协作模式"""
    analyses = state.get("agent_analyses", [])
    
    # 统计投票
    votes = {"buy": 0, "sell": 0, "hold": 0}
    weighted_score = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
    
    for analysis in analyses:
        action = analysis.get("action", "hold")
        confidence = analysis.get("confidence", 0.5)
        votes[action] += 1
        weighted_score[action] += confidence
    
    # 找出最高票
    max_votes = max(votes.values())
    winners = [k for k, v in votes.items() if v == max_votes]
    
    # 如果有平局，用加权分数决定
    if len(winners) > 1:
        winner = max(winners, key=lambda k: weighted_score[k])
    else:
        winner = winners[0]
    
    # 计算共识度
    total_agents = len(analyses)
    consensus = votes[winner] / total_agents if total_agents > 0 else 0
    
    state["final_decision"] = Decision(
        action=winner,
        consensus=consensus,
        participating_agents=[a["agent_name"] for a in analyses],
        summary=f"投票模式：{votes['buy']}票买入，{votes['sell']}票卖出，{votes['hold']}票持有",
    )
    
    return state

async def debate_collaboration(state: AnalysisState) -> AnalysisState:
    """辩论协作模式"""
    # 实现3轮辩论逻辑
    analyses = state.get("agent_analyses", [])
    debate_history = []
    
    for round_num in range(3):
        # 选择立场分歧最大的两个Agent进行辩论
        # ...辩论逻辑...
        
        debate_message = {
            "agent_name": agent.name,
            "content": content,
            "round": round_num + 1,
            "timestamp": "",
        }
        debate_history.append(debate_message)
    
    state["debate_history"] = debate_history
    
    # 仲裁者综合判断
    # ...仲裁逻辑...
    
    return state
```

- [ ] **Step 4: 创建工作流**

```python
# app/graph/workflow.py
"""LangGraph工作流定义"""

from langgraph.graph import StateGraph, END
from app.core.state import AnalysisState
from app.graph.nodes import router, agents, collaboration, output

def create_investment_graph() -> StateGraph:
    """创建投资分析工作流图"""
    
    workflow = StateGraph(AnalysisState)
    
    # 添加节点
    workflow.add_node("router", router.route_analysis)
    workflow.add_node("buffet_agent", lambda s: agents.execute_agent_analysis(s, "buffet"))
    workflow.add_node("graham_agent", lambda s: agents.execute_agent_analysis(s, "graham"))
    workflow.add_node("fisher_agent", lambda s: agents.execute_agent_analysis(s, "fisher"))
    workflow.add_node("lynch_agent", lambda s: agents.execute_agent_analysis(s, "lynch"))
    workflow.add_node("soros_agent", lambda s: agents.execute_agent_analysis(s, "soros"))
    workflow.add_node("dalio_agent", lambda s: agents.execute_agent_analysis(s, "dalio"))
    workflow.add_node("vote_collaborator", collaboration.vote_collaboration)
    workflow.add_node("debate_collaborator", collaboration.debate_collaboration)
    workflow.add_node("output", output.format_output)
    
    # 设置入口
    workflow.set_entry_point("router")
    
    # 添加边
    workflow.add_edge("router", "buffet_agent")
    workflow.add_edge("buffet_agent", "graham_agent")
    # ... 其他Agent的边
    
    # 条件边：根据mode选择协作方式
    workflow.add_conditional_edges(
        "dalio_agent",
        lambda s: s.get("mode", "parallel"),
        {
            "parallel": "output",
            "vote": "vote_collaborator",
            "debate": "debate_collaborator",
        }
    )
    
    workflow.add_edge("vote_collaborator", "output")
    workflow.add_edge("debate_collaborator", "output")
    workflow.add_edge("output", END)
    
    return workflow.compile()
```

---

## Task 8: 完善CLI analyze命令

**Files:**
- Update: `app/cli/main.py`
- Create: `app/cli/commands/analyze.py`

- [ ] **实现完整analyze命令**

```python
# app/cli/commands/analyze.py
"""完整的analyze命令实现"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from app.graph.workflow import create_investment_graph
from app.core.state import AnalysisState

console = Console()

@click.command()
@click.argument("stock_code")
@click.option(
    "--mode",
    type=click.Choice(["parallel", "vote", "debate"]),
    default="parallel",
    help="协作模式",
)
@click.option(
    "--agents",
    help="指定Agent（逗号分隔）",
    default="all",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="详细输出",
)
def analyze(stock_code: str, mode: str, agents: str, verbose: bool):
    """
    分析股票 - 使用多Agent协作分析
    
    示例:
        invest-agent analyze 600519
        invest-agent analyze 600519 --mode vote
        invest-agent analyze 600519 --agents buffet,graham --mode debate
    """
    console.print(f"[bold cyan]分析股票：[/bold cyan] {stock_code}")
    console.print(f"[dim]协作模式：{mode}[/dim]")
    
    # 创建状态
    state = AnalysisState(
        stock_code=stock_code,
        mode=mode,
        user_request=f"分析股票{stock_code}",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None,
    )
    
    # 运行工作流
    try:
        with console.status("[bold green]正在分析中...", spinner="dots"):
            graph = create_investment_graph()
            result = graph.invoke(state)
        
        # 显示结果
        _display_results(result, verbose)
        
    except Exception as e:
        console.print(f"[bold red]分析失败：[/bold red] {str(e)}")
        raise click.ClickException(str(e))

def _display_results(state: AnalysisState, verbose: bool):
    """显示分析结果"""
    # Agent分析结果表格
    table = Table(title="Agent分析结果")
    table.add_column("Agent", style="cyan")
    table.add_column("类型", style="magenta")
    table.add_column("建议", style="bold")
    table.add_column("置信度", justify="right")
    table.add_column("理由")
    
    for analysis in state.get("agent_analyses", []):
        action_emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}[analysis.get("action", "hold")]
        table.add_row(
            f"{action_emoji} {analysis.get('agent_name')}",
            analysis.get("agent_type", ""),
            analysis.get("action", "").upper(),
            f"{analysis.get('confidence', 0):.2%}",
            analysis.get("reasoning", "")[:50] + "...",
        )
    
    console.print(table)
    
    # 最终决策
    decision = state.get("final_decision")
    if decision:
        action_emoji = {"buy": "🟢", "sell": "🔴", "hold": "🟡"}[decision.get("action", "hold")]
        decision_text = f"[bold]最终决策：{action_emoji} {decision.get('action', '').upper()}[/bold]"
        consensus_text = f"[dim]共识度：{decision.get('consensus', 0):.1%}[/dim]"
        
        console.print(Panel(
            f"{decision_text}\n{consensus_text}\n\n{decision.get('summary', '')}",
            title="💡 投资建议",
            border_style="bold blue",
        ))
```

---

## Task 9-11: 测试、文档、发布

（同Phase 1，省略详细步骤）

---

## Phase 2 完成检查清单

- [ ] 5个新Agent全部实现并通过测试
- [ ] LangGraph工作流正常工作
- [ ] 三种协作模式都能正确执行
- [ ] CLI analyze命令功能完整
- [ ] 集成测试通过
- [ ] 文档更新（添加新Agent说明）
- [ ] 创建v0.2.0-beta标签

---

## 预计工作量

- Task 1-3 (3个Agent): 各1-2天
- Task 4-6 (2个Agent + workflow): 2-3天
- Task 7-8 (协作模式 + CLI): 2-3天
- Task 9-11 (测试、文档): 1-2天

**总计：8-12天**
