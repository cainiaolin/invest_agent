# Phase 3: 高级功能 - 回测、选股、Web API

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 实现策略回测引擎、智能选股功能、Web API和前端界面，完成完整的多Agent投资智能体系

**架构:** 扩展Phase 2，添加回测层、选股层和Web层

**技术栈:** Python 3.11+, FastAPI, Vue 3, TypeScript, asyncio, SQLAlchemy

---

## Phase 2 成果回顾

Phase 2 已完成：
- ✅ 6个投资大师Agent（Buffett, Graham, Fisher, Lynch, Soros, Dalio）
- ✅ LangGraph工作流编排
- ✅ 三种协作模式（并行/投票/辩论）
- ✅ 完整CLI命令系统
- ✅ 文档和测试

---

## 文件结构扩展

```
invest_agent_by_graph/
├── app/
│   ├── backtest/                    # 🆕 回测引擎
│   │   ├── __init__.py
│   │   ├── engine.py               # 回测引擎核心
│   │   ├── portfolio.py            # 投资组合管理
│   │   ├── metrics.py              # 回测指标计算
│   │   └── report.py               # 报告生成
│   │
│   ├── screening/                  # 🆕 选股模块
│   │   ├── __init__.py
│   │   ├── scanner.py              # 市场扫描器
│   │   ├── filters.py              # 选股过滤器
│   │   └── ranking.py              # 结果排序
│   │
│   ├── api/                        # 🆕 Web API
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI应用
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py          # 分析API
│   │   │   ├── screen.py           # 选股API
│   │   │   ├── backtest.py         # 回测API
│   │   │   └── websocket.py        # 实时推送
│   │   └── schemas/                # Pydantic模型
│   │       ├── __init__.py
│   │       ├── analyze.py
│   │       ├── screen.py
│   │       └── backtest.py
│   │
│   └── ... (Phase 1-2文件)
│
├── frontend/                       # 🆕 Vue 3前端
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── StockAnalysis.vue   # 股票分析组件
│   │   │   ├── AgentCard.vue       # Agent卡片
│   │   │   ├── BacktestChart.vue    # 回测图表
│   │   │   ├── ScreeningResult.vue # 选股结果
│   │   │   └── DebateView.vue      # 辩论视图
│   │   ├── views/
│   │   │   ├── Home.vue
│   │   │   ├── Analyze.vue
│   │   │   ├── Screen.vue
│   │   │   └── Backtest.vue
│   │   ├── api/
│   │   │   └── client.ts           # API客户端
│   │   ├── stores/
│   │   │   └── analysis.ts         # 状态管理
│   │   └── assets/
│   └── tests/                      # 前端测试
│
├── tests/
│   ├── unit/
│   │   └── backtest/               # 🆕 回测单元测试
│   ├── integration/
│   │   └── api/                    # 🆕 API集成测试
│   └── e2e/                         # 🆕 端到端测试
│
├── pyproject.toml                   # 🔄 更新依赖
├── README.md                        # 🔄 更新文档
└── docker/
    ├── Dockerfile                   # 🆕 后端Docker
    └── docker-compose.yml           # 🆕 完整部署配置
```

---

## Task 1: 更新依赖和配置

**Files:**
- Update: `pyproject.toml`
- Create: `docker/Dockerfile`
- Create: `docker/docker-compose.yml`

**新增依赖:**
```toml
[tool.poetry.dependencies]
# ... Phase 1-2依赖
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
websockets = "^12.0"
sqlalchemy = "^2.0.0"
aiosqlite = "^0.19.0"
pandas = "^2.1.0"
numpy = "^1.26.0"
```

---

## Task 2: 回测引擎核心

**Files:**
- Create: `app/backtest/engine.py`
- Create: `app/backtest/portfolio.py`
- Create: `app/backtest/metrics.py`
- Create: `app/backtest/report.py`
- Create: `tests/unit/backtest/test_engine.py`

**核心功能:**

```python
class BacktestEngine:
    """轻量级回测引擎"""
    
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
        1. 获取历史数据（日线、财务数据）
        2. 按时间顺序滚动
        3. 每个交易日调用Agent.analyze()
        4. 记录交易、计算收益
        5. 生成回测报告
        """
```

**回测指标:**
- 总收益率、年化收益率
- 夏普比率、最大回撤
- 胜率、平均持有天数
- 与沪深300对比

---

## Task 3: 投资组合管理

**核心功能:**

```python
class Portfolio:
    """投资组合管理"""
    
    def __init__(self, initial_capital: float):
        self.cash = initial_capital
        self.holdings = {}  # {stock_code: quantity}
        self.initial_capital = initial_capital
    
    @property
    def total_value(self) -> float:
        """计算总资产（现金 + 持仓市值）"""
        
    @property
    def return_rate(self) -> float:
        """计算收益率"""
        
    def execute_trade(
        self, 
        action: str, 
        stock_code: str, 
        price: float, 
        quantity: int
    ) -> Trade:
        """执行交易（买入/卖出）"""
        
    def update_holdings_value(self, current_prices: dict):
        """更新持仓市值"""
```

---

## Task 4: 智能选股功能

**Files:**
- Create: `app/screening/scanner.py`
- Create: `app/screening/filters.py`
- Create: `app/screening/ranking.py`
- Create: `tests/unit/screening/test_scanner.py`

**核心功能:**

```python
class MarketScanner:
    """市场扫描器"""
    
    async def scan_market(
        self,
        agent: BaseAgent,
        universe: str = "all",  # all | industry:白酒 | index:沪深300
        top_n: int = 20
    ) -> List[StockScore]:
        """
        扫描市场寻找投资机会
        
        流程:
        1. 获取股票池（全部或特定行业）
        2. 并行调用Agent分析
        3. 收集分析结果
        4. 按评分排序
        5. 返回Top N
        """
```

**CLI命令:**
```bash
invest-agent screen --agents buffet --top 20
invest-agent screen --industry 白酒 --agents fisher,lynch --top 10
```

---

## Task 5: Web API - FastAPI

**Files:**
- Create: `app/api/main.py`
- Create: `app/api/routes/analyze.py`
- Create: `app/api/routes/screen.py`
- Create: `app/api/routes/backtest.py`
- Create: `app/api/routes/websocket.py`
- Create: `app/api/schemas/`
- Create: `tests/integration/api/`

**核心API端点:**

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="InvestAgent API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/analyze")
async def analyze_stock(request: AnalyzeRequest) -> AnalyzeResponse:
    """分析单个股票"""
    pass

@app.post("/api/v1/screen")
async def screen_stocks(request: ScreenRequest) -> ScreenResponse:
    """智能选股"""
    pass

@app.post("/api/v1/backtest")
async def backtest_strategy(request: BacktestRequest) -> BacktestResponse:
    """策略回测"""
    pass

@app.websocket("/ws/analyze")
async def analyze_websocket(websocket: WebSocket):
    """实时分析推送（辩论模式）"""
    pass
```

---

## Task 6: Vue 3 前端

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/components/`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/stores/analysis.ts`

**核心组件:**

```vue
<!-- StockAnalysis.vue -->
<template>
  <div class="stock-analysis">
    <el-input v-model="stockCode" placeholder="股票代码" />
    <el-select v-model="mode">
      <el-option label="并行模式" value="parallel" />
      <el-option label="投票模式" value="vote" />
      <el-option label="辩论模式" value="debate" />
    </el-select>
    <el-button @click="analyze">分析</el-button>
    
    <!-- Agent卡片 -->
    <AgentCard 
      v-for="agent in agents" 
      :analysis="agent.analysis" 
    />
    
    <!-- 最终决策 -->
    <DecisionPanel :decision="decision" />
  </div>
</template>

<!-- BacktestChart.vue -->
<template>
  <div class="backtest-chart">
    <div ref="chartRef" style="width: 100%; height: 400px"></div>
    
    <el-table :data="trades">
      <el-table-column prop="date" label="日期" />
      <el-table-column prop="action" label="操作" />
      <el-table-column prop="price" label="价格" />
      <el-table-column prop="quantity" label="数量" />
    </el-table>
  </div>
</template>
```

**技术栈:**
- Vue 3 + TypeScript
- Vite (构建工具)
- Element Plus (UI组件库)
- ECharts (图表)
- Pinia (状态管理)
- Axios (HTTP客户端)

---

## Task 7: Docker部署

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/docker-compose.yml`

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
    volumes:
      - ./data:/app/data
    depends_on:
      - db
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=investagent
      - POSTGRES_USER=investagent
      - POSTGRES_PASSWORD=investagent
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## Task 8-10: 测试、文档、发布

（同Phase 1-2，省略详细步骤）

---

## Phase 3 完成检查清单

- [ ] 回测引擎实现并通过测试
- [ ] 选股功能实现并通过测试
- [ ] FastAPI后端实现并通过测试
- [ ] Vue 3前端实现并通过测试
- [ ] Docker部署配置完成
- [ ] 完整的端到端测试通过
- [ ] 文档更新完整
- [ ] 创建v0.3.0标签

---

## 预计工作量

- Task 1-2 (回测引擎): 3-4天
- Task 3-4 (选股功能): 2-3天
- Task 5 (Web API): 3-4天
- Task 6 (前端界面): 5-7天
- Task 7 (Docker): 1天
- Task 8-10 (测试文档): 2-3天

**总计：16-22天（约3-4周）**
