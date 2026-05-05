# 数据服务重构说明

## 问题背景

原代码存在以下问题：

1. **静默失败**：Tushare数据获取失败时返回空字典或默认值0
2. **数据质量未知**：无法区分真实数据和默认值
3. **决策风险**：关键指标为0时仍可做出投资决策
4. **错误掩盖**：使用`.get(key, 0)`掩盖了数据获取失败

## 解决方案

### 1. 异常体系（`exceptions.py`）

定义了明确的异常类型：

- **TushareAPIError**：API调用失败
- **TusharePermissionError**：权限不足（积分不够）
- **TushareDataNotFoundError**：数据不存在
- **MissingCriticalDataError**：缺少关键数据
- **InvalidDataError**：数据无效

### 2. TushareService重构

**核心改进**：

```python
# 旧代码：返回空字典
async def get_daily_basic(self, stock_code: str) -> Dict[str, Any]:
    try:
        df = self.api.daily_basic(...)
        if df.empty:
            return {}  # ❌ 静默失败
        return {"daily_basic": df}
    except Exception as e:
        return {}  # ❌ 掩盖错误

# 新代码：抛出异常
async def get_daily_basic(self, stock_code: str) -> pd.DataFrame:
    df = self.api.daily_basic(...)
    if df.empty:
        raise TushareDataNotFoundError(...)  # ✅ 明确错误
    return df  # ✅ 直接返回DataFrame
```

**关键变化**：

1. **返回类型**：从`Dict[str, Any]`改为`pd.DataFrame`
2. **错误处理**：失败时抛出异常而非返回空字典
3. **权限检查**：自动检测并报告权限不足
4. **数据验证**：`get_stock_fundamentals`确保关键数据完整

### 3. 数据质量检查（`data_validator.py`）

**功能**：

- 验证Agent所需的关键字段
- 检查数据值的合理性
- 计算数据质量评分
- 提供详细的验证报告

**使用示例**：

```python
from app.services.data_validator import DataValidator

# 验证数据
validation_result = DataValidator.validate_stock_data(
    stock_data=stock_data,
    agent_name="Buffet",
    strict_mode=True  # 严格模式：缺少必需字段时抛出异常
)

if not validation_result["is_valid"]:
    # 处理验证失败
    pass
```

### 4. Agent使用示例

**旧代码**（使用默认值）：

```python
async def _get_stock_data(self, stock_code: str) -> dict:
    fundamentals = await self.tushare.get_stock_fundamentals(stock_code)
    income = fundamentals.get("income", pd.DataFrame())

    if not income.empty:
        eps = income.iloc[0].get("basic_eps", 0)  # ❌ 可能为默认值0
    else:
        eps = 0  # ❌ 默认值

    return {"eps": eps, ...}
```

**新代码**（严格验证）：

```python
async def _get_stock_data(self, stock_code: str) -> dict:
    try:
        # 1. 获取数据（失败会抛出异常）
        fundamentals = await self.tushare.get_stock_fundamentals(stock_code)

        # 2. 提取数据
        income = fundamentals["income"]
        balancesheet = fundamentals["balancesheet"]
        fina = fundamentals["fina_indicator"]

        # 3. 构建数据字典
        latest_income = income.iloc[0]
        eps = float(latest_income["basic_eps"])

        metrics = {
            "eps": eps,
            "roe": float(fina.iloc[0]["roe"]),
            # ... 其他字段
        }

        # 4. 验证数据质量
        from app.services.data_validator import DataValidator
        validation = DataValidator.validate_stock_data(
            {"symbol": stock_code, "metrics": metrics},
            agent_name=self.name,
            strict_mode=True
        )

        # 5. 返回验证通过的数据
        return {"symbol": stock_code, "metrics": metrics}

    except MissingCriticalDataError as e:
        # 关键数据缺失，拒绝决策
        logger.error(f"无法分析：{e}")
        raise
    except TusharePermissionError as e:
        # 权限不足
        logger.error(f"Tushare权限不足：{e}")
        raise
```

## Agent关键数据要求

各Agent所需的关键数据：

| Agent | 必需字段 | 说明 |
|-------|---------|------|
| **Buffet** | roe, debt_ratio, current_ratio, profit_margin | 护城河分析 |
| **Graham** | eps, bvps, pe_ratio, debt_ratio, current_ratio | 内在价值计算 |
| **Fisher** | revenue_growth, profit_growth, gross_margin, operating_margin | 成长质量评估 |
| **Lynch** | pe_ratio, revenue_growth, profit_growth | PEG比率 |
| **Dalio** | debt_ratio, current_ratio | 债务周期分析 |
| **Soros** | revenue_growth, profit_growth | 趋势分析 |

## Tushare 2000积分权限

**可访问的接口**：

- ✅ `daily_basic`：每日基本面（PE、PB等）
- ✅ `income`：利润表（EPS、营收、利润）
- ✅ `balancesheet`：资产负债表
- ✅ `cashflow`：现金流量表
- ✅ `fina_indicator`：财务指标（ROE、利润率等）

**接口限制**：

- 调用频率：200次/分钟
- 日限制：100,000次/天
- 单次查询：按股票代码逐个查询

## 迁移指南

### 1. 更新Agent的数据获取方法

**步骤**：

1. 移除`.get(key, default)`调用
2. 添加异常处理
3. 使用`DataValidator`验证数据
4. 在验证失败时拒绝决策

**示例**：

```python
# 1. 添加导入
from app.services.exceptions import MissingCriticalDataError, TusharePermissionError
from app.services.data_validator import DataValidator

# 2. 修改数据获取
async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
    try:
        stock_data = await self._get_validated_stock_data(
            state.get("stock_code", "")
        )
        return self._make_decision(stock_data)
    except (MissingCriticalDataError, TusharePermissionError) as e:
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"数据不足，无法决策：{str(e)}",
            "data_error": str(e)
        }

async def _get_validated_stock_data(self, stock_code: str) -> Dict:
    # 获取并验证数据
    fundamentals = await self.tushare.get_stock_fundamentals(stock_code)
    # ... 处理数据
    stock_data = {"metrics": metrics, ...}

    # 验证
    DataValidator.validate_stock_data(
        stock_data, self.name, strict_mode=True
    )

    return stock_data
```

### 2. API路由错误处理

在`analyze.py`中处理数据异常：

```python
from app.services.exceptions import TusharePermissionError, MissingCriticalDataError

@router.post("/")
async def analyze_stock(request: AnalyzeRequest):
    try:
        # ... 创建Agent
        analysis_result = await agent.analyze(state)
        # ...
    except TusharePermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=f"Tushare权限不足：{str(e)}"
        )
    except MissingCriticalDataError as e:
        return AnalyzeResponse(
            # ... 返回部分结果，标记数据不足
            error=f"关键数据缺失：{str(e)}"
        )
```

## 最佳实践

1. **严格模式**：生产环境使用`strict_mode=True`
2. **优雅降级**：捕获异常并提供有意义的错误消息
3. **数据日志**：记录数据质量评分和缺失字段
4. **用户通知**：前端显示数据质量警告
5. **缓存策略**：缓存有效数据减少API调用

## 测试建议

1. **单元测试**：测试各异常场景
2. **集成测试**：测试完整的数据获取流程
3. **边界测试**：测试权限不足、数据不存在等情况
4. **Agent测试**：验证各Agent的数据要求

## 相关文件

- `app/services/exceptions.py`：异常定义
- `app/services/data_validator.py`：数据验证器
- `app/services/tushare_service.py`：Tushare服务（已重构）
- `app/agents/base.py`：Agent基类
- `app/api/routes/analyze.py`：API路由
