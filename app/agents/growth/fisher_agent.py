"""Philip Fisher成长投资Agent"""
from app.agents.base import BaseAgent
from app.core.state import AnalysisState


class FisherAgent(BaseAgent):
    """
    Philip Fisher风格的成长投资Agent

    投资理念:
    1. 闲话法调研：深入了解公司管理层、员工、客户、竞争对手
    2. 长期成长：关注具有持续成长潜力的优质企业
    3. 质量优先：选择管理卓越、有竞争优势的公司
    4. 集中投资：重仓最了解的少数优质股票

    Fisher的8个投资标准：
    1. 持续的盈利增长能力
    2. 管理层对成长的承诺
    3. 高水平的股东权益回报率
    4. 有效的成本控制
    5. 持续的研发投入
    6. 强大的销售组织
    7. 良好的员工关系
    8. 严格的内部控制
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Philip Fisher"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "成长投资：关注企业质量、长期成长潜力和管理层能力"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于Fisher理念分析股票

        评估维度（Fisher的8个标准）：
        1. 盈利持续性：过去和未来的盈利增长
        2. 管理层质量：对成长的承诺和执行能力
        3. 股东回报：ROE和资本配置效率
        4. 成本控制：运营效率和利润率改善
        5. 研发投入：创新能力和未来竞争力
        6. 销售组织：市场开拓和客户保持能力
        7. 员工关系：人才保留和激励机制
        8. 内部控制：风险管理和合规能力

        Args:
            state: 分析状态，包含股票代码等信息

        Returns:
            包含action、confidence、reasoning、key_metrics的字典
        """
        stock_code = state.get("stock_code", "")

        # 获取股票数据（模拟数据，实际应从tushare获取）
        stock_data = await self._get_stock_data(stock_code)

        # 调用原有的分析逻辑
        result = self._analyze_stock_data(stock_data)

        # 添加agent_name并统一返回格式
        result["agent_name"] = self.name
        if "decision" in result and "action" not in result:
            result["action"] = result.pop("decision")
        if "key_factors" in result and "key_metrics" not in result:
            result["key_metrics"] = {"key_factors": result.pop("key_factors")}

        return result

    async def _get_stock_data(self, stock_code: str) -> dict:
        """获取股票数据"""
        import random
        random.seed(hash(stock_code) % 10000)

        return {
            "symbol": stock_code,
            "name": f"股票{stock_code}",
            "metrics": {
                "pe_ratio": round(random.uniform(8, 40), 2),
                "pb_ratio": round(random.uniform(1, 8), 2),
                "roe": round(random.uniform(5, 30), 2),
                "debt_ratio": round(random.uniform(20, 70), 2),
                "revenue_growth": round(random.uniform(-5, 35), 2),
                "profit_growth": round(random.uniform(-10, 40), 2),
                "operating_margin": round(random.uniform(3, 35), 2),
                "net_margin": round(random.uniform(2, 25), 2),
            },
            "growth_indicators": {
                "rd_ratio": round(random.uniform(0.5, 12), 2),
                "rd_growth": round(random.uniform(-5, 25), 2),
                "market_share_growth": round(random.uniform(-3, 8), 2),
                "customer_satisfaction": random.randint(3, 10),
                "sales_force_quality": random.randint(3, 10),
            },
            "management_quality": {
                "management_tenure": round(random.uniform(1, 15), 2),
                "management_experience": random.randint(2, 10),
                "employee_turnover": round(random.uniform(3, 30), 2),
                "employee_satisfaction": random.randint(3, 10),
                "internal_control_quality": random.randint(3, 10),
            },
        }

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        metrics = stock_data.get("metrics", {})
        growth_indicators = stock_data.get("growth_indicators", {})
        management_quality = stock_data.get("management_quality", {})

        # 提取关键指标
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        roe = metrics.get("roe", 0)
        debt_ratio = metrics.get("debt_ratio", 100)
        revenue_growth = metrics.get("revenue_growth", 0)
        profit_growth = metrics.get("profit_growth", 0)
        operating_margin = metrics.get("operating_margin", 0)
        net_margin = metrics.get("net_margin", 0)

        # 成长性指标
        rd_ratio = growth_indicators.get("rd_ratio", 0)  # 研发费用率
        rd_growth = growth_indicators.get("rd_growth", 0)  # 研发增长率
        market_share_growth = growth_indicators.get("market_share_growth", 0)
        customer_satisfaction = growth_indicators.get("customer_satisfaction", 5)
        sales_force_quality = growth_indicators.get("sales_force_quality", 5)

        # 管理层质量指标
        management_tenure = management_quality.get("management_tenure", 0)
        management_experience = management_quality.get("management_experience", 5)
        employee_turnover = management_quality.get("employee_turnover", 20)
        employee_satisfaction = management_quality.get("employee_satisfaction", 5)
        internal_control_quality = management_quality.get("internal_control_quality", 5)

        # Fisher的8个标准评分 (0-100)
        scores = {
            "earnings_persistence": self._evaluate_earnings_persistence(
                revenue_growth, profit_growth, roe
            ),
            "growth_commitment": self._evaluate_growth_commitment(
                management_tenure, management_experience, profit_growth
            ),
            "shareholder_returns": self._evaluate_shareholder_returns(
                roe, debt_ratio, profit_growth
            ),
            "cost_control": self._evaluate_cost_control(
                operating_margin, net_margin, revenue_growth
            ),
            "rd_investment": self._evaluate_rd_investment(
                rd_ratio, rd_growth, revenue_growth
            ),
            "sales_organization": self._evaluate_sales_organization(
                sales_force_quality, market_share_growth, customer_satisfaction
            ),
            "employee_relations": self._evaluate_employee_relations(
                employee_satisfaction, employee_turnover
            ),
            "internal_controls": self._evaluate_internal_controls(
                internal_control_quality, debt_ratio
            ),
        }

        # 计算总分（Fisher强调所有8个标准都要满足）
        # 如果任何一个关键维度得分过低，总分会受到惩罚
        min_score = min(scores.values())
        avg_score = sum(scores.values()) / len(scores)

        # Fisher认为所有标准都很重要，所以使用加权平均
        # 如果最低分太低，总分会显著降低
        if min_score < 40:
            total_score = avg_score * 0.6  # 严重惩罚
        elif min_score < 60:
            total_score = avg_score * 0.8  # 轻微惩罚
        else:
            total_score = avg_score

        # 计算置信度
        confidence = min(total_score / 100, 1.0)

        # 做出决策
        decision = self._make_decision(total_score, scores)

        # 生成理由和关键因素
        reasoning = self._generate_reasoning(decision, scores, stock_data)
        key_factors = self._extract_key_factors(scores, stock_data)

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "scores": scores,
            "total_score": total_score,
        }

    def _evaluate_earnings_persistence(
        self, revenue_growth: float, profit_growth: float, roe: float
    ) -> float:
        """评估盈利持续性 (0-100)"""
        score = 50  # 基础分

        # 盈利增长评估
        if profit_growth > 20:
            score += 25
        elif profit_growth > 15:
            score += 20
        elif profit_growth > 10:
            score += 15
        elif profit_growth > 5:
            score += 10
        elif profit_growth < 0:
            score -= 30

        # 收入增长评估
        if revenue_growth > 15:
            score += 15
        elif revenue_growth > 10:
            score += 10
        elif revenue_growth > 5:
            score += 5
        elif revenue_growth < 0:
            score -= 20

        # ROE评估（Fisher重视高ROE）
        if roe > 20:
            score += 10
        elif roe > 15:
            score += 5
        elif roe < 8:
            score -= 10

        return max(0, min(100, score))

    def _evaluate_growth_commitment(
        self, management_tenure: float, management_experience: int, profit_growth: float
    ) -> float:
        """评估管理层对成长的承诺 (0-100)"""
        score = 50  # 基础分

        # 管理层任期（长期任职意味着承诺）
        if management_tenure > 10:
            score += 20
        elif management_tenure > 5:
            score += 15
        elif management_tenure > 3:
            score += 10

        # 管理层经验
        if management_experience >= 8:
            score += 15
        elif management_experience >= 5:
            score += 10
        elif management_experience >= 3:
            score += 5

        # 实际增长表现验证承诺
        if profit_growth > 15:
            score += 15
        elif profit_growth > 10:
            score += 10
        elif profit_growth < 5:
            score -= 15

        return max(0, min(100, score))

    def _evaluate_shareholder_returns(
        self, roe: float, debt_ratio: float, profit_growth: float
    ) -> float:
        """评估股东回报 (0-100)"""
        score = 50  # 基础分

        # ROE是Fisher最看重的指标之一
        if roe > 25:
            score += 30
        elif roe > 20:
            score += 25
        elif roe > 15:
            score += 15
        elif roe > 10:
            score += 5
        elif roe < 5:
            score -= 20

        # 增长与ROE的结合（Fisher寻找高增长+高ROE）
        if roe > 15 and profit_growth > 15:
            score += 20  # 额外奖励
        elif roe > 10 and profit_growth > 10:
            score += 10

        # 负债水平（适度负债可以提升ROE）
        if debt_ratio < 30:
            score += 10
        elif debt_ratio < 50:
            score += 5
        elif debt_ratio > 70:
            score -= 15

        return max(0, min(100, score))

    def _evaluate_cost_control(
        self, operating_margin: float, net_margin: float, revenue_growth: float
    ) -> float:
        """评估成本控制能力 (0-100)"""
        score = 50  # 基础分

        # 运营利润率
        if operating_margin > 25:
            score += 25
        elif operating_margin > 20:
            score += 20
        elif operating_margin > 15:
            score += 15
        elif operating_margin > 10:
            score += 5
        elif operating_margin < 5:
            score -= 15

        # 净利润率
        if net_margin > 20:
            score += 15
        elif net_margin > 15:
            score += 10
        elif net_margin > 10:
            score += 5
        elif net_margin < 3:
            score -= 10

        # 收入增长下的利润率保持（体现成本控制）
        if revenue_growth > 10 and operating_margin > 15:
            score += 10  # 增长同时保持利润率

        return max(0, min(100, score))

    def _evaluate_rd_investment(
        self, rd_ratio: float, rd_growth: float, revenue_growth: float
    ) -> float:
        """评估研发投入 (0-100)"""
        score = 50  # 基础分

        # 研发费用率（Fisher重视创新）
        if rd_ratio > 10:
            score += 25
        elif rd_ratio > 7:
            score += 20
        elif rd_ratio > 5:
            score += 15
        elif rd_ratio > 3:
            score += 10
        elif rd_ratio < 1:
            score -= 15

        # 研发增长率（持续投入）
        if rd_growth > 15:
            score += 15
        elif rd_growth > 10:
            score += 10
        elif rd_growth > 5:
            score += 5
        elif rd_growth < 0:
            score -= 10

        # 研发投入转化为增长
        if rd_ratio > 5 and revenue_growth > 10:
            score += 10  # 研发投入有效转化为增长

        return max(0, min(100, score))

    def _evaluate_sales_organization(
        self,
        sales_force_quality: int,
        market_share_growth: float,
        customer_satisfaction: int,
    ) -> float:
        """评估销售组织 (0-100)"""
        score = 50  # 基础分

        # 销售团队质量（1-10评分）
        if sales_force_quality >= 8:
            score += 25
        elif sales_force_quality >= 6:
            score += 15
        elif sales_force_quality >= 4:
            score += 5
        elif sales_force_quality < 3:
            score -= 15

        # 市场份额增长
        if market_share_growth > 5:
            score += 15
        elif market_share_growth > 3:
            score += 10
        elif market_share_growth > 1:
            score += 5
        elif market_share_growth < -2:
            score -= 10

        # 客户满意度（1-10评分）
        if customer_satisfaction >= 8:
            score += 10
        elif customer_satisfaction >= 6:
            score += 5
        elif customer_satisfaction < 4:
            score -= 10

        return max(0, min(100, score))

    def _evaluate_employee_relations(
        self, employee_satisfaction: int, employee_turnover: float
    ) -> float:
        """评估员工关系 (0-100)"""
        score = 50  # 基础分

        # 员工满意度（1-10评分）
        if employee_satisfaction >= 8:
            score += 30
        elif employee_satisfaction >= 6:
            score += 15
        elif employee_satisfaction >= 4:
            score += 5
        elif employee_satisfaction < 3:
            score -= 20

        # 员工流失率
        if employee_turnover < 5:
            score += 20
        elif employee_turnover < 10:
            score += 15
        elif employee_turnover < 15:
            score += 5
        elif employee_turnover > 25:
            score -= 15

        return max(0, min(100, score))

    def _evaluate_internal_controls(
        self, internal_control_quality: int, debt_ratio: float
    ) -> float:
        """评估内部控制 (0-100)"""
        score = 50  # 基础分

        # 内控质量（1-10评分）
        if internal_control_quality >= 8:
            score += 30
        elif internal_control_quality >= 6:
            score += 15
        elif internal_control_quality >= 4:
            score += 5
        elif internal_control_quality < 3:
            score -= 25

        # 负债控制（合理的财务杠杆）
        if debt_ratio < 40:
            score += 20
        elif debt_ratio < 60:
            score += 10
        elif debt_ratio > 80:
            score -= 15

        return max(0, min(100, score))

    def _make_decision(self, total_score: float, scores: dict) -> str:
        """基于评分做出决策"""
        # Fisher要求所有8个标准都要达到一定水平
        min_score = min(scores.values())

        # 如果任何关键维度得分过低，回避
        if min_score < 30:
            return "sell"

        # Fisher寻找的是全面优秀的公司
        if total_score >= 75 and min_score >= 60:
            return "buy"
        elif total_score >= 65 and min_score >= 50:
            return "hold"
        else:
            return "sell"

    def _generate_reasoning(self, decision: str, scores: dict, stock_data: dict) -> str:
        """生成投资理由"""
        symbol = stock_data.get("symbol", "")
        name = stock_data.get("name", "")

        reasoning_parts = []

        # 决策说明
        if decision == "buy":
            reasoning_parts.append(f"建议{name}({symbol})买入。")
        elif decision == "hold":
            reasoning_parts.append(f"建议{name}({symbol})持有观望。")
        else:
            reasoning_parts.append(f"建议{name}({symbol})卖出或回避。")

        # Fisher的核心理念阐述
        if decision == "buy":
            reasoning_parts.append(
                "该公司在Fisher的8个投资标准上表现优异，"
                "具备长期成长潜力。"
            )
            # 找出最强的维度
            max_score_dim = max(scores, key=scores.get)
            if scores[max_score_dim] >= 80:
                dimension_names = {
                    "earnings_persistence": "盈利持续性",
                    "growth_commitment": "成长承诺",
                    "shareholder_returns": "股东回报",
                    "cost_control": "成本控制",
                    "rd_investment": "研发投入",
                    "sales_organization": "销售组织",
                    "employee_relations": "员工关系",
                    "internal_controls": "内部控制",
                }
                reasoning_parts.append(f"特别在{dimension_names[max_score_dim]}方面表现突出。")

        elif decision == "sell":
            # 找出最弱的维度
            min_score_dim = min(scores, key=scores.get)
            if scores[min_score_dim] < 50:
                dimension_names = {
                    "earnings_persistence": "盈利持续性",
                    "growth_commitment": "成长承诺",
                    "shareholder_returns": "股东回报",
                    "cost_control": "成本控制",
                    "rd_investment": "研发投入",
                    "sales_organization": "销售组织",
                    "employee_relations": "员工关系",
                    "internal_controls": "内部控制",
                }
                reasoning_parts.append(f"公司在{dimension_names[min_score_dim]}方面存在不足。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(self, scores: dict, stock_data: dict) -> list:
        """提取关键投资因素"""
        factors = []

        dimension_names = {
            "earnings_persistence": "盈利持续增长",
            "growth_commitment": "管理层承诺",
            "shareholder_returns": "高股东回报",
            "cost_control": "成本控制优秀",
            "rd_investment": "持续研发投入",
            "sales_organization": "销售能力强",
            "employee_relations": "员工关系良好",
            "internal_controls": "内控严格",
        }

        # 提取得分高的维度
        for dim, score in scores.items():
            if score >= 70:
                factors.append(dimension_names[dim])
            elif score < 40:
                factors.append(f"缺乏{dimension_names[dim]}")

        # 添加具体的财务指标
        metrics = stock_data.get("metrics", {})
        if metrics.get("roe", 0) > 20:
            factors.append(f"超高ROE({metrics['roe']:.1f}%)")

        growth_indicators = stock_data.get("growth_indicators", {})
        if growth_indicators.get("rd_ratio", 0) > 8:
            factors.append("高研发投入")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        Fisher风格：
        - 高置信度(>0.75)的买入分析 → buy
        - 高置信度(>0.75)的卖出分析 → sell
        - 其他情况 → hold（Fisher强调长期持有，不轻易交易）

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        decision = analysis.get("decision", "hold")
        confidence = analysis.get("confidence", 0.5)

        # Fisher只在非常确信时才采取行动
        if confidence > 0.75:
            return decision

        # 其他情况倾向于长期持有
        return "hold"

    def debate(self, context: dict) -> str:
        """
        参与投资辩论

        Fisher会强调：
        1. 闲话法调研的重要性
        2. 长期成长的持续性
        3. 管理层质量是关键
        4. 质量比价格更重要
        5. 集中投资于最了解的公司

        Args:
            context: 包含股票信息、市场情绪、其他观点的字典

        Returns:
            Fisher风格的观点陈述
        """
        stock = context.get("stock", {})
        stock_name = stock.get("name", "该公司")
        market_sentiment = context.get("market_sentiment", "neutral")

        # Fisher的核心观点
        if market_sentiment == "bullish":
            return (
                f"关于{stock_name}，在市场乐观时我们更要关注公司的基本面质量。"
                "价格合理与否固然重要，但公司的长期成长潜力更为关键。"
                "我建议深入了解公司的管理层、竞争对手、客户和员工，"
                "这比短期价格波动更能揭示投资价值。记住：优质公司值得长期持有。"
            )
        elif market_sentiment == "bearish":
            return (
                f"关于{stock_name}，市场下跌可能为长期投资者提供机会。"
                "如果这是一家管理层卓越、具有持续成长能力的优质公司，"
                "当前的价格下跌反而是买入时机。关键是确认公司的基本面是否依然稳健，"
                "管理层是否依然专注于长期发展。"
            )
        else:
            return (
                f"关于{stock_name}，我关注的是公司的长期成长质量。"
                "我们需要问：管理层是否有能力和远见？"
                "公司是否持续投资于未来（研发、市场、人才）？"
                "是否有真正的竞争优势和客户忠诚度？"
                "如果这些答案都是肯定的，这就是一个值得长期投资的机会。"
            )
