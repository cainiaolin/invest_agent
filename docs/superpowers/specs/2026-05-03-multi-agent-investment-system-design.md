# 多Agent投资智能系统设计文档

**项目名称:** invest_agent_by_graph
**设计日期:** 2026-05-03
**状态:** 已批准
**版本:** 1.0

---

## 1. 项目概述

### 1.1 目标

基于 LangGraph + Tushare 开发一个面向A股市场的多Agent投资智能体系，每个Agent代表不同投资大师的思想哲学，可提供选股、个股分析和回测功能。

### 1.2 核心功能

1. **主动选股** - 根据用户需求从A股池筛选符合特定投资风格的股票
2. **个股分析** - 对指定股票给出多维度投资建议
3. **策略回测** - 验证各Agent历史表现

### 1.3 投资风格覆盖

- **价值投资派**: 巴菲特（护城河、安全边际）、格雷厄姆（深度价值）
- **成长投资派**: 费雪（成长质量）、彼得·林奇（GARP策略）
- **宏观对冲派**: 索罗斯（反身性）、达利欧（经济周期）

---

## 2. 架构设计

### 2.1 分层架构

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
│  LangGraph 编排层 (StateGraph)                               │
│  - 路由节点 → Agent节点 → 协作节点 → 输出节点                 │
│  - 三种协作模式条件边                                         │
│  - 状态管理与传递                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Agent 层 (Agent Layer)                       │
├─────────────────────────────────────────────────────────────┤
│  价值投资派              │  成长投资派    │  宏观对冲派        │
│  - BuffetAgent          │  - FisherAgent │  - SorosAgent     │
│  - GrahamAgent          │  - LynchAgent  │  - DalioAgent     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  服务层 (Service Layer)                       │
├─────────────────────────────────────────────────────────────┤
│  TushareService  │  BacktestEngine  │  CacheService         │
│  - 数据获取        │  - 策略回测      │  - 内存缓存          │
│  - 数据清洗        │  - 指标计算      │  - LRU缓存          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  数据层 (Data Layer)                          │
├─────────────────────────────────────────────────────────────┤
│  SQLite (持久化)      │  Tushare API    │  内存缓存          │
│  - 分析结果历史        │  - 实时行情      │  - functools      │
│  - 回测记录          │  - 财务数据      │  - lru_cache       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

1. **职责分离** - 每层有明确边界，通过接口通信
2. **可测试性** - Agent层可独立单元测试，服务层可mock测试
3. **可扩展性** - 新增Agent只需实现统一接口
4. **状态驱动** - LangGraph的TypedState贯穿分析流程

---

## 3. 核心数据结构

### 3.1 AnalysisState (LangGraph 状态)

```python
from typing import TypedDict, List, Optional
from typing_extensions import Annotated
import operator

class AnalysisState(TypedDict):
    """投资分析的状态定义"""

    # 输入
    stock_code: str                      # 股票代码 "600519"
    mode: str                            # 协作模式: "parallel" | "vote" | "debate"
    user_request: str                    # 用户自然语言需求

    # Agent 分析结果（累积）
    agent_analyses: Annotated[List[AgentAnalysis], operator.add]

    # 协作中间状态
    debate_round: int                    # 辩论轮次
    debate_history: List[DebateMessage]  # 辩论历史

    # 输出
    final_decision: Optional[Decision]   # 最终决策
    error: Optional[str]                 # 错误信息
```

### 3.2 AgentAnalysis

```python
class AgentAnalysis(TypedDict):
    """单个Agent的分析结果"""
    agent_name: str                      # "BuffetAgent"
    agent_type: str                      # "value" | "growth" | "macro"
    action: str                          # "buy" | "sell" | "hold"
    confidence: float                    # 0.0 - 1.0
    reasoning: str                       # 分析理由
    key_metrics: dict                    # 关键指标
    price_target: Optional[float]        # 目标价格
```

### 3.3 Decision

```python
class Decision(TypedDict):
    """最终投资决策"""
    action: str                          # 最终决策
    consensus: float                     # 共识度 0.0 - 1.0
    participating_agents: List[str]      # 参与的Agent
    summary: str                         # 决策摘要
```

---

## 4. Agent 接口设计

### 4.1 BaseAgent 抽象类

```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """所有Agent的基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent名称"""
        pass

    @property
    @abstractmethod
    def style(self) -> str:
        """投资风格描述"""
        pass

    @abstractmethod
    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        """
        核心分析方法

        流程:
        1. 从Tushare获取数据
        2. 应用投资哲学分析
        3. 返回结构化结果
        """
        pass

    @abstractmethod
    def vote(self, analyses: List[AgentAnalysis]) -> str:
        """投票模式下给出投票"""
        pass

    @abstractmethod
    async def debate(self, message: DebateMessage) -> DebateMessage:
        """辩论模式下回应其他Agent"""
        pass
```

### 4.2 Agent 实现示例

#### BuffetAgent (巴菲特式价值投资)

```python
class BuffetAgent(BaseAgent):
    """巴菲特式价值投资Agent"""

    def __init__(self, tushare_service: TushareService):
        self.tushare = tushare_service

    @property
    def name(self) -> str:
        return "BuffetAgent"

    @property
    def style(self) -> str:
        return "价值投资 - 护城河、安全边际、长期持有"

    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        # 1. 获取数据
        stock_data = await self.tushare.get_stock_fundamentals(state['stock_code'])

        # 2. 巴菲特式分析
        moat_score = self._evaluate_moat(stock_data)
        margin_of_safety = self._calculate_margin_of_safety(stock_data)
        roe_trend = self._analyze_roe_trend(stock_data)

        # 3. 决策逻辑
        if moat_score > 8 and margin_of_safety > 0.3:
            action = "buy"
            confidence = 0.85
        elif moat_score < 4 or margin_of_safety < 0:
            action = "sell"
            confidence = 0.7
        else:
            action = "hold"
            confidence = 0.6

        return AgentAnalysis(
            agent_name=self.name,
            agent_type="value",
            action=action,
            confidence=confidence,
            reasoning=f"护城河评分 {moat_score}/10，安全边际 {margin_of_safety:.1%}",
            key_metrics={
                "moat_score": moat_score,
                "margin_of_safety": margin_of_safety,
                "roe_avg": stock_data['roe_5y_avg']
            },
            price_target=stock_data['intrinsic_value'] * 0.8
        )

    def _evaluate_moat(self, data: dict) -> float:
        """护城河评估: 品牌、网络效应、成本优势、转换成本"""
        score = 0
        # 品牌溢价 (高毛利率)
        if data.get('gross_margin', 0) > 50:
            score += 3
        # 行业地位
        if data.get('market_share', 0) > 20:
            score += 3
        # ROE稳定性
        if data.get('roe_std', 100) < 5:
            score += 4
        return score
```

---

## 5. LangGraph 工作流

### 5.1 工作流图

```python
from langgraph.graph import StateGraph, END

def create_investment_graph() -> StateGraph:
    """创建投资分析工作流图"""

    workflow = StateGraph(AnalysisState)

    # 添加节点
    workflow.add_node("router", route_analysis)
    workflow.add_node("buffet_agent", buffet_agent_node)
    workflow.add_node("graham_agent", graham_agent_node)
    workflow.add_node("fisher_agent", fisher_agent_node)
    workflow.add_node("lynch_agent", lynch_agent_node)
    workflow.add_node("soros_agent", soros_agent_node)
    workflow.add_node("dalio_agent", dalio_agent_node)
    workflow.add_node("vote_collaborator", vote_collaboration_node)
    workflow.add_node("debate_collaborator", debate_collaboration_node)
    workflow.add_node("output", output_node)

    # 设置入口
    workflow.set_entry_point("router")

    # 条件边: 协作模式选择
    workflow.add_conditional_edges(
        "buffet_agent",
        check_collaboration_mode,
        {
            "parallel": "output",
            "vote": "vote_collaborator",
            "debate": "debate_collaborator"
        }
    )

    return workflow.compile()
```

### 5.2 三种协作模式

#### 模式A: 并行独立分析
- 各Agent独立分析
- 返回所有观点
- 用户自行判断

#### 模式B: 投票决策制
- 各Agent独立分析
- 统计投票结果
- 返回多数意见

#### 模式C: 辩论仲裁制
- Agent轮流发言
- 互相质疑论证
- 仲裁者综合判断

---

## 6. 回测引擎

### 6.1 BacktestEngine

```python
class BacktestEngine:
    """轻量级回测引擎"""

    def __init__(self, tushare_service: TushareService):
        self.tushare = tushare_service
        self.commission_rate = 0.0003  # 万三手续费
        self.slippage_rate = 0.001     # 千一滑点

    async def backtest(
        self,
        agent: BaseAgent,
        stock_code: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 1000000
    ) -> BacktestResult:
        """
        回测单个Agent策略

        流程:
        1. 获取历史数据
        2. 按时间顺序滚动
        3. 每个交易日调用Agent.analyze()
        4. 记录交易、计算收益
        5. 生成回测报告
        """
        pass
```

### 6.2 BacktestResult

```python
class BacktestResult(TypedDict):
    """回测结果"""
    agent_name: str
    stock_code: str
    start_date: str
    end_date: str

    # 收益指标
    total_return: float           # 总收益率
    annual_return: float          # 年化收益率
    sharpe_ratio: float           # 夏普比率
    max_drawdown: float           # 最大回撤

    # 交易统计
    total_trades: int             # 总交易次数
    win_rate: float               # 胜率
    avg_holding_days: float       # 平均持有天数

    # 基准对比
    benchmark_return: float       # 沪深300收益率
    excess_return: float          # 超额收益

    # 详细数据
    equity_curve: List[dict]      # 净值曲线
    trades: List[dict]            # 交易明细
```

---

## 7. 服务层设计

### 7.1 TushareService

```python
import tushare as ts
from functools import lru_cache

class TushareService:
    """Tushare数据服务封装"""

    def __init__(self, token: str):
        ts.set_token(token)
        self.api = ts.pro_api()

    @lru_cache(maxsize=1000)
    async def get_stock_fundamentals(self, stock_code: str) -> dict:
        """获取股票基本面数据"""
        # 基础行情
        daily = await self._get_daily(stock_code)
        # 财务指标
        indicators = await self._get_financial_indicators(stock_code)
        # 财务报表
        balance_sheet = await self._get_balance_sheet(stock_code)
        income_statement = await self._get_income_statement(stock_code)
        cash_flow = await self._get_cash_flow(stock_code)

        return {
            'stock_code': stock_code,
            'daily': daily,
            'indicators': indicators,
            'balance_sheet': balance_sheet,
            'income_statement': income_statement,
            'cash_flow': cash_flow
        }
```

### 7.2 CacheService

```python
from functools import lru_cache
import asyncio

class CacheService:
    """简单内存缓存服务"""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache = {}

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T]
    ) -> T:
        """获取缓存或计算新值"""
        pass
```

---

## 8. 用户界面

### 8.1 CLI 接口

```bash
# 分析个股
invest-agent analyze 600519 --mode parallel

# 指定Agent
invest-agent analyze 600519 --agents buffet,graham

# 回测
invest-agent backtest 600519 --agent buffet --start 2020-01-01 --end 2024-12-31

# 选股
invest-agent screen --agents buffet --top 20

# 辩论模式
invest-agent debate 600519 --agents buffet,soros --rounds 3
```

### 8.2 Web API (FastAPI)

```python
from fastapi import FastAPI

app = FastAPI(title="InvestAgent API", version="1.0.0")

@app.post("/api/v1/analyze")
async def analyze_stock(request: AnalyzeRequest) -> AnalyzeResponse:
    """分析单个股票"""
    pass

@app.post("/api/v1/screen")
async def screen_stocks(request: ScreenRequest) -> ScreenResponse:
    """选股"""
    pass

@app.post("/api/v1/backtest")
async def backtest(request: BacktestRequest) -> BacktestResponse:
    """回测"""
    pass

@app.websocket("/ws/analyze")
async def analyze_websocket(websocket: WebSocket):
    """实时分析推送"""
    pass
```

---

## 9. 项目结构

```
invest_agent_by_graph/
├── README.md
├── pyproject.toml
├── .env.example
│
├── app/
│   ├── main.py                    # FastAPI入口
│   ├── core/                      # 核心配置
│   │   ├── config.py
│   │   └── state.py
│   ├── agents/                    # Agent实现
│   │   ├── base.py
│   │   ├── value/
│   │   ├── growth/
│   │   └── macro/
│   ├── graph/                     # LangGraph工作流
│   │   ├── workflow.py
│   │   ├── nodes/
│   │   └── edges/
│   ├── services/                  # 服务层
│   │   ├── tushare_service.py
│   │   ├── cache_service.py
│   │   └── storage_service.py
│   ├── backtest/                  # 回测引擎
│   ├── api/                       # API路由
│   └── cli/                       # CLI命令
│
├── frontend/                      # Vue 3前端
├── tests/
└── docs/
```

---

## 10. 技术栈

### 后端
- **框架**: FastAPI
- **编排**: LangGraph (langchain)
- **数据**: Tushare Pro
- **缓存**: functools.lru_cache
- **存储**: SQLite (aiosqlite)
- **CLI**: Click, Rich

### 前端
- **框架**: Vue 3 + TypeScript
- **构建**: Vite
- **图表**: ECharts / Plotly
- **UI**: Element Plus / Naive UI

---

## 11. 开发计划

### Phase 1: 核心框架 (2-3周)
- [ ] 项目脚手架
- [ ] TushareService基础实现
- [ ] BaseAgent抽象类
- [ ] BuffetAgent实现
- [ ] 简单CLI框架

### Phase 2: 多Agent协作 (2-3周)
- [ ] 其他Agent实现
- [ ] LangGraph工作流
- [ ] 三种协作模式
- [ ] CLI analyze命令

### Phase 3: 回测引擎 (1-2周)
- [ ] BacktestEngine核心逻辑
- [ ] 回测指标计算
- [ ] CLI backtest命令

### Phase 4: 选股功能 (1-2周)
- [ ] 全市场扫描
- [ ] CLI screen命令

### Phase 5: Web API (2-3周)
- [ ] FastAPI框架
- [ ] REST API实现
- [ ] WebSocket实时推送

### Phase 6: 前端界面 (3-4周)
- [ ] Vue 3项目搭建
- [ ] 核心页面开发
- [ ] 图表组件集成

**总计: 11-17周 (约3-4个月)**

---

## 12. 非功能性需求

### 性能
- 单个股票分析响应时间 < 10秒
- 选股扫描支持异步并发
- 缓存命中后响应 < 1秒

### 可靠性
- Tushare API调用失败自动重试
- Agent分析异常隔离处理
- 数据持久化防止丢失

### 可维护性
- 代码覆盖率 > 80%
- 完整的类型注解
- 清晰的文档注释

### 安全性
- API Token环境变量管理
- 敏感数据不提交版本控制
- 输入验证和错误处理

---

## 13. 风险与挑战

1. **Tushare API限制** - 标准版每分钟120次调用，需要合理控制并发
2. **Agent质量** - 投资策略需要充分回测验证，避免过度拟合
3. **数据质量** - Tushare数据可能存在缺失，需要容错处理
4. **性能优化** - 全市场扫描可能耗时较长，需要缓存和增量更新

---

## 14. 成功标准

1. 完成6个Agent实现，具备不同投资风格
2. 三种协作模式正常工作
3. 回测结果与历史表现基本吻合
4. CLI和Web接口功能完整
5. 代码质量符合工程规范
6. 通过真实案例分析验证

---

**文档版本:** 1.0
**最后更新:** 2026-05-03
**设计者:** Claude
**状态:** 已批准，准备进入实施计划阶段
