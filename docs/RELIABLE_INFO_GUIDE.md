# 可靠信息获取系统指南

## 设计原则

本系统遵循以下原则确保信息可靠性：

1. **来源可靠优先** - 所有数据来源均为官方或可信渠道
2. **多源验证** - 使用多个独立来源进行交叉验证
3. **透明可追溯** - 每条信息都标注来源和时间
4. **降级保护** - 任何环节失败都有备用方案

## 数据来源

### 主要数据源（按优先级）

#### 1. 东方财富API
- **类型**: 官方API
- **可靠性**: ⭐⭐⭐⭐⭐
- **更新频率**: 实时
- **数据类型**:
  - 公司公告
  - 财务数据
  - 新闻资讯
- **API特点**:
  - 稳定的RESTful接口
  - JSON格式返回
  - 支持股票代码过滤
  - 无需认证

#### 2. 新浪财经API
- **类型**: 官方API
- **可靠性**: ⭐⭐⭐⭐
- **更新频率**: 准实时
- **数据类型**:
  - 新闻资讯
  - 股票行情
- **API特点**:
  - 公开接口
  - 长期稳定
  - 支持历史数据

#### 3. 腾讯财经API
- **类型**: 官方API
- **可靠性**: ⭐⭐⭐⭐
- **更新频率**: 准实时
- **数据类型**:
  - 新闻资讯
  - 实时行情
- **API特点**:
  - 轻量级接口
  - 响应快速
  - 格式简单

### 备用验证

#### LLM联网验证（可选）
- **支持模型**:
  - Claude 3.5 Sonnet (with computer use)
  - Claude 3.7 Sonnet
  - GPT-4 with browsing
  - GPT-4o
- **作用**:
  - 验证已获取信息的准确性
  - 补充缺失的关键信息
  - 交叉验证多个来源
- **限制**:
  - 需要模型支持联网功能
  - 成本较高
  - 响应较慢

## 可靠性保障机制

### 1. 多层级降级策略

```
第一层: 东方财富API (最稳定)
    ↓ 失败
第二层: 新浪财经API
    ↓ 失败
第三层: 腾讯财经API
    ↓ 失败
第四层: LLM联网验证 (可选)
    ↓ 失败
降级: 仅使用Tushare历史数据
```

### 2. 信息验证

**来源验证**:
- 只接受来自白名单的来源
- 官方渠道优先级最高
- 主流财经媒体次之

**时效性验证**:
- 默认查询最近7天信息
- 可配置查询时间范围
- 过期信息自动过滤

**相关性验证**:
- 计算信息与股票的相关性
- 过滤低相关性信息
- 优先展示高相关性信息

### 3. 可信度评分

每条信息都会经过可信度评分，包含以下维度：

- **来源权威性** (40%): 官方=1.0, 主流媒体=0.8, 其他=0.5
- **时效性** (30%): 1天内=1.0, 1周内=0.9, 1月内=0.7
- **内容类型** (20%): 公告=1.0, 研报=0.9, 新闻=0.7
- **官方属性** (10%): 官方公告=1.0, 其他=0.5

**评分标准**:
- 高可信度: ≥0.8
- 中可信度: 0.5-0.8
- 低可信度: <0.5

### 4. LLM智能验证（可选）

当启用LLM验证时，系统会：

1. **准确性验证**: 检查已获取信息是否真实
2. **信息补充**: 补充缺失的关键信息
3. **交叉验证**: 与多个来源进行对比
4. **重要性标注**: 标注信息的重要程度

## 配置说明

### 基础配置

```bash
# .env文件

# 启用搜索增强
SEARCH_ENABLED=true

# 搜索模式（重要）
SEARCH_MODE=reliable  # reliable=可靠API, crawler=传统爬虫

# 搜索参数
SEARCH_DAYS=7                # 搜索最近7天
SEARCH_MAX_RESULTS=10        # 最多返回10条结果
SEARCH_CACHE_TTL=900         # 缓存15分钟

# LLM验证（可选）
SEARCH_ENABLE_LLM_VERIFY=true  # 是否启用LLM验证
```

### 模式选择建议

**可靠模式** (推荐):
```bash
SEARCH_MODE=reliable
```
- ✅ 使用稳定的金融API
- ✅ 数据来源可靠
- ✅ 响应快速
- ✅ 无需维护爬虫
- ❌ 信息来源相对固定

**爬虫模式**:
```bash
SEARCH_MODE=crawler
```
- ✅ 可定制性强
- ✅ 支持更多数据源
- ❌ 容易被反爬虫
- ❌ 需要定期维护
- ❌ 稳定性较差

## 使用示例

### API调用

```python
from app.services.reliable_info import ReliableSearchService

# 创建服务
search_service = ReliableSearchService(
    llm_service=llm_service,
    cache_ttl=900,
    search_days=7,
    max_results=10,
    enable_llm_verify=True
)

# 搜索信息
summary = await search_service.search_stock_info(
    stock_code="600519",
    stock_name="贵州茅台"
)

# 查看结果
print(f"总计: {summary.total_results}条")
print(f"高可信度: {summary.high_reliability_count}条")
print(f"中可信度: {summary.medium_reliability_count}条")
print(f"低可信度: {summary.low_reliability_count}条")

for result in summary.results:
    print(f"[{result.reliability_score.to_prompt_format()}] {result.title}")
    print(f"  来源: {result.source}")
    print(f"  时间: {result.publish_date}")
    print()
```

### 在Agent中使用

```python
from app.services.reliable_info import ReliableSearchService
from app.agents.value.llm_buffet_agent import LLMBuffetAgent

# 创建搜索服务
search_service = ReliableSearchService(llm_service=llm_service)

# 创建Agent时传入
agent = LLMBuffetAgent(
    tushare_service=tushare_service,
    llm_service=llm_service,
    knowledge_service=knowledge_service,
    master_name="buffet",
    search_service=search_service
)

# Agent分析时会自动使用搜索增强
result = await agent.analyze({"stock_code": "600519"})
```

## 性能优化

### 缓存机制

- 15分钟时间窗口缓存
- 避免重复API调用
- 显著提升响应速度
- 自动过期清理

### 并发请求

- 多个API并行调用
- 先返回先使用
- 失败自动切换

### 结果限制

- 每个源最多10条结果
- 去重处理
- 相关性排序
- 时效性优先

## 错误处理

### API失败处理

1. **单个API失败**: 自动切换到下一个API
2. **所有API失败**: 降级到仅使用Tushare数据
3. **LLM验证失败**: 使用API结果，跳过验证
4. **缓存失败**: 直接调用API

### 日志记录

所有关键操作都有详细日志：

```
INFO: 尝试使用 _fetch_from_eastmoney 获取新闻
INFO: _fetch_from_eastmoney 成功获取 5 条新闻
INFO: 搜索完成: 贵州茅台(600519), 总计5条, 高可信度4条
```

## 注意事项

1. **API限制**:
   - 东方财富API可能有频率限制
   - 建议增加缓存时间
   - 避免短时间内大量请求

2. **LLM成本**:
   - LLM验证会增加成本
   - 建议仅在重要分析时启用
   - 可通过配置开关控制

3. **数据延迟**:
   - API数据可能有几分钟延迟
   - 非实时行情数据
   - 建议结合Tushare实时数据使用

4. **免责声明**:
   - 所有信息仅供参考
   - 不构成投资建议
   - 投资决策需自行负责

## 未来扩展

### 计划添加的数据源

1. **官方数据源**:
   - 巨潮资讯网API
   - 上交所API
   - 深交所API

2. **付费数据源**（可选）:
   - Wind API
   - 同花顺iFinD
   - 东方财富Choice

3. **国际数据源**:
   - Yahoo Finance API
   - Alpha Vantage
   - IEX Cloud

### 功能增强

1. **智能摘要**: 使用LLM生成信息摘要
2. **情感分析**: 分析新闻情感倾向
3. **事件分类**: 自动分类重大事件
4. **价格影响**: 评估事件对价格的影响
