# Invest Agent By Graph

基于 LangGraph + Tushare 的多Agent投资智能体系

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0--alpha-orange.svg)](https://github.com/yourusername/invest-agent-by-graph)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 项目概述

Invest Agent By Graph 是一个智能投资分析系统，通过多个AI Agent模拟不同投资大师的思维模式，为股票投资提供多维度分析和决策支持。

### 当前状态 (v0.3.0-alpha)

✅ **Phase 1 核心框架已完成**
- 核心配置管理系统
- 数据结构定义（AnalysisState、AgentVote）
- Tushare数据服务集成
- BaseAgent抽象基类
- CLI命令行界面
- 完整的单元测试和集成测试

✅ **Phase 2 多Agent协作系统已完成**
- LangGraph工作流集成
- 6个投资大师Agent（Buffett、Graham、Fisher、Lynch、Soros、Dalio）
- 3种协作模式（并行、投票、辩论）
- 智能Agent选择和路由
- 完整的测试验证

✅ **Phase 3 高级特性已完成**
- Web API完整实现（FastAPI）
- Vue 3前端界面
- 策略回测引擎
- 智能选股扫描器
- Docker容器化部署

## ✨ 核心特性

### 投资大师Agent

**价值投资派:**
- **沃伦·巴菲特**: 护城河分析、安全边际、ROE质量
- **本杰明·格雷厄姆**: 深度价值、内在价值计算、Net-Net分析

**成长投资派:**
- **菲利普·费雪**: 成长质量评估、管理层调研、研发投入分析
- **彼得·林奇**: GARP策略、PEG比率、13只股票特征

**宏观对冲派:**
- **乔治·索罗斯**: 反身性理论、繁荣-崩溃周期、趋势拐点
- **雷·达利欧**: 经济周期分析、全天候策略、债务周期模型

### 搜索增强Agent 🆕

- **智能搜索**: 实时获取官方公告、市场新闻、行业动态
- **可信度评估**: 多维度评估信息质量，确保数据可靠性
- **深度融合**: 历史数据与实时信息智能整合
- **个性化策略**: 每个Agent有独特的搜索偏好和策略

详见 [搜索增强Agent使用指南](docs/SEARCH_ENHANCED_AGENT_GUIDE.md)

## 🤖 AI增强模式

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

### 核心功能

**个股分析:**
- 多Agent并行分析
- 投票决策制
- 辩论仲裁制
- 详细分析报告

**智能选股:**
- 全市场扫描
- 行业/指数筛选
- 多维度评分
- 推荐级别排序

**策略回测:**
- 历史数据回测
- 完整绩效指标
- 交易明细记录
- 基准对比分析

## 📦 安装

### 环境要求

- Python 3.11+
- Poetry (推荐) 或 pip
- Node.js 18+ (前端)

### 快速安装

```bash
# 克隆项目
git clone https://github.com/yourusername/invest-agent-by-graph.git
cd invest-agent-by-graph

# 使用Poetry安装（推荐）
poetry install

# 或使用pip
pip install -r requirements.txt

# 配置Tushare Token
export TUSHARE_TOKEN="your_token_here"
```

### 获取 Tushare Token

1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号
3. 在个人中心获取API Token
4. 将Token添加到环境变量或`.env`文件

## 🚀 快速开始

### CLI使用

```bash
# 分析股票
invest-agent analyze 600519 --agent buffet --mode vote

# 智能选股
invest-agent screen all --agents buffet,graham,fisher --top 20

# 策略回测
invest-agent backtest 600519 --agent buffet --start-date 2020-01-01 --end-date 2024-12-31
```

### Web API使用

```bash
# 启动API服务器
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# 访问API文档
# http://localhost:8000/docs
```

### 前端使用

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 访问
# API: http://localhost:8000
# 前端: http://localhost:80
```

## 📖 项目结构

```
invest-agent-by-graph/
├── app/
│   ├── agents/              # Agent实现
│   │   ├── base.py         # 抽象基类
│   │   ├── value/          # 价值投资Agent
│   │   ├── growth/         # 成长投资Agent
│   │   └── macro/          # 宏观对冲Agent
│   ├── api/                # Web API
│   │   └── routes/         # API路由
│   ├── backtest/           # 回测引擎
│   │   ├── engine.py       # 核心引擎
│   │   ├── portfolio.py    # 组合管理
│   │   └── metrics.py      # 绩效指标
│   ├── cli/                # CLI界面
│   │   └── commands/       # 命令实现
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理
│   │   └── state.py        # 数据结构
│   ├── graph/              # LangGraph工作流
│   │   ├── workflow.py     # 主工作流
│   │   ├── nodes/          # 工作流节点
│   │   └── edges/          # 条件边
│   ├── screening/          # 选股扫描器
│   │   └── scanner.py      # 市场扫描
│   └── services/           # 数据服务
│       └── tushare_service.py
├── frontend/               # Vue 3前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── api/            # API服务
│   └── package.json
├── docker/                 # Docker配置
├── docs/                   # 文档
├── tests/                  # 测试套件
├── pyproject.toml          # 项目配置
└── README.md
```

## 🔧 API端点

### 分析API

```bash
# 分析股票
POST /api/v1/analyze
{
  "stock_code": "600519",
  "mode": "vote",
  "agents": "buffet,graham,fisher"
}

# 获取Agent列表
GET /api/v1/analyze/agents
```

### 选股API

```bash
# 智能选股
POST /api/v1/screen
{
  "universe": "all",
  "agents": "buffet,graham",
  "top_n": 20
}

# 获取行业列表
GET /api/v1/screen/industries
```

### 回测API

```bash
# 策略回测
POST /api/v1/backtest
{
  "stock_code": "600519",
  "agent": "buffet",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 1000000
}

# 获取支持的Agent
GET /api/v1/backtest/agents
```

## 🧪 测试

```bash
# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest tests/unit

# 查看测试覆盖率
poetry run pytest --cov=app --cov-report=html
```

## 🛠️ 开发

### 添加新的Agent

```python
from app.agents.base import BaseAgent
from app.services.tushare_service import TushareService

class MyAgent(BaseAgent):
    def __init__(self, tushare_service: TushareService):
        super().__init__(tushare_service)

    @property
    def name(self) -> str:
        return "MyAgent"

    @property
    def style(self) -> str:
        return "我的投资风格"

    async def analyze(self, state: AnalysisState) -> AgentAnalysis:
        # 实现分析逻辑
        return {
            "agent_name": self.name,
            "action": "buy|sell|hold",
            "confidence": 0.8,
            "reasoning": "决策理由",
            "key_metrics": {}
        }
```

## 📋 设计原则

本项目严格遵循以下软件工程原则：

1. **SOLID原则**:
   - 单一职责: 每个类专注一件事
   - 开闭原则: 通过Agent扩展功能
   - 里氏替换: 所有Agent可互换
   - 接口隔离: 专一的小接口
   - 依赖倒置: 依赖抽象而非具体

2. **DRY**: 避免代码重复，提取公共逻辑
3. **KISS**: 保持简单，优先最直观的方案
4. **YAGNI**: 只实现当前需要的功能

## 🤝 贡献

欢迎贡献！请查看 `CONTRIBUTING.md` 了解详情。

1. Fork项目
2. 创建特性分支
3. 提交更改 (使用Conventional Commits)
4. 推送到分支
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Tushare](https://tushare.pro/) - 提供金融数据接口
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent框架基础
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI组件库

## 📞 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/invest-agent-by-graph)
- 问题反馈: [GitHub Issues](https://github.com/yourusername/invest-agent-by-graph/issues)
- 详细文档: [docs/](./docs/)

---

⚠️ **免责声明**: 本项目仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。
=======
# invest_agent
