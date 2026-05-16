# 搜索增强Agent使用指南

## 概述

搜索增强Agent是在现有LLM Agent基础上，增加了智能联网搜索能力的新一代Agent。

## 核心特性

### 1. 智能搜索
- 多源搜索：官方公告、市场新闻、行业动态
- 可信度评估：自动评估信息质量
- 个性化策略：每个Agent有不同的搜索偏好

### 2. 深度融合
- 历史数据与实时信息结合
- 结构化分析上下文
- LLM友好的信息格式

### 3. 智能分析
- 应用投资大师哲学
- 考虑最新市场动态
- 提供更准确的投资建议

## 使用方法

### 基本使用

```python
from app.agents.value.buffet_search_agent import BuffetSearchAgent

# 创建Agent实例
agent = BuffetSearchAgent(
    tushare_service=tushare_service,
    search_service=search_service,
    llm_service=llm_service,
    knowledge_service=knowledge_service
)

# 分析股票
result = await agent.analyze({
    "stock_code": "600519",
    "mode": "parallel"
})
```

### API使用

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "mode": "parallel",
    "agents": "buffet",
    "agent_mode": "search_enhanced"
  }'
```

## 搜索策略

各Agent的搜索策略：

| Agent | 基本面 | 市场情绪 | 行业 | 竞争对手 | 时间范围 | 可信度 |
|-------|--------|----------|------|----------|----------|--------|
| Buffett | ✓ | ✗ | ✓ | ✓ | 30天 | 0.7 |
| Graham | ✓ | ✗ | ✗ | ✗ | 90天 | 0.8 |
| Fisher | ✓ | ✓ | ✓ | ✓ | 60天 | 0.6 |
| Lynch | ✓ | ✓ | ✓ | ✗ | 14天 | 0.6 |
| Soros | ✗ | ✓ | ✓ | ✗ | 7天 | 0.5 |
| Dalio | ✓ | ✓ | ✓ | ✓ | 30天 | 0.6 |

## 配置

在`.env`文件中配置：

```bash
# 启用搜索增强
SEARCH_ENABLED=true

# Agent个性化配置
BUFFET_SEARCH_HORIZON=30
```

## 降级策略

当搜索服务不可用时，Agent会自动降级到基础LLM分析或规则引擎，确保服务可用性。