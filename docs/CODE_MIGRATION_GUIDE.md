# 代码重构对比文档

## 问题说明

您指出的核心问题是：**Tushare数据获取失败时直接使用默认值0，导致Agent基于错误数据做出决策**。

## 代码对比

### 1. TushareService数据获取

#### ❌ 旧代码（tushare_service.py）

```python
async def get_daily_basic(self, stock_code: str) -> Dict[str, Any]:
    """获取股票每日基本面数据"""
    try:
        df = self.api.daily_basic(...)
        if df.empty:
            logger.warning(f"数据为空")
            return {}  # ❌ 返回空字典
        return {"daily_basic": df}
    except Exception as e:
        logger.error(f"获取失败: {e}")
        return {}  # ❌ 掩盖所有错误
```

**问题**：
- 返回空字典`{}`，调用方无法区分"失败"和"无数据"
- 异常被吞掉，错误原因丢失
- 调用方不知道是否应该重试或报告用户

#### ✅ 新代码（tushare_service.py）

```python
async def get_daily_basic(self, stock_code: str) -> pd.DataFrame:
    """获取股票每日基本面数据"""
    try:
        df = self.api.daily_basic(...)
        if df.empty:
            # ✅ 明确抛出异常
            raise TushareDataNotFoundError(
                api_name="daily_basic",
                stock_code=stock_code,
                reason="无数据"
            )
        return df  # ✅ 直接返回DataFrame
    except Exception as e:
        error_msg = str(e)
        # ✅ 区分权限不足和其他错误
        if "权限" in error_msg or "积分" in error_msg:
            raise TusharePermissionError(
                api_name="daily_basic",
                required_points=self.REQUIRED_POINTS,
                current_points=0
            )
        # ✅ 传递原始错误信息
        raise TushareAPIError(
            message=f"获取失败: {error_msg}",
            api_name="daily_basic",
            stock_code=stock_code,
            original_error=e
        )
```

**改进**：
- 返回`pd.DataFrame`而非`Dict`，类型明确
- 数据为空时抛出`TushareDataNotFoundError`
- 区分权限不足、API错误等不同情况
- 保留原始错误信息便于调试

### 2. Agent数据使用

#### ❌ 旧代码（graham_agent.py）

```python
async def _get_stock_data(self, stock_code: str) -> dict:
    """从tushare获取股票数据"""
    try:
        fundamentals = await self.tushare.get_stock_fundamentals(stock_code)
        # ... 获取各种数据
    except Exception as e:
        print(f"获取失败: {e}")
        # ❌ 返回全是默认值0的字典
        return {
            "symbol": stock_code,
            "metrics": {
                "eps": 0,  # ❌ 默认值
                "roe": 0,  # ❌ 默认值
                "debt_ratio": 0,  # ❌ 默认值
                # ... 更多默认值
            }
        }

def _analyze_stock_data(self, stock_data: dict) -> dict:
    """分析股票数据"""
    metrics = stock_data.get("metrics", {})

    # ❌ 使用.get(key, 0)掩盖了数据缺失
    eps = metrics.get("eps", 0)  # 可能是默认值0
    roe = metrics.get("roe", 0)  # 可能是默认值0
    debt_ratio = metrics.get("debt_ratio", 100)  # 默认值100

    # ❌ 基于可能是默认值的数据进行计算
    intrinsic_value = self._calculate_graham_intrinsic_value(eps, bvps)

    # ❌ 即使数据全部为0，仍然返回决策
    return {
        "decision": "buy",  # 可能基于错误数据
        "confidence": 0.8,
        "reasoning": "基于内在价值分析..."  # 但实际数据全是0
    }
```

**问题**：
- 数据获取失败时返回默认值0
- Agent无法区分真实数据和默认值
- 可能基于错误的0值做出买入决策
- 用户不知道决策基于的数据质量

#### ✅ 新代码（graham_agent_v2.py）

```python
async def _get_validated_stock_data(self, stock_code: str) -> dict:
    """获取并验证股票数据"""
    try:
        # ✅ get_stock_fundamentals现在会抛出异常
        fundamentals = await self.tushare.get_stock_fundamentals(stock_code)

        # ✅ 直接访问字段，不使用默认值
        income = fundamentals["income"]  # 如果不存在会抛KeyError
        latest_income = income.iloc[0]
        eps = float(latest_income["basic_eps"])  # 真实数据或异常

        fina = fundamentals["fina_indicator"]
        latest_fina = fina.iloc[0]
        roe = float(latest_fina["roe"])  # 真实数据或异常

        # ✅ 构建metrics字典
        metrics = {
            "eps": eps,
            "roe": roe,
            # ... 其他字段
        }

        # ✅ 验证数据质量
        from app.services.data_validator import DataValidator
        validation_result = DataValidator.validate_stock_data(
            {"symbol": stock_code, "metrics": metrics},
            agent_name=self.name,
            strict_mode=True  # ✅ 缺少必需字段时抛出异常
        )

        # ✅ 添加数据质量信息
        return {
            "symbol": stock_code,
            "metrics": metrics,
            "data_quality": validation_result
        }

    except TusharePermissionError as e:
        # ✅ 明确处理权限不足
        raise
    except MissingCriticalDataError as e:
        # ✅ 明确处理数据缺失
        raise
    except TushareAPIError as e:
        # ✅ 明确处理API错误
        raise

async def analyze(self, state: AnalysisState) -> dict:
    """分析股票"""
    try:
        # ✅ 获取验证过的数据（失败会抛出异常）
        stock_data = await self._get_validated_stock_data(stock_code)

        # ✅ 基于验证过的数据进行分析
        return self._analyze_stock_data(stock_data)

    except MissingCriticalDataError as e:
        # ✅ 关键数据缺失 - 拒绝决策
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"缺少关键数据({', '.join(e.missing_fields)})，无法决策",
            "error_type": "missing_critical_data",
            "missing_fields": e.missing_fields
        }

    except TusharePermissionError as e:
        # ✅ 权限不足 - 明确告知用户
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"数据权限不足，需要{e.required_points}积分",
            "error_type": "permission_error"
        }

    except TushareAPIError as e:
        # ✅ API错误 - 提供错误信息
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"数据获取失败：{e.message}",
            "error_type": "api_error"
        }
```

**改进**：
- 数据获取失败时抛出明确异常
- 使用`strict_mode=True`强制验证关键数据
- 数据不足时拒绝决策（confidence=0.0）
- 提供详细的错误信息给用户
- 区分不同类型的错误

### 3. 数据质量检查

#### 新增功能（data_validator.py）

```python
class DataValidator:
    """数据质量验证器"""

    AGENT_DATA_REQUIREMENTS = {
        "graham": {
            "required": ["eps", "bvps", "pe_ratio", "debt_ratio", "current_ratio"],
            "optional": ["pb_ratio", "net_margin", "revenue_growth"],
            "reason": "格雷厄姆需要计算内在价值和安全边际"
        },
        # ... 其他Agent
    }

    @staticmethod
    def validate_stock_data(
        stock_data: Dict[str, Any],
        agent_name: str,
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """验证股票数据质量"""
        metrics = stock_data.get("metrics", {})

        # 获取Agent的数据要求
        requirements = DataValidator.AGENT_DATA_REQUIREMENTS.get(agent_name, {...})
        required_fields = requirements["required"]

        # ✅ 检查必需字段
        missing_fields = []
        for field in required_fields:
            value = metrics.get(field)
            if value is None or value == 0:
                missing_fields.append(field)

        # ✅ 严格模式：抛出异常
        if strict_mode and missing_fields:
            raise MissingCriticalDataError(
                missing_fields=missing_fields,
                stock_code=stock_data.get("symbol", ""),
                agent_name=agent_name
            )

        # ✅ 检查数据值的合理性
        invalid_fields = []
        for field, value in metrics.items():
            if field == "pe_ratio" and (value < 0 or value > 1000):
                invalid_fields.append(f"{field}={value} (PE异常)")
            # ... 更多验证

        # ✅ 计算数据质量评分
        quality_score = DataValidator._calculate_quality_score(...)

        return {
            "is_valid": len(missing_fields) == 0,
            "missing_required": missing_fields,
            "invalid_fields": invalid_fields,
            "data_quality_score": quality_score
        }
```

**功能**：
- 定义各Agent的关键数据要求
- 验证必需字段是否存在且非零
- 检查数据值的合理性
- 计算数据质量评分
- 严格模式下缺少关键数据时抛出异常

## 迁移步骤

### 1. 更新依赖导入

```python
# 在Agent文件中添加
from app.services.exceptions import (
    TushareAPIError,
    TushareDataNotFoundError,
    MissingCriticalDataError,
    TusharePermissionError
)
from app.services.data_validator import DataValidator
```

### 2. 修改analyze方法

```python
async def analyze(self, state: AnalysisState) -> dict:
    try:
        stock_data = await self._get_validated_stock_data(...)
        return self._analyze_with_data(stock_data)
    except (MissingCriticalDataError, TusharePermissionError) as e:
        return {
            "action": "hold",
            "confidence": 0.0,
            "reasoning": f"数据不足：{str(e)}",
            "error_type": type(e).__name__
        }
```

### 3. 创建_get_validated_stock_data方法

参考`graham_agent_v2.py`中的实现。

### 4. 移除.get(key, default)调用

```python
# ❌ 旧代码
eps = metrics.get("eps", 0)

# ✅ 新代码（已验证）
eps = metrics["eps"]  # 如果不存在会在验证阶段抛出异常
```

## 测试建议

1. **测试数据缺失场景**：
   - 模拟Tushare返回空数据
   - 验证Agent返回confidence=0.0

2. **测试权限不足场景**：
   - 模拟权限错误响应
   - 验证错误信息正确显示

3. **测试异常值场景**：
   - 传入异常的PE、ROE值
   - 验证数据质量检查

4. **对比测试**：
   - 同时运行新旧版本
   - 验证决策一致性

## 总结

| 方面 | 旧代码 | 新代码 |
|------|--------|--------|
| **错误处理** | 返回空字典/默认值 | 抛出明确异常 |
| **数据验证** | 无验证 | 严格验证关键字段 |
| **决策质量** | 可能基于错误数据 | 数据不足时拒绝决策 |
| **用户体验** | 无法知道数据质量 | 明确告知数据问题 |
| **可维护性** | 错误难以调试 | 错误信息详细 |

## 相关文件

- `app/services/exceptions.py` - 异常定义
- `app/services/data_validator.py` - 数据验证器
- `app/services/tushare_service.py` - Tushare服务（已重构）
- `app/agents/value/graham_agent_v2.py` - 重构示例
- `app/services/README.md` - 详细文档
