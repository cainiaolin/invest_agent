# Tushare 数据集成说明

## 概述

所有 6 个投资分析 Agent 已完成与 Tushare 数据的集成：

- **BuffetAgent** (巴菲特) - 价值投资
- **GrahamAgent** (格雷厄姆) - 深度价值投资
- **FisherAgent** (费雪) - 成长投资
- **LynchAgent** (林奇) - GARP投资
- **SorosAgent** (索罗斯) - 宏观对冲
- **DalioAgent** (达里奥) - 宏观经济分析

## 配置步骤

### 1. 获取 Tushare Token

访问 [Tushare Pro](https://tushare.pro/register) 注册账号并获取 API Token。

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
cd /path/to/invest_agent
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Tushare Token：

```env
TUSHARE_TOKEN=你的实际token
LOG_LEVEL=INFO
CACHE_TTL=3600
```

### 3. 验证配置

运行测试脚本验证配置：

```bash
cd invest_agent
python test_agent_integration.py
```

## 数据获取说明

### 已实现的 Tushare 数据接口

每个 Agent 的 `_get_stock_data` 方法现在会从 Tushare 获取以下数据：

#### 基本面数据

1. **每日基本面** (`daily_basic`)
   - PE、PB 比率
   - 市值数据
   - 股息率

2. **利润表** (`income`)
   - 营业收入
   - 净利润
   - 基本每股收益

3. **资产负债表** (`balancesheet`)
   - 总资产
   - 股东权益
   - 总负债
   - 流动资产/负债

4. **现金流量表** (`cashflow`)
   - 经营活动现金流
   - 净利润

#### 价格数据

- 日线数据（用于计算动量、波动率等）
- 收盘价、涨跌幅

### 计算的衍生指标

从原始数据计算出的关键指标：

- **ROE** (净资产收益率) = 净利润 / 股东权益 × 100%
- **负债率** = 总负债 / 总资产 × 100%
- **流动比率** = 流动资产 / 流动负债
- **毛利率** = 营业利润 / 营业收入 × 100%
- **净利率** = 净利润 / 营业收入 × 100%

### 需要额外数据源的字段

以下字段需要额外的数据接口，目前使用默认值或空值：

#### BuffetAgent 护城河指标
- `brand_strength` (品牌强度)
- `market_share` (市场份额)
- `competitive_advantage` (竞争优势)

#### FisherAgent 管理层质量
- `rd_ratio` (研发费用率)
- `management_tenure` (管理层任期)
- `employee_satisfaction` (员工满意度)

#### LynchAgent 商业信息
- `industry` (行业分类)
- `insider_buying` (内部人买入)
- `share_buyback` (股票回购)

#### SorosAgent 宏观指标
- `liquidity_cycle` (流动性周期)
- `credit_spread` (信用利差)
- `put_call_ratio` (看跌/看涨比率)

#### DalioAgent 宏观数据
- `gdp_growth` (GDP增长率)
- `inflation_rate` (通胀率)
- `unemployment_rate` (失业率)

## 使用示例

### Python 代码示例

```python
import asyncio
from app.services.tushare_service import TushareService
from app.agents.value.buffet_agent import BuffetAgent
from app.core.state import AnalysisState

async def analyze_stock():
    # 创建 Tushare 服务
    tushare_service = TushareService()

    # 创建 Agent
    buffet = BuffetAgent(tushare_service)

    # 分析股票（以贵州茅台为例）
    state = AnalysisState(stock_code="600519")
    result = await buffet.analyze(state)

    print(f"Agent: {result['agent_name']}")
    print(f"操作建议: {result['action']}")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"理由: {result['reasoning']}")

# 运行分析
asyncio.run(analyze_stock())
```

### CLI 命令示例

```bash
# 分析单只股票
python -m app.cli.main analyze 600519

# 使用指定 Agent 分析
python -m app.cli.main analyze 600519 --agents buffet,graham

# 分析多只股票
python -m app.cli.main analyze 600519,000001,000002
```

## 错误处理

当 Tushare API 调用失败时，Agent 会：

1. 捕获异常并记录错误日志
2. 返回空数据结构
3. Agent 会基于空数据进行保守分析

常见错误原因：

- **Token 无效**：检查 `.env` 文件中的 `TUSHARE_TOKEN` 是否正确
- **网络问题**：确保网络连接正常
- **API 频率限制**：Tushare 免费账户有调用频率限制
- **股票代码不存在**：检查股票代码格式是否正确

## 注意事项

1. **数据更新频率**
   - 基本面数据：季度更新
   - 每日数据：交易日收盘后更新
   - 建议设置合理的缓存时间（默认 3600 秒）

2. **API 调用限制**
   - 免费账户：每分钟 120 次
   - 积分账户：根据积分等级有不同的限制
   - 建议使用缓存减少重复调用

3. **股票代码格式**
   - 支持格式：`600519` 或 `600519.SH`
   - 系统会自动添加交易所后缀
   - 上海：6开头（.SH），5开头基金（.SH）
   - 深圳：0开头（.SZ），3开头创业板（.SZ）

## 扩展开发

如需添加更多数据源或字段：

1. 在 `TushareService` 中添加新的数据获取方法
2. 在对应 Agent 的 `_get_stock_data` 中调用新方法
3. 更新数据结构转换逻辑
4. 添加相应的单元测试

## 相关文件

- `app/services/tushare_service.py` - Tushare 数据服务
- `app/core/tushare_client.py` - Tushare 客户端封装
- `app/agents/base.py` - Agent 基类
- `app/agents/value/` - 价值投资 Agents
- `app/agents/growth/` - 成长投资 Agents
- `app/agents/macro/` - 宏观分析 Agents
