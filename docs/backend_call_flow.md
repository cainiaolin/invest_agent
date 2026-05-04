# 后端调用链路详解

## 完整调用流程

### 1️⃣ FastAPI应用入口 (app/api/main.py)

```python
# 创建FastAPI应用实例
app = FastAPI(title="InvestAgent API")

# 注册路由，添加前缀 /api/v1
app.include_router(analyze.router, prefix="/api/v1")
```

**URL映射：**
- `POST /api/v1/analyze/` → analyze_stock 函数
- `POST /api/v1/screen/` → screen_stocks 函数
- `POST /api/v1/backtest/` → run_backtest 函数

---

### 2️⃣ 路由层 (app/api/routes/analyze.py)

#### Agent映射表
```python
AGENT_MAP = {
    "buffet": BuffetAgent,      # 巴菲特
    "graham": GrahamAgent,      # 格雷厄姆
    "fisher": FisherAgent,      # 费雪
    "lynch": LynchAgent,        # 林奇
    "soros": SorosAgent,        # 索罗斯
    "dalio": DalioAgent,        # 达利欧
}
```

#### 请求处理流程
```python
@router.post("/", response_model=AnalyzeResponse)
async def analyze_stock(request: AnalyzeRequest):
    """
    步骤：
    1. 解析用户选择的Agent列表
    2. 创建TushareService实例（用于获取股票数据）
    3. 实例化每个Agent
    4. 为每个Agent创建分析状态
    5. 调用Agent.analyze(state)
    6. 聚合所有分析结果
    7. 返回响应
    """

    # 步骤1: 解析Agent参数
    agent_names = _parse_agents(request.agents)
    # 例如: "buffet,graham" → ["buffet", "graham"]

    # 步骤2: 创建数据服务
    tushare_service = TushareService(settings.tushare_token)

    # 步骤3: 实例化Agent
    agents = []
    for name in agent_names:
        agent_class = AGENT_MAP.get(name)  # 例如: BuffetAgent
        if agent_class:
            agents.append(agent_class(tushare_service))
    # 结果: [BuffetAgent实例, GrahamAgent实例, ...]

    # 步骤4: 创建分析状态
    state = AnalysisState(
        stock_code=request.stock_code,  # "600519"
        mode=request.mode,               # "parallel"
        user_request="分析此股票的投资价值",
        agent_analyses=[],
        debate_round=0,
        debate_history=[],
        final_decision=None,
        error=None
    )

    # 步骤5: 调用每个Agent的analyze方法
    agent_analyses_models = []
    for agent in agents:
        # 关键调用！
        analysis_result = await agent.analyze(state)

        # 构造响应模型
        agent_analysis = AgentAnalysisModel(
            agent_name=agent.name,          # "Warren Buffett"
            agent_type=_get_agent_type(...), # "value"
            action=analysis_result["action"], # "buy"
            confidence=analysis_result["confidence"], # 0.85
            reasoning=analysis_result["reasoning"],
            key_metrics=analysis_result["key_metrics"]
        )
        agent_analyses_models.append(agent_analysis)

    # 步骤6: 聚合决策（根据mode）
    final_decision = make_final_decision(agent_analyses_models, request.mode)

    # 步骤7: 返回响应
    return AnalyzeResponse(
        stock_code=request.stock_code,
        mode=request.mode,
        agent_analyses=agent_analyses_models,
        final_decision=final_decision
    )
```

---

### 3️⃣ Agent基类 (app/agents/base.py)

```python
class BaseAgent(ABC):
    """所有Agent的抽象基类"""

    def __init__(self, tushare_service):
        """初始化时注入数据服务"""
        self.tushare = tushare_service

    @property
    @abstractmethod
    def name(self) -> str:
        """子类必须实现：返回Agent名称"""
        pass

    @property
    @abstractmethod
    def style(self) -> str:
        """子类必须实现：返回投资风格描述"""
        pass

    @abstractmethod
    async def analyze(self, state: AnalysisState) -> dict:
        """
        子类必须实现：核心分析方法

        Args:
            state: 包含stock_code, mode等信息的字典

        Returns:
            {
                "action": "buy/sell/hold",
                "confidence": 0.85,
                "reasoning": "投资理由...",
                "key_metrics": {...}
            }
        """
        pass
```

---

### 4️⃣ 具体Agent实现 (app/agents/value/buffet_agent.py)

```python
class BuffetAgent(BaseAgent):
    """巴菲特风格价值投资Agent"""

    @property
    def name(self) -> str:
        return "Warren Buffett"

    @property
    def style(self) -> str:
        return "价值投资：关注企业护城河、安全边际和长期成长性"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        巴菲特风格的分析逻辑
        """
        # 1. 提取股票代码
        stock_code = state.get("stock_code", "")

        # 2. 获取股票数据
        stock_data = await self._get_stock_data(stock_code)

        # 3. 调用内部分析方法
        result = self._analyze_stock_data(stock_data)

        # 4. 添加agent_name并返回
        result["agent_name"] = self.name
        return result

    async def _get_stock_data(self, stock_code: str) -> dict:
        """获取股票数据（可从tushare或模拟）"""
        return {
            "symbol": stock_code,
            "name": "贵州茅台",
            "metrics": {
                "pe_ratio": 35.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                ...
            },
            "moat_indicators": {
                "brand_strength": 9,
                "market_share": 60.0,
                ...
            }
        }

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """巴菲特投资理念的具体实现"""
        metrics = stock_data["metrics"]

        # 评估维度1: 护城河强度
        moat_score = self._evaluate_moat(
            metrics["brand_strength"],
            metrics["market_share"]
        )

        # 评估维度2: 财务健康
        health_score = self._evaluate_financial_health(
            metrics["roe"],
            metrics["debt_ratio"]
        )

        # 评估维度3: 估值安全边际
        valuation_score = self._evaluate_valuation(
            metrics["pe_ratio"],
            metrics["pb_ratio"]
        )

        # 评估维度4: 盈利质量
        quality_score = self._evaluate_quality(...)

        # 计算总分
        scores = {
            "moat": moat_score,
            "financial_health": health_score,
            "valuation": valuation_score,
            "quality": quality_score
        }
        total_score = sum(scores.values()) / len(scores)

        # 计算置信度
        confidence = min(total_score / 100, 1.0)

        # 做出决策
        action = self._make_decision(total_score, scores)

        # 生成理由
        reasoning = self._generate_reasoning(action, scores, stock_data)

        # 提取关键因素
        key_factors = self._extract_key_factors(scores, stock_data)

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_metrics": {"scores": scores},
            "total_score": total_score
        }
```

---

## 📝 时序图

```
前端                    FastAPI               Agent              Tushare/数据
 │                       │                    │                    │
 ├── POST /api/v1/analyze ─>│                    │                    │
 │   {stock_code:"600519"}  │                    │                    │
 │                       │                    │                    │
 │                       ├── 创建TushareService ─>│                    │
 │                       │                    │                    │
 │                       ├── 实例化BuffetAgent ─>│                    │
 │                       ├── 实例化GrahamAgent ─>│                    │
 │                       │                    │                    │
 │                       ├── await agent.analyze(state) ─>│            │
 │                       │                    ├── 获取股票数据 ─>     │
 │                       │                    │    <──────── 返回数据 │
 │                       │                    │                    │
 │                       │                    ├── 评估护城河      │
 │                       │                    ├── 评估财务健康    │
 │                       │                    ├── 评估估值        │
 │                       │                    ├── 计算总分        │
 │                       │                    ├── 做出决策        │
 │                       │                    ├── 生成理由        │
 │                       │                    │                    │
 │                       │ <─── 返回分析结果 ───│                    │
 │                       │                    │                    │
 │ <─── 返回JSON响应 ─────│                    │                    │
 │   {                   │                    │                    │
 │     "agent_analyses":[...]                   │                    │
 │   }                                      │                    │
```

---

## 🔧 关键设计模式

### 1. 依赖注入
```python
# Agent不直接创建TushareService，而是通过构造函数注入
agent = BuffetAgent(tushare_service)  # ✅
```

### 2. 策略模式
```python
# 每个Agent实现相同的接口，但有不同的分析策略
for agent in [BuffetAgent, GrahamAgent, FisherAgent]:
    result = await agent.analyze(state)  # 统一调用方式
```

### 3. 工厂模式
```python
# 通过映射表创建Agent实例
AGENT_MAP = {
    "buffet": BuffetAgent,
    "graham": GrahamAgent,
    ...
}
agent_class = AGENT_MAP["buffet"]  # 获取类
agent = agent_class(tushare)        # 创建实例
```

---

## 💡 总结

**核心流程：**
1. 前端发送POST请求到 `/api/v1/analyze/`
2. 路由解析参数，从AGENT_MAP获取Agent类
3. 实例化Agent（注入TushareService）
4. 调用每个Agent的`analyze(state)`方法
5. Agent内部获取数据、计算评分、返回决策
6. 路由聚合所有结果，返回JSON响应

**关键点：**
- 所有Agent继承自`BaseAgent`
- 统一的异步接口：`async def analyze(state) -> dict`
- Agent独立运作，互不干扰
- 通过AnalysisState传递上下文信息
