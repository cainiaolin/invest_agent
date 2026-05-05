# 数据服务重构总结

## 🎯 核心问题

您指出的问题：
> Tushare有很多数据可以获取，而不是直接get设置默认值，各个agent需要的关键数据获取不到应该报错

**现状问题**：
1. Tushare数据获取失败时返回空字典`{}`
2. Agent使用`.get(key, 0)`掩盖了数据缺失
3. ROE、利润率等关键指标为0时仍输出决策
4. 用户无法知道决策基于真实数据还是默认值

## ✅ 解决方案

### 1. 创建异常体系（`app/services/exceptions.py`）

定义了明确的异常类型：
- **TushareAPIError**：API调用失败
- **TusharePermissionError**：权限不足（积分不够）
- **TushareDataNotFoundError**：数据不存在
- **MissingCriticalDataError**：缺少关键数据
- **InvalidDataError**：数据无效

### 2. 重构TushareService（`app/services/tushare_service.py`）

**关键改进**：
- 返回类型从`Dict[str, Any]`改为`pd.DataFrame`
- 失败时抛出异常而非返回空字典
- 自动检测权限不足
- `get_stock_fundamentals`确保关键数据完整

### 3. 数据质量检查（`app/services/data_validator.py`）

**功能**：
- 定义各Agent的关键数据要求
- 验证必需字段是否存在且非零
- 检查数据值的合理性
- 计算数据质量评分
- 严格模式下缺少关键数据时抛出异常

### 4. Agent重构示例（`app/agents/value/graham_agent_v2.py`）

展示了如何：
- 使用新的错误处理机制
- 验证数据质量
- 数据不足时拒绝决策
- 提供有意义的错误信息

## 📊 Tushare 2000积分权限

根据文档，2000积分可以访问：

| 接口 | 数据 | 说明 |
|------|------|------|
| `daily_basic` | PE、PB、市值、换手率 | 每日基本面数据 |
| `income` | EPS、营收、利润、成本 | 利润表 |
| `balancesheet` | 资产、负债、权益 | 资产负债表 |
| `cashflow` | 经营现金流、净利润 | 现金流量表 |
| `fina_indicator` | ROE、利润率、增长率 | 财务指标（预计算） |

**调用限制**：
- 频率：200次/分钟
- 日限制：100,000次/天
- 注意：需要按股票代码逐个查询

## 🔧 迁移指南

### 步骤1：更新Agent导入

```python
from app.services.exceptions import (
    TushareAPIError,
    TushareDataNotFoundError,
    MissingCriticalDataError,
    TusharePermissionError
)
from app.services.data_validator import DataValidator
```

### 步骤2：修改analyze方法

```python
async def analyze(self, state: AnalysisState) -> dict:
    try:
        stock_data = await self._get_validated_stock_data(...)
        return self._analyze_with_data(stock_data)
    except MissingCriticalDataError as e:
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"缺少关键数据：{', '.join(e.missing_fields)}",
            "error_type": "missing_critical_data"
        }
```

### 步骤3：创建验证方法

```python
async def _get_validated_stock_data(self, stock_code: str) -> dict:
    # 获取数据（失败会抛出异常）
    fundamentals = await self.tushare.get_stock_fundamentals(stock_code)

    # 提取数据
    metrics = {...}

    # 验证数据质量
    DataValidator.validate_stock_data(
        {"symbol": stock_code, "metrics": metrics},
        agent_name=self.name,
        strict_mode=True
    )

    return {"symbol": stock_code, "metrics": metrics}
```

### 步骤4：移除默认值使用

```python
# ❌ 旧代码
eps = metrics.get("eps", 0)

# ✅ 新代码（已验证）
eps = metrics["eps"]
```

## 📝 Agent关键数据要求

| Agent | 必需字段 | 原因 |
|-------|---------|------|
| Buffet | roe, debt_ratio, current_ratio, profit_margin | 护城河分析 |
| Graham | eps, bvps, pe_ratio, debt_ratio, current_ratio | 内在价值计算 |
| Fisher | revenue_growth, profit_growth, gross_margin, operating_margin | 成长质量评估 |
| Lynch | pe_ratio, revenue_growth, profit_growth | PEG比率 |
| Dalio | debt_ratio, current_ratio | 债务周期分析 |
| Soros | revenue_growth, profit_growth | 趋势分析 |

## 📁 文件清单

### 新增文件
- ✅ `app/services/exceptions.py` - 异常定义
- ✅ `app/services/data_validator.py` - 数据验证器
- ✅ `app/agents/value/graham_agent_v2.py` - 重构示例
- ✅ `app/services/README.md` - 使用文档
- ✅ `docs/CODE_MIGRATION_GUIDE.md` - 代码对比文档

### 修改文件
- ✅ `app/services/tushare_service.py` - 重构错误处理

### 待迁移文件
- ⏳ `app/agents/value/buffet_agent.py`
- ⏳ `app/agents/value/graham_agent.py`
- ⏳ `app/agents/growth/fisher_agent.py`
- ⏳ `app/agents/growth/lynch_agent.py`
- ⏳ `app/agents/macro/dalio_agent.py`
- ⏳ `app/agents/macro/soros_agent.py`
- ⏳ `app/api/routes/analyze.py` - 添加异常处理

## 🎓 设计原则

1. **Fail Fast**：数据不足时立即失败，而非使用默认值
2. **明确错误**：区分API错误、权限不足、数据不存在
3. **用户透明**：明确告知数据问题和原因
4. **数据质量**：验证关键指标的非零性和合理性
5. **优雅降级**：异常情况下返回有意义的错误信息

## 📚 参考资料

- [Tushare积分与权限](https://tushare.pro/document/1?doc_id=290)
- [Tushare利润表接口](https://tushare.pro/document/2?doc_id=33)
- [SOLID原则](https://en.wikipedia.org/wiki/SOLID)
- [Fail Fast原则](https://en.wikipedia.org/wiki/Fail-fast)

## 🚀 下一步

1. **测试**：测试graham_agent_v2.py
2. **迁移**：将其他Agent迁移到新架构
3. **前端**：更新前端显示数据质量警告
4. **文档**：更新用户文档说明数据要求

## 📞 问题反馈

如有问题或建议，请查看：
- `app/services/README.md` - 详细文档
- `docs/CODE_MIGRATION_GUIDE.md` - 代码对比
- `app/agents/value/graham_agent_v2.py` - 参考实现
