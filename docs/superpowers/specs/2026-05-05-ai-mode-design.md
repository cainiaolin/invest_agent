# AI模式投资分析系统设计文档

**日期**: 2026-05-05
**版本**: 1.0
**作者**: Claude Code
**状态**: 设计阶段

---

## 1. 概述

### 1.1 目标

为现有投资分析系统增加AI模式，使Agent能够：
1. 配置调用指定的LLM模型（OpenAI/Claude/本地模型等）
2. 根据投资大师的经验知识（存储在md文件）结合Tushare数据做投资决策
3. 使用思维链推理确保投资结论准确可靠

### 1.2 设计原则

- **最小侵入性**: 保留现有BaseAgent接口，通过扩展实现新功能
- **渐进式迁移**: 新旧Agent并存，支持A/B对比测试
- **配置驱动**: LLM模型、知识文件均可配置
- **容错降级**: LLM失败时自动降级到规则引擎
- **可观测性**: 详细记录LLM推理过程

### 1.3 方案选择

采用**方案A：LLM Agent增强架构**
- 保留现有BaseAgent接口
- 新增LLMAgent基类
- 每个大师创建对应的LLM{大师}Agent
- 知识文件采用知识图谱形式
- 使用思维链推理保证可靠性

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────┐
│                  API Layer                          │
│           /api/v1/analyze (现有接口扩展)             │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  Agent Layer                        │
│  ┌──────────────┐      ┌──────────────┐            │
│  │ RuleAgent    │      │  LLMAgent    │            │
│  │ (现有6个)    │      │  (新增AI)    │            │
│  └──────────────┘      └──────────────┘            │
│         ↓                      ↓                     │
│  规则引擎               LLM推理引擎                   │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Services Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │TushareService│  │ LLMService   │  │Knowledge  │ │
│  │  (数据获取)  │  │  (模型调用)  │  │ Service   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Knowledge Layer                        │
│     /knowledge/graham/GRAHAM_AGENT_SUMMARY.md       │
│     /knowledge/buffet/BUFFET_AGENT_SUMMARY.md       │
│                  ... (其他大师)                      │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 路径 | 职责 |
|------|------|------|
| LLMAgent | app/agents/llm_agent.py | LLM Agent抽象基类 |
| LLMService | app/services/llm_service.py | 统一LLM调用服务 |
| KnowledgeService | app/services/knowledge_service.py | 知识文件管理 |
| LLMGrahamAgent | app/agents/value/llm_graham_agent.py | 格雷厄姆AI Agent |
| 知识文件 | knowledge/{master}/*.md | 大师投资知识 |

---

## 3. 详细设计

### 3.1 LLMAgent 基类

**文件**: `app/agents/llm_agent.py`

```python
class LLMAgent(BaseAgent):
    """
    基于LLM的智能投资Agent基类

    特点：
    - 使用思维链(Chain-of-Thought)推理
    - 结合知识图谱和实时数据
    - 支持多LLM模型配置
    - 自动降级到规则引擎
    """

    def __init__(
        self,
        tushare_service,
        llm_service: LLMService,
        knowledge_service: KnowledgeService,
        master_name: str
    ):
        super().__init__(tushare_service)
        self.llm = llm_service
        self.knowledge = knowledge_service
        self.master_name = master_name

    @abstractmethod
    def master_name(self) -> str:
        """大师名称"""
        pass

    async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行投资分析

        流程：
        1. 获取股票数据
        2. 加载大师知识
        3. 构建思维链Prompt
        4. 调用LLM推理
        5. 验证并解析结果
        6. 失败时降级到规则引擎
        """
```

### 3.2 LLMService 服务

**文件**: `app/services/llm_service.py`

**功能**:
- 统一的LLM调用接口
- 支持OpenAI、Anthropic、本地模型
- 自动重试机制（速率限制、网络错误）
- 响应格式验证

**配置格式**:
```python
{
    "provider": "openai",  # openai | anthropic | local
    "model": "gpt-4o",
    "api_key": "sk-...",
    "base_url": "...",  # 可选，用于本地模型
    "temperature": 0.7,
    "max_tokens": 4000
}
```

**错误处理**:
- `LLMRateLimitError`: 速率限制，自动重试
- `LLMTokenLimitError`: Token超限，自动缩短Prompt
- `LLMInvalidResponseError`: 响应格式错误，重试或降级

### 3.3 KnowledgeService 服务

**文件**: `app/services/knowledge_service.py`

**功能**:
- 加载md知识文件
- 解析frontmatter元数据
- 提取特定章节内容
- 内存缓存提升性能

**知识文件结构**:
```
knowledge/
├── graham/
│   ├── GRAHAM_AGENT_SUMMARY.md  # 主要知识文件
│   ├── cases.md                  # 经典案例
│   └── metrics.md                # 指标定义
├── buffet/
│   ├── BUFFET_AGENT_SUMMARY.md
│   └── ...
└── ...
```

### 3.4 知识文件格式

**GRAHAM_AGENT_SUMMARY.md 结构**:

```markdown
# Benjamin Graham 投资大师知识图谱

## 元数据
---
master_name: graham
display_name: 本杰明·格雷厄姆
school: 价值投资
---

## 核心投资哲学
- 内在价值概念
- 安全边际理论
- Net-Net策略

## 核心评估维度
1. 安全边际分析
2. 盈利收益率
3. 财务安全性
4. 估值吸引力
5. Net-Net机会

## 决策规则
- 买入条件（必须同时满足...）
- 持有条件
- 卖出/回避条件

## 经典案例
- 成功案例: GEICO
- 失败教训: 1929大萧条

## 分析检查清单
- [ ] 内在价值计算
- [ ] 安全边际验证
- ...
```

### 3.5 LLMGrahamAgent 实现

**文件**: `app/agents/value/llm_graham_agent.py`

**核心方法**:

1. `_calculate_graham_metrics()`: 计算Graham特有指标
2. `_build_graham_cot_prompt()`: 构建思维链Prompt
3. `_validate_result()`: 验证LLM结果合理性
4. `_fallback_to_rule_engine()`: 降级到规则引擎

**思维链步骤**:
1. 数据理解
2. 理念对照
3. 维度评分
4. 风险识别
5. 决策推理
6. 格雷厄姆语气总结

---

## 4. API集成

### 4.1 请求参数扩展

```python
class AnalyzeRequest(BaseModel):
    stock_code: str
    mode: str = "parallel"
    agents: Optional[str] = None
    agent_mode: str = "rule"  # 新增: "rule" | "ai" | "hybrid"
    llm_config: Optional[Dict] = None  # 新增
    verbose: bool = False
```

### 4.2 Agent注册系统

```python
# 规则引擎Agent
RULE_AGENTS = {
    "graham": GrahamAgent,
    "buffet": BuffetAgent,
    ...
}

# AI增强Agent
AI_AGENTS = {
    "graham": LLMGrahamAgent,
    "buffet": LLMBuffetAgent,
    ...
}

def get_agent(agent_name: str, mode: str = "rule", **kwargs):
    """统一的Agent获取接口"""
    if mode == "ai":
        return AI_AGENTS.get(agent_name)(**kwargs)
    return RULE_AGENTS.get(agent_name)(**kwargs)
```

---

## 5. 前端集成

### 5.1 UI组件

**新增组件**:
1. `AgentModeSelector`: 选择规则/AI/混合模式
2. `LLMConfigPanel`: LLM配置面板
3. `ThoughtProcessViewer`: 思维过程展示

### 5.2 分析模式切换

- **规则引擎模式**: 使用现有硬编码规则
- **AI增强模式**: 使用LLM推理
- **混合模式**: 同时运行两种模式，对比结果

### 5.3 响应展示

AI模式额外展示：
- 思维链推理过程
- 各维度详细评分
- LLM模型信息
- 降级标记（如适用）

---

## 6. 错误处理

### 6.1 LLM调用错误

| 错误类型 | 处理策略 |
|---------|---------|
| 速率限制(429) | 指数退避重试 |
| Token超限(400) | 缩短Prompt重试 |
| 网络错误 | 重试3次 |
| 响应格式错误 | 重试或降级 |
| 超时 | 降级到规则引擎 |

### 6.2 降级策略

```python
try:
    # 尝试LLM分析
    return await self._analyze_with_llm(state)
except LLMServiceError:
    # 降级到规则引擎
    return await self._fallback_to_rule_engine(state)
```

### 6.3 结果验证

- action合法性检查
- confidence范围检查[0,1]
- 投资逻辑一致性检查（如：安全边际为负不应买入）
- 数据完整性检查

---

## 7. 测试策略

### 7.1 单元测试

**测试覆盖**:
- LLMService各provider调用
- KnowledgeService文件加载
- Agent基础逻辑
- 错误处理重试机制

### 7.2 集成测试

**测试场景**:
- 完整分析流程
- LLM失败降级
- 多Agent协作
- 知识文件缺失处理

### 7.3 A/B测试

**对比维度**:
- 规则引擎 vs AI Agent决策一致性
- 分析深度对比
- 响应时间对比
- 用户满意度对比

---

## 8. 部署配置

### 8.1 环境变量

```bash
# LLM配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# AI模式
AI_MODE_ENABLED=true
KNOWLEDGE_BASE_PATH=knowledge
```

### 8.2 Docker配置

**新增内容**:
- 挂载knowledge目录
- LLM API密钥配置
- 可选的Redis缓存

---

## 9. 实施计划

### Phase 1: 基础设施 (Week 1)
- [ ] 创建LLMService
- [ ] 创建KnowledgeService
- [ ] 创建LLMAgent基类
- [ ] 编写单元测试

### Phase 2: Agent实现 (Week 2)
- [ ] 实现LLMGrahamAgent
- [ ] 编写Graham知识文件
- [ ] 编写集成测试
- [ ] A/B测试对比

### Phase 3: API集成 (Week 3)
- [ ] 扩展API接口
- [ ] Agent注册系统
- [ ] 错误处理完善

### Phase 4: 前端开发 (Week 4)
- [ ] 模式选择UI
- [ ] LLM配置面板
- [ ] 思维过程展示

### Phase 5: 测试与优化 (Week 5)
- [ ] 端到端测试
- [ ] 性能优化
- [ ] 文档完善

---

## 10. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| LLM API成本高 | 运营成本 | 缓存、批处理、本地模型 |
| LLM响应慢 | 用户体验 | 超时设置、降级策略 |
| LLM结果不稳定 | 决策质量 | 多次采样、结果验证 |
| Token超限 | 功能限制 | Prompt优化、分段处理 |
| 知识文件维护 | 可维护性 | 版本控制、模板化 |

---

## 11. 成功指标

1. **功能指标**
   - AI模式可用率 > 99%
   - 降级率 < 5%
   - 响应时间 < 30秒

2. **质量指标**
   - AI vs 规则引擎决策一致性 > 70%
   - 用户满意度 > 80%
   - 分析深度评分 > 4/5

3. **性能指标**
   - LLM调用成功率 > 95%
   - 平均响应时间 < 20秒
   - 缓存命中率 > 30%

---

## 12. 附录

### 12.1 文件清单

**新增文件**:
- app/agents/llm_agent.py
- app/agents/value/llm_graham_agent.py
- app/agents/value/llm_buffet_agent.py
- app/services/llm_service.py
- app/services/knowledge_service.py
- knowledge/graham/GRAHAM_AGENT_SUMMARY.md
- knowledge/buffet/BUFFET_AGENT_SUMMARY.md

**修改文件**:
- app/api/routes/analyze.py
- app/core/config.py
- frontend/src/views/AnalyzeView.vue
- frontend/src/api/analyze.ts

### 12.2 依赖更新

```toml
[tool.poetry.dependencies]
httpx = "^0.27.0"
python-frontmatter = "^1.0.0"
```

---

**文档结束**
