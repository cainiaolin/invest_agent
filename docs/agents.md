# 投资大师Agent文档

## Agent架构概览

Invest Agent By Graph 实现了6个著名投资大师的思维模式，分为三大投资风格类别：

```
投资大师Agent体系
├── 价值投资派 (Value)
│   ├── Warren Buffett (沃伦·巴菲特)
│   └── Benjamin Graham (本杰明·格雷厄姆)
├── 成长投资派 (Growth)
│   ├── Philip Fisher (菲利普·费雪)
│   └── Peter Lynch (彼得·林奇)
└── 宏观对冲派 (Macro)
    ├── George Soros (乔治·索罗斯)
    └── Ray Dalio (雷·达里奥)
```

## 价值投资派

### Warren Buffett (沃伦·巴菲特)

**核心理念**: 护城河、安全边际、长期持有

**投资哲学**:
- 寻找具有持续竞争优势的优质企业
- 关注企业的内在价值和安全边际
- 长期持有优秀企业的股票
- 在别人恐惧时贪婪，在别人贪婪时恐惧

**评估维度**:
1. **护城河强度** (Moat Strength: 25%)
   - 品牌价值 (9分制)
   - 市场份额 (百分比)
   - 竞争优势 (布尔值)

2. **财务健康度** (Financial Health: 25%)
   - ROE (净资产收益率)
   - 负债率 (越低越好)
   - 现金流状况

3. **估值安全边际** (Valuation Safety: 25%)
   - PE比率 (市盈率)
   - PB比率 (市净率)
   - 相对估值

4. **盈利质量** (Earnings Quality: 25%)
   - 股息率
   - 盈利增长稳定性
   - 再投资收益率

**决策逻辑**:
- 总分 > 80: 强烈买入 (buy, confidence > 0.8)
- 总分 70-80: 买入 (buy, confidence 0.7-0.8)
- 总分 60-70: 观望 (hold, confidence 0.6-0.7)
- 总分 < 60: 观望或卖出 (hold/sell, confidence < 0.6)

**典型案例**: 可口可乐、苹果公司、美国运通

### Benjamin Graham (本杰明·格雷厄姆)

**核心理念**: 价值投资之父、安全边际、深度价值

**投资哲学**:
- 市场短期是投票机，长期是称重机
- 严格的安全边际要求
- 关注资产负债表和现金流
- 逆向投资，寻找被低估的优质企业

**评估维度**:
1. **估值吸引力** (Value Appeal: 30%)
   - PE相对历史水平
   - PB相对历史水平
   - PS (市销率) 分析

2. **财务安全性** (Financial Safety: 30%)
   - 流动比率 (>2为优)
   - 负债率 (<50%为优)
   - 利息保障倍数

3. **资产质量** (Asset Quality: 20%)
   - 净资产收益率
   - 总资产周转率
   - 存货周转率

4. **盈利稳定性** (Earnings Stability: 20%)
   - 过去10年盈利增长稳定性
   - 股息连续性
   - 现金流稳定性

**决策逻辑**:
- 总分 > 75且安全边际 > 30%: 强烈买入
- 总分 65-75: 买入
- 总分 55-65: 观望
- 总分 < 55: 卖出

**典型案例**: GEICO、政府雇员保险公司

## 成长投资派

### Philip Fisher (菲利普·费雪)

**核心理念**: 成长股投资、 qualitative分析、长期持有

**投资哲学**:
- 关注企业的成长潜力和管理质量
- 重视定性分析而非定量分析
- 长期持有优秀成长企业
- "买进正确，长期持有"

**评估维度**:
1. **成长潜力** (Growth Potential: 30%)
   - 研发投入比例 (>5%为优)
   - 研发增长率
   - 市场份额增长率

2. **管理层素质** (Management Quality: 30%)
   - 管理层任期 (越长越稳定)
   - 管理层经验
   - 员工流失率 (低为优)
   - 员工满意度
   - 内部控制质量

3. **竞争优势** (Competitive Advantage: 25%)
   - 客户忠诚度
   - 销售团队质量
   - 产品差异化
   - 市场地位

4. **盈利增长** (Earnings Growth: 15%)
   - 收入增长率
   - 利润增长率
   - 盈利质量

**决策逻辑**:
- 总分 > 80: 优秀成长股，强烈买入
- 总分 70-80: 良好成长股，买入
- 总分 60-70: 一般成长股，谨慎买入
- 总分 < 60: 成长性不足，观望

**典型案例**: 摩托罗拉、德州仪器

### Peter Lynch (彼得·林奇)

**核心理念**: GARP策略、十倍股、投资你所了解的

**投资哲学**:
- 寻找合理价格增长股 (Growth At Reasonable Price)
- 投资于日常生活中了解的企业
- 分类投资策略 (缓慢增长型、稳定增长型等)
- 长期持有，忽略短期波动

**评估维度**:
1. **PEG比率** (PEG Ratio: 30%)
   - PEG = PE / 增长率
   - PEG < 1: 被低估
   - PEG 1-2: 合理
   - PEG > 2: 被高估

2. **收益增长** (Earnings Growth: 25%)
   - 收入增长率 (>15%为优)
   - 利润增长率
   - 增长稳定性

3. **相对强度** (Relative Strength: 20%)
   - 股价相对大盘表现
   - 行业地位
   - 市场份额

4. **资产负债** (Balance Sheet: 15%)
   - 负债率
   - 现金状况
   - 利息保障

5. **故事逻辑** (Story Logic: 10%)
   - 业务模式简单性
   - 护城河可持续性
   - 增长可信度

**决策逻辑**:
- 总分 > 75且PEG < 1.2: 十倍股潜力，强烈买入
- 总分 65-75: 良好GARP，买入
- 总分 55-65: 一般GARP，观望
- 总分 < 55: 不符合GARP标准

**典型案例**: Dunkin' Donuts、Taco Bell

## 宏观对冲派

### George Soros (乔治·索罗斯)

**核心理念**: 反身性理论、市场泡沫、宏观趋势

**投资哲学**:
- 市场参与者的偏见影响价格
- 寻找市场泡沫和拐点
- 宏观经济趋势分析
- 积极的交易策略

**评估维度**:
1. **宏观趋势** (Macro Trends: 30%)
   - 经济周期阶段
   - 货币政策环境
   - 财政政策环境

2. **市场情绪** (Market Sentiment: 25%)
   - 投资者情绪指标
   - 市场泡沫程度
   - 波动率水平

3. **反身性机会** (Reflexivity Opportunities: 25%)
   - 价格与基本面偏离程度
   - 自我强化趋势
   - 拐点信号

4. **风险收益比** (Risk-Reward Ratio: 20%)
   - 潜在上涨空间
   - 下行风险保护
   - 仓位管理

**决策逻辑**:
- 总分 > 75且反身性机会明显: 大胆买入
- 总分 65-75: 买入
- 总分 55-65: 观望
- 总分 < 55或泡沫明显: 卖空或回避

**典型案例**: 1992年做空英镑、亚洲金融危机

### Ray Dalio (雷·达里奥)

**核心理念**: 经济周期、全天候策略、债务周期

**投资哲学**:
- 理解经济机器的运作规律
- 通过分散化降低风险
- 重视债务周期和通货膨胀
- 构建全天候投资组合

**评估维度**:
1. **经济阶段** (Economic Phase: 30%)
   - 经济周期判断
   - 通胀/通缩环境
   - 增长/衰退阶段

2. **债务周期** (Debt Cycle: 25%)
   - 短期债务周期位置
   - 长期债务周期风险
   - 去杠杆化压力

3. **政策环境** (Policy Environment: 25%)
   - 货币政策宽松度
   - 财政政策方向
   - 监管环境变化

4. **资产配置** (Asset Allocation: 20%)
   - 股票相对吸引力
   - 债券相对吸引力
   - 另类投资机会

**决策逻辑**:
- 总分 > 75: 经济环境有利，增持股票
- 总分 65-75: 中性配置
- 总分 55-65: 谨慎配置
- 总分 < 55: 经济环境不利，减少股票配置

**典型案例**: 全天候基金 (All Weather Fund)

## Agent协作模式

### 1. 并行模式 (Parallel)
- **特点**: 所有Agent独立分析，无协作
- **输出**: 各Agent的独立分析结果
- **适用**: 快速获取多个投资视角

### 2. 投票模式 (Vote)
- **特点**: 所有Agent投票决策，多数获胜
- **输出**: 最终决策 + 共识度
- **适用**: 需要明确投资建议

### 3. 辩论模式 (Debate)
- **特点**: 3轮结构化辩论，深度讨论
- **输出**: 完整辩论记录 + 最终决策
- **适用**: 复杂投资决策，需要充分讨论

## Agent使用示例

```python
from app.graph.workflow import create_investment_workflow

# 创建工作流
workflow = create_investment_workflow()

# 执行分析
result = workflow.invoke({
    "stock_code": "600519",
    "mode": "vote",  # parallel/vote/debate
    "user_request": "分析贵州茅台的投资价值"
})

# 查看各Agent分析
for analysis in result['agent_analyses']:
    print(f"{analysis['agent_name']}: {analysis['action']}")
    print(f"  理由: {analysis['reasoning']}")
    print(f"  置信度: {analysis['confidence']:.1%}")
```

## Agent选择策略

系统根据用户输入的关键词自动选择Agent组合：

- **价值投资关键词**: "护城河"、"安全边际"、"内在价值"、"低估值"
  → 选择价值投资Agent (Buffett, Graham)

- **成长投资关键词**: "成长"、"增长"、"创新"、"市场份额"
  → 选择成长投资Agent (Fisher, Lynch)

- **宏观分析关键词**: "经济"、"政策"、"宏观"、"趋势"
  → 选择宏观对冲Agent (Soros, Dalio)

- **默认**: 所有6个Agent并行分析

## 扩展新Agent

要添加新的投资大师Agent：

1. 继承 `BaseAgent` 抽象基类
2. 实现必需的4个方法: `name`, `style`, `analyze`, `vote`, `debate`
3. 在相应的Agent类别文件夹中创建文件
4. 更新工作流节点以包含新Agent
5. 添加单元测试和集成测试

示例:
```python
from app.agents.base import BaseAgent

class MyInvestmentAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "My Investment Master"

    @property
    def style(self) -> str:
        return "My Investment Style"

    def analyze(self, stock_data: dict) -> dict:
        # 实现分析逻辑
        pass

    def vote(self, analysis: dict) -> str:
        # 实现投票逻辑
        pass

    def debate(self, context: dict) -> str:
        # 实现辩论逻辑
        pass
```

## Agent性能指标

### 分析准确性
- 历史决策准确率 (待回测验证)
- 不同市场环境下的表现
- 风险调整后收益

### 协作效果
- 多Agent共识度 vs 单Agent表现
- 辩论模式 vs 投票模式效果
- 不同Agent组合的互补性

### 计算效率
- 单次分析耗时
- 并行处理效率
- 内存使用情况

## 免责声明

所有Agent仅模拟投资大师的思维模式，不构成实际投资建议。投资有风险，入市需谨慎。历史表现不代表未来收益。

---

**文档版本**: v0.2.0-beta
**最后更新**: 2025-05-03
