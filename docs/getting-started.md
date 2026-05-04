# 快速入门指南

## 系统概述

Invest Agent By Graph 是一个基于 LangGraph 的多Agent投资分析系统，通过6个投资大师的AI Agent模拟不同投资思维模式，提供多维度投资分析。

### 核心功能

- **6个投资大师Agent**: 巴菲特、格雷厄姆、费雪、林奇、索罗斯、达里奥
- **3种协作模式**: 并行分析、投票决策、辩论仲裁
- **智能Agent选择**: 根据需求自动选择合适的投资策略
- **丰富的分析维度**: 价值、成长、宏观多维度分析

## 安装步骤

### 1. 环境准备

确保你的系统已安装以下软件：

- Python 3.11 或更高版本
- Git
- Poetry（推荐）或 pip

### 2. 获取项目代码

```bash
git clone https://github.com/yourusername/invest-agent-by-graph.git
cd invest-agent-by-graph
```

### 3. 安装依赖

**使用 Poetry（推荐）：**

```bash
# 安装Poetry（如果还没安装）
pip install poetry

# 安装项目依赖
poetry install

# 激活虚拟环境
poetry shell
```

**使用 pip：**

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的配置
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中设置：

```env
# 必须配置：Tushare Token
TUSHARE_TOKEN=你的实际Token

# 可选配置
LOG_LEVEL=INFO
CACHE_TTL=3600
```

### 5. 获取 Tushare Token

1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并登录
3. 进入"个人中心" → "接口Token"
4. 点击"生成Token"
5. 复制Token到 `.env` 文件

## 基本使用

### CLI命令

安装完成后，可以使用以下命令：

```bash
# 基本分析（默认并行模式）
invest-agent analyze 600519

# 使用投票模式
invest-agent analyze 600519 --mode vote

# 使用辩论模式
invest-agent analyze 600519 --mode debate

# 指定特定Agent
invest-agent analyze 600519 --agents buffet,graham

# 详细输出模式
invest-agent analyze 600519 -v

# 查看配置状态
invest-agent config

# 查看版本信息
invest-agent version

# 查看帮助
invest-agent --help
invest-agent analyze --help
```

### Python代码使用

```python
from app.graph.workflow import create_investment_workflow
from app.services.tushare_service import TushareService

# 初始化服务
service = TushareService()

# 创建工作流
workflow = create_investment_workflow()

# 方式1: 投票模式分析
result = workflow.invoke({
    "stock_code": "600519",
    "mode": "vote",
    "user_request": "分析贵州茅台的投资价值"
})

# 查看最终决策
print(f"最终决策: {result['final_decision']['action']}")
print(f"共识度: {result['final_decision']['consensus']:.1%}")
print(f"参与Agent: {', '.join(result['final_decision']['participating_agents'])}")

# 查看各Agent分析
print("\n各Agent分析结果:")
for analysis in result['agent_analyses']:
    print(f"{analysis['agent_name']}: {analysis['action']} "
          f"(置信度: {analysis['confidence']:.1%})")
    print(f"  理由: {analysis['reasoning'][:100]}...")

# 方式2: 辩论模式分析
result = workflow.invoke({
    "stock_code": "600519",
    "mode": "debate",
    "user_request": "深度分析贵州茅台，讨论投资价值"
})

# 查看辩论过程
print("\n辩论过程:")
for i, debate_point in enumerate(result['debate_history'], 1):
    print(f"第{i}轮: {debate_point}")

# 方式3: 单独使用Agent
from app.agents.value.buffet_agent import BuffetAgent

# 获取股票数据
stock_data = service.get_stock_data("600519")

if stock_data:
    # 创建Agent并分析
    agent = BuffetAgent()
    analysis = agent.analyze(stock_data)
    
    print(f"\n单独Agent分析:")
    print(f"决策: {analysis['decision']}")
    print(f"置信度: {analysis['confidence']:.1%}")
    print(f"理由: {analysis['reasoning']}")
    print(f"关键因素: {', '.join(analysis['key_factors'])}")
```

## 常见问题

### Q: 如何处理 Tushare API 限制？

A: Tushare有积分和调用频率限制。建议：
- 合理设置缓存时间（CACHE_TTL）
- 避免频繁调用相同数据
- 考虑升级Tushare账户等级
- 使用批量API减少调用次数

### Q: 系统支持哪些投资策略？

A: 当前版本（v0.2.0-beta）支持6个投资大师策略：

**价值投资:**
- Warren Buffett (巴菲特): 护城河、安全边际
- Benjamin Graham (格雷厄姆): 深度价值、财务安全

**成长投资:**
- Philip Fisher (费雪): 成长潜力、管理层质量
- Peter Lynch (林奇): GARP策略、十倍股

**宏观对冲:**
- George Soros (索罗斯): 反身性、市场泡沫
- Ray Dalio (达里奥): 经济周期、债务周期

### Q: 如何添加自定义Agent？

A: 继承 BaseAgent 类并实现必需方法：

```python
from app.agents.base import BaseAgent

class MyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "My Agent"

    @property
    def style(self) -> str:
        return "我的投资风格"

    def analyze(self, stock_data: dict) -> dict:
        # 实现分析逻辑
        return {
            "decision": "buy",
            "confidence": 0.8,
            "reasoning": "分析理由",
            "key_factors": ["因素1", "因素2"]
        }

    def vote(self, analysis: dict) -> str:
        return analysis["decision"]

    def debate(self, context: dict) -> str:
        return "我的观点"

# 然后在相应的工作流节点中注册这个Agent
# app/graph/nodes/agents.py
```

### Q: 三种协作模式有什么区别？

A: 

**并行模式 (parallel):**
- 所有Agent独立分析，无协作
- 快速返回各Agent的独立观点
- 适合快速参考多个投资视角

**投票模式 (vote):**
- 所有Agent投票，多数获胜
- 计算共识度，量化决策信心
- 适合需要明确投资建议的场景

**辩论模式 (debate):**
- 进行3轮结构化辩论
- Agent之间可以相互影响和说服
- 适合复杂投资决策，需要深度讨论

### Q: 数据从哪里来？

A: 系统通过Tushare API获取：
- 实时股价数据
- 财务指标数据
- 公司基本面数据

如果没有Tushare Token，系统会使用模拟数据进行演示。

## 高级使用

### 自定义Agent组合

```python
# 只使用价值投资Agent
result = workflow.invoke({
    "stock_code": "600519",
    "selected_agents": ["Warren Buffett", "Benjamin Graham"],
    "mode": "vote"
})

# 只使用成长投资Agent
result = workflow.invoke({
    "stock_code": "600519",
    "selected_agents": ["Philip Fisher", "Peter Lynch"],
    "mode": "vote"
})

# 自定义组合
result = workflow.invoke({
    "stock_code": "600519",
    "selected_agents": ["Warren Buffett", "Peter Lynch", "Ray Dalio"],
    "mode": "debate"
})
```

### 批量分析

```python
import asyncio
from app.graph.workflow import create_investment_workflow

workflow = create_investment_workflow()

stocks = ["600519", "000858", "601318"]

async def analyze_batch(stocks):
    results = []
    for stock in stocks:
        result = await workflow.ainvoke({
            "stock_code": stock,
            "mode": "parallel"
        })
        results.append(result)
    return results

# 执行批量分析
results = asyncio.run(analyze_batch(stocks))
```

## 实战案例

### 案例1: 价值股分析

```python
# 分析价值股（银行、保险、消费等）
result = workflow.invoke({
    "stock_code": "601318",  # 中国平安
    "user_request": "分析这只保险股的投资价值和安全边际",
    "mode": "vote"
})

# 系统会自动选择价值投资Agent (Buffett, Graham)
```

### 案例2: 成长股分析

```python
# 分析成长股（科技、医药、新能源等）
result = workflow.invoke({
    "stock_code": "300750",  # 宁德时代
    "user_request": "分析新能源公司的成长潜力和技术创新",
    "mode": "debate"
})

# 系统会自动选择成长投资Agent (Fisher, Lynch)
```

### 案例3: 宏观影响分析

```python
# 分析受宏观影响较大的股票
result = workflow.invoke({
    "stock_code": "600519",  # 贵州茅台
    "user_request": "分析宏观政策对消费股的影响",
    "mode": "vote"
})

# 系统会自动选择宏观对冲Agent (Soros, Dalio)
```

## 技术支持

- GitHub Issues: [https://github.com/yourusername/invest-agent-by-graph/issues](https://github.com/yourusername/invest-agent-by-graph/issues)
- 文档: [https://github.com/yourusername/invest-agent-by_graph/wiki](https://github.com/yourusername/invest-agent-by_graph/wiki)

---

⚠️ **重要提示**: 本项目仅供学习研究使用，不构成投资建议。