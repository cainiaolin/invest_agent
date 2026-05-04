# 系统架构文档

## 总体架构

Invest Agent By Graph 采用模块化、可扩展的架构设计，基于 Python 和 LangGraph 构建。

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                        │
│                     (Click + Rich)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│              LangGraph Workflow Layer (v0.2.0)             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │   Router    │    Agents   │Collaboration│   Output    │ │
│  │    Node     │    Nodes    │    Nodes    │    Node     │ │
│  └──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┘ │
└─────────┼─────────────┼─────────────┼─────────────┼────────┘
          │             │             │             │
          └─────────────┴─────────────┴─────────────┘
                        │
┌───────────────────────┴───────────────────────────────────┐
│                    Agent Layer (6 Agents)                 │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │ Buffett  │ Graham   │ Fisher   │ Lynch    │ Soros    │ │
│  │  Agent   │  Agent   │  Agent   │  Agent   │  Agent   │ │
│  └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘ │
│       │          │          │          │          │       │
│       │  Value   │  Growth  │  Macro   │          │       │
│       └──────────┴──────────┴──────────┘          │       │
│                        │                            │       │
│              ┌─────────┴─────────┐                 │       │
│              │   BaseAgent Interface│               │       │
│              │  - analyze()       │               │       │
│              │  - vote()          │               │       │
│              │  - debate()        │               │       │
│              └─────────┬─────────┘                 │       │
│                        │                          │       │
└────────────────────────┼──────────────────────────┼───────┘
                         │                          │
          ┌──────────────┴──────────┐      ┌────────┴────────┐
          │   Core State Management │      │ Dalio Agent     │
          │  - AnalysisState        │      │ (Macro)         │
          │  - AgentAnalysis        │      └─────────────────┘
          │  - Decision             │
          └──────────────┬──────────┘
                         │
          ┌──────────────┴──────────┐
          │    Data Services Layer  │
          │  - TushareService       │
          │  - CacheManager         │
          └──────────────┬──────────┘
                         │
          ┌──────────────┴──────────┐
          │   External Data Sources │
          │  - Tushare API          │
          │  - Future: More Sources │
          └─────────────────────────┘
```

## 核心组件

### 1. LangGraph工作流层 (v0.2.0新增)

#### 工作流结构
```python
class InvestmentWorkflow:
    """基于LangGraph的投资分析工作流"""
    
    # 工作流节点
    - router_node: 智能路由和Agent选择
    - parallel_agents_node: 并行执行所有Agent
    - value_agent_node: 执行价值投资Agent
    - growth_agent_node: 执行成长投资Agent
    - macro_agent_node: 执行宏观对冲Agent
    - vote_collaboration_node: 投票协作
    - debate_collaboration_node: 辩论协作
    - output_node: 结果输出和格式化
    
    # 条件路由
    - route_to_agents: 根据用户需求选择Agent类型
    - route_after_agents: 根据模式选择协作方式
```

#### 三种协作模式

**1. 并行模式 (Parallel)**
```
用户输入 → 路由 → 并行Agent分析 → 输出
```
- 特点: 无协作，快速返回各Agent独立观点
- 适用: 快速参考多个投资视角

**2. 投票模式 (Vote)**
```
用户输入 → 路由 → Agent分析 → 投票决策 → 输出
```
- 特点: 多数投票，量化共识度
- 适用: 需要明确决策建议的场景

**3. 辩论模式 (Debate)**
```
用户输入 → 路由 → Agent分析 → 3轮辩论 → 决策 → 输出
```
- 特点: 深度讨论，观点交互
- 适用: 复杂投资决策，需要充分讨论

#### 状态管理
```python
class AnalysisState(TypedDict):
    """工作流状态定义"""
    # 输入
    stock_code: str                  # 股票代码
    user_request: str                # 用户需求
    mode: str                        # 协作模式
    
    # 中间状态
    selected_agent_type: str         # 选择的Agent类型
    stock_data: dict                 # 股票数据
    agent_analyses: list[AgentAnalysis]  # Agent分析结果
    debate_round: int                # 辩论轮次
    debate_history: list[str]        # 辩论历史
    
    # 输出
    final_decision: dict             # 最终决策
    error: str | None                # 错误信息
```

### 2. Agent框架

#### BaseAgent 抽象基类
所有Agent的基类，定义统一接口：

```python
class BaseAgent(ABC):
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
    def analyze(self, stock_data: dict) -> dict:
        """分析股票数据"""
        pass

    @abstractmethod
    def vote(self, analysis: dict) -> str:
        """投票决策"""
        pass

    @abstractmethod
    def debate(self, context: dict) -> str:
        """参与辩论"""
        pass
```

#### 6个具体Agent实现

**价值投资Agent**
- **BuffetAgent** (巴菲特): 护城河、安全边际、长期持有
- **GrahamAgent** (格雷厄姆): 价值投资之父、深度价值、安全边际

**成长投资Agent**
- **FisherAgent** (费雪): 成长股投资、管理层质量、长期持有
- **LynchAgent** (林奇): GARP策略、十倍股、投资你所了解的

**宏观对冲Agent**
- **SorosAgent** (索罗斯): 反身性理论、市场泡沫、宏观趋势
- **DalioAgent** (达里奥): 经济周期、全天候策略、债务周期

### 3. 数据层

#### TushareService
负责与Tushare API交互：

```python
class TushareService:
    def get_stock_data(self, symbol: str) -> dict:
        """获取股票数据"""

    def get_financial_metrics(self, symbol: str) -> dict:
        """获取财务指标"""

    def get_market_data(self, symbol: str) -> dict:
        """获取市场数据"""
```

#### 数据结构

**AnalysisState** (工作流状态)
```python
class AnalysisState(TypedDict):
    # 输入
    stock_code: str
    user_request: str
    mode: str
    selected_agents: list[str]
    
    # 中间状态
    selected_agent_type: str
    stock_data: dict
    agent_analyses: list[AgentAnalysis]
    debate_round: int
    debate_history: list[str]
    
    # 输出
    final_decision: dict
    error: str | None
```

**AgentAnalysis** (Agent分析结果)
```python
class AgentAnalysis(TypedDict):
    agent_name: str
    agent_type: str
    action: str              # buy/sell/hold
    confidence: float
    reasoning: str
    key_metrics: dict
    price_target: float | None
```

**Decision** (最终决策)
```python
class Decision(TypedDict):
    action: str              # buy/sell/hold
    consensus: float         # 共识度 0-1
    participating_agents: list[str]
    summary: str
```

### 3. 配置管理

基于 Pydantic Settings：

```python
class Settings(BaseSettings):
    tushare_token: str
    log_level: str = "INFO"
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"
```

### 4. CLI界面

基于 Click 和 Rich：

- **analyze**: 股票分析命令
- **config**: 配置管理命令
- **version**: 版本信息命令

## 数据流

### 分析流程

#### 工作流执行流程
```
1. 用户输入股票代码和需求
   ↓
2. CLI解析命令和参数
   ↓
3. 工作流开始 (router_node)
   ├─ 解析用户需求
   └─ 选择Agent类型 (value/growth/macro/parallel)
   ↓
4. Agent执行 (agents_node)
   ├─ 并行模式: 执行所有6个Agent
   ├─ 价值模式: 执行Buffett, Graham
   ├─ 成长模式: 执行Fisher, Lynch
   └─ 宏观模式: 执行Soros, Dalio
   ↓
5. 条件路由 (route_after_agents)
   ├─ parallel → 直接输出
   ├─ vote → 投票协作
   └─ debate → 辩论协作
   ↓
6. 协作过程 (可选)
   ├─ 投票: 统计buy/sell/hold，计算共识度
   └─ 辩论: 3轮结构化辩论
   ↓
7. 输出格式化 (output_node)
   └─ 生成投资分析报告
   ↓
8. CLI展示结果
```

### 数据结构转换

```
Tushare API Response
   ↓
Raw Data (dict)
   ├─ basic info (symbol, name, price)
   ├─ financial metrics (pe, pb, roe, etc.)
   └─ qualitative data (moat, growth, management)
   ↓
StockData (dict) - 标准化格式
   ├─ symbol, name, price
   ├─ metrics (财务指标)
   ├─ moat_indicators (护城河指标)
   ├─ growth_indicators (成长指标)
   └─ management_quality (管理质量)
   ↓
Agent Analysis Results (list)
   ├─ agent_name, agent_type
   ├─ action (buy/sell/hold)
   ├─ confidence (0-1)
   ├─ reasoning (决策理由)
   └─ key_metrics (关键指标)
   ↓
Collaboration Result
   ├─ voting (投票统计)
   ├─ consensus (共识度)
   └─ debate_history (辩论记录)
   ↓
Final Decision (dict)
   ├─ action, consensus
   ├─ participating_agents
   └─ summary
   ↓
Formatted Output (Rich Console)
   ├─ 投资分析报告
   ├─ 各Agent观点摘要
   ├─ 协作过程详情
   └─ 最终决策建议
```

## 扩展性设计

### 添加新Agent

1. 继承 BaseAgent
2. 实现4个抽象方法
3. 创建Agent文件在相应类别目录
4. 更新工作流节点以包含新Agent
5. 添加单元测试和集成测试
6. 更新文档

### 添加数据源

1. 实现数据服务接口
2. 统一数据格式
3. 集成到服务层
4. 更新配置

### 添加协作模式

1. 在 `app/graph/nodes/collaboration.py` 中定义新的协作节点
2. 在 `app/graph/edges/conditions.py` 中添加路由条件
3. 在 `app/graph/workflow.py` 中集成到工作流图
4. 在 CLI 中添加新模式选项
5. 编写测试验证新协作模式

## 技术栈

### 核心框架
- **Python 3.11+**: 主要编程语言
- **LangGraph (^0.2.0)**: Agent工作流引擎
- **LangChain (^0.3.0)**: LLM集成框架
- **Pydantic (^2.6.0)**: 数据验证和设置管理

### 数据处理
- **Tushare**: 金融数据源
- **Python字典**: 主要数据结构

### CLI开发
- **Click**: 命令行框架
- **Rich**: 终端美化

### 测试
- **pytest**: 测试框架
- **pytest-mock**: Mock支持
- **pytest-cov**: 覆盖率统计

### 代码质量
- **Black**: 代码格式化
- **Ruff**: 代码检查
- **MyPy**: 类型检查

## 设计原则

### 1. SOLID原则
- **S**: 单一职责，每个类只负责一项功能
- **O**: 开闭原则，对扩展开放，对修改封闭
- **L**: 里氏替换，子类可以替换父类
- **I**: 接口隔离，接口小而专一
- **D**: 依赖倒置，依赖抽象而非具体

### 2. DRY原则
- 避免代码重复
- 提取公共逻辑
- 使用组合和继承

### 3. KISS原则
- 保持简单直接
- 优先选择直观方案
- 避免过度设计

### 4. 测试驱动
- 先写测试，再写代码
- 保持高测试覆盖率
- 集成测试验证流程

## 性能考虑

### 缓存策略
- Tushare数据缓存（可配置TTL）
- 避免频繁API调用
- 内存缓存常用数据

### 异步处理
- 数据获取异步化（Phase 2）
- 并行Agent分析（Phase 2）
- 非阻塞I/O操作

### 资源管理
- 连接池管理
- 内存使用优化
- 错误重试机制

## 安全性

### API密钥管理
- 环境变量存储
- 不提交到版本控制
- .env.example提供模板

### 数据验证
- Pydantic模型验证
- 输入数据清理
- 异常处理机制

## 未来规划

### Phase 2: LangGraph集成 ✅已完成
- ✅ 工作流编排 (StateGraph)
- ✅ 多Agent协作 (并行/投票/辩论)
- ✅ 状态管理优化 (TypedDict)
- ✅ 智能路由和Agent选择
- ✅ 完整测试覆盖

### Phase 3: 扩展Agent ✅已完成
- ✅ 6个投资大师Agent
- ✅ 3类投资策略 (价值/成长/宏观)
- ✅ 统一Agent接口
- ✅ 丰富的分析维度

### Phase 4: 生产化 (规划中)
- Web界面开发
- 数据持久化
- 性能优化
- 监控告警
- 策略回测系统

---

最后更新: 2025-05-03 (v0.2.0-beta)