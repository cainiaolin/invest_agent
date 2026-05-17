# 搜索增强功能使用指南

## 功能概述

搜索增强功能为LLM Agent提供了实时市场信息获取能力，使Agent能够基于最新动态做出更准确的投资决策。

### 核心能力

1. **多源数据聚合** - 整合巨潮资讯网、上交所、深交所等官方渠道
2. **智能爬虫系统** - 开源爬虫为主，LLM联网为辅
3. **可靠性评估** - 两阶段评估：规则过滤 + LLM深度分析
4. **时间窗口缓存** - 15分钟缓存，平衡实时性和性能
5. **综合信息融合** - 结构化分类 + 时间排序 + 可信度标签

## 配置说明

在`.env`文件中添加以下配置：

```bash
# 搜索增强配置
SEARCH_ENABLED=true                    # 是否启用搜索增强
SEARCH_CACHE_TTL=900                   # 缓存时间（秒），默认15分钟
SEARCH_PRIMARY_SOURCE=crawler          # 主搜索方式：crawler或llm
SEARCH_FALLBACK_LLM=true               # 是否启用LLM备用搜索
SEARCH_DAYS=7                          # 搜索最近N天信息
SEARCH_MAX_RESULTS=10                  # 每个源最大结果数

# 可靠性评估配置
RELIABILITY_THRESHOLD=0.5              # 最低可信度阈值
RELIABILITY_USE_LLM=true               # 是否使用LLM深度评估

# 爬虫配置
CRAWLER_USER_AGENT=Mozilla/5.0...
CRAWLER_TIMEOUT=10                     # 请求超时（秒）
CRAWLER_RETRY=3                        # 重试次数
CRAWLER_DELAY=1.0                      # 请求间隔（秒）
```

## 使用示例

### 1. 初始化搜索服务

```python
from app.services.search import create_search_service
from app.services.llm_service import LLMService

# 创建LLM服务
llm_service = LLMService()

# 创建搜索服务
search_service = create_search_service(llm_service)
```

### 2. 在Agent中使用

```python
from app.agents.value.llm_buffet_agent import LLMBuffetAgent

# 创建Agent时传入搜索服务
agent = LLMBuffetAgent(
    tushare_service=tushare_service,
    llm_service=llm_service,
    knowledge_service=knowledge_service,
    master_name="buffet",
    search_service=search_service  # 启用搜索增强
)

# Agent分析时会自动使用搜索增强
result = await agent.analyze({"stock_code": "600519"})
```

### 3. 独立使用搜索服务

```python
from app.services.search import create_search_service

search_service = create_search_service()

# 搜索股票信息
summary = await search_service.search_stock_info(
    stock_code="600519",
    stock_name="贵州茅台"
)

print(f"找到 {summary.total_results} 条信息")
print(f"高可信度: {summary.high_reliability_count}条")
print(f"中可信度: {summary.medium_reliability_count}条")
print(f"低可信度: {summary.low_reliability_count}条")
```

## 信息流

```
用户请求
   ↓
LLMAgent.analyze()
   ↓
获取Tushare历史数据
   ↓
获取搜索增强信息（新增）
   ├─ 检查缓存（15分钟窗口）
   ├─ 执行爬虫搜索
   │  ├─ 巨潮资讯网
   │  ├─ 上交所
   │  └─ 深交所
   ├─ 可靠性评估
   │  ├─ 规则过滤
   │  └─ LLM深度分析
   └─ 数据融合
   ↓
构建综合Prompt
   ├─ 历史财务数据
   └─ 实时搜索信息
   ↓
LLM推理决策
   ↓
返回分析结果
```

## 可信度评估机制

### 评估维度

1. **来源权威性（权重40%）**
   - 官方渠道（巨潮、交易所）：1.0
   - 主流财经媒体（新浪、东方财富）：0.8
   - 社交平台（雪球）：0.5
   - 其他：0.4

2. **时效性（权重30%）**
   - 1天内：1.0
   - 1周内：0.9
   - 1月内：0.7
   - 3月内：0.5
   - 更早：0.3

3. **内容类型（权重20%）**
   - 官方公告：1.0
   - 研究报告：0.9
   - 新闻：0.7
   - 评论：0.4

4. **是否官方（权重10%）**
   - 是：1.0
   - 否：0.5

### 评分标准

- **高可信度**：≥0.8 - 来源权威、内容新鲜
- **中可信度**：0.5-0.8 - 来源一般或时效性一般
- **低可信度**：<0.5 - 来源不明或内容过旧

## 性能优化

1. **缓存机制** - 15分钟时间窗口缓存，减少重复搜索
2. **并发爬取** - 多个爬虫并行工作
3. **智能限流** - 爬虫请求间隔控制，避免被封
4. **结果限制** - 每个源最多返回10条结果

## 故障处理

1. **爬虫失败** - 自动降级到LLM备用搜索
2. **搜索无结果** - 仅使用Tushare历史数据
3. **评估失败** - 使用规则评估作为后备
4. **超时处理** - 10秒超时，自动重试3次

## 注意事项

1. 爬虫可能受到目标网站结构变化影响，需要定期维护
2. LLM备用搜索需要模型支持联网功能
3. 搜索结果仅供参考，不构成投资建议
4. 请遵守目标网站的robots.txt和使用条款
