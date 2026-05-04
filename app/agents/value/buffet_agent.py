"""巴菲特风格价值投资Agent"""
from app.agents.base import BaseAgent
from app.core.state import AnalysisState
import pandas as pd


class BuffetAgent(BaseAgent):
    """
    巴菲特风格的价值投资Agent

    投资理念:
    1. 护城河分析：品牌、网络效应、转换成本、成本优势
    2. 安全边际：以低于内在价值的价格买入
    3. 长期持有：持有优秀企业10年以上
    4. 能力圈：只投资自己理解的行业
    """

    def __init__(self, tushare_service):
        """
        初始化巴菲特Agent

        Args:
            tushare_service: Tushare数据服务实例
        """
        super().__init__(tushare_service)

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Warren Buffett"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "价值投资：关注企业护城河、安全边际和长期成长性"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于巴菲特理念分析股票

        评估维度:
        1. 护城河强度（品牌、市场份额、竞争优势）
        2. 财务健康度（ROE、负债率、现金流）
        3. 估值安全边际（PE、PB相对于增长）
        4. 盈利质量（盈利稳定性、ROIC）

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

        # 添加agent_name
        result["agent_name"] = self.name

        return result

    async def _get_stock_data(self, stock_code: str) -> dict:
        """
        从tushare获取股票数据

        Args:
            stock_code: 股票代码

        Returns:
            包含股票数据的字典
        """
        try:
            # 获取完整基本面数据
            fundamentals = await self.tushare.get_stock_fundamentals(stock_code)

            if not fundamentals:
                # 如果无法获取真实数据，返回空数据
                return {
                    "symbol": stock_code,
                    "name": f"股票{stock_code}",
                    "metrics": {},
                    "moat_indicators": {}
                }

            # 解析daily_basic数据
            daily_basic = fundamentals.get("daily_basic", pd.DataFrame())
            if not daily_basic.empty:
                latest = daily_basic.iloc[0]
                pe_ratio = latest.get("pe", 0)
                pb_ratio = latest.get("pb", 0)
                total_mv = latest.get("total_mv", 0)  # 总市值(万元)
            else:
                pe_ratio = 0
                pb_ratio = 0
                total_mv = 0

            # 解析利润表数据
            income = fundamentals.get("income", pd.DataFrame())
            if not income.empty:
                latest_income = income.iloc[0]
                basic_eps = latest_income.get("basic_eps", 0)  # 基本每股收益
                revenue = latest_income.get("total_revenue", 0)  # 营业收入
                operating_profit = latest_income.get("oper_profit", 0)  # 营业利润
            else:
                basic_eps = 0
                revenue = 0
                operating_profit = 0

            # 解析资产负债表数据
            balancesheet = fundamentals.get("balancesheet", pd.DataFrame())
            if not balancesheet.empty:
                latest_bs = balancesheet.iloc[0]
                total_assets = latest_bs.get("total_assets", 0)  # 总资产
                equity = latest_bs.get("equities_parent_comp", 0)  # 股东权益合计
                total_liab = latest_bs.get("total_liab", 0)  # 负债合计
                current_assets = latest_bs.get("current_assets", 0)  # 流动资产
                current_liab = latest_bs.get("current_liab", 0)  # 流动负债
            else:
                total_assets = 0
                equity = 0
                total_liab = 0
                current_assets = 0
                current_liab = 0

            # 解析现金流量表数据
            cashflow = fundamentals.get("cashflow", pd.DataFrame())
            if not cashflow.empty:
                latest_cf = cashflow.iloc[0]
                net_profit = latest_cf.get("net_profit", 0)  # 净利润
                operating_cash_flow = latest_cf.get("n_cashflow_act", 0)  # 经营活动现金流
            else:
                net_profit = 0
                operating_cash_flow = 0

            # 计算衍生指标
            roe = (net_profit / equity * 100) if equity > 0 else 0
            debt_ratio = (total_liab / total_assets * 100) if total_assets > 0 else 0
            current_ratio = (current_assets / current_liab) if current_liab > 0 else 0

            # 股息收益率 (简化计算，实际需要股息数据)
            dividend_yield = 0  # 需要额外的股息数据接口

            # 计算增长率（简化，需要同比数据）
            revenue_growth = 0  # 需要历史数据计算同比
            profit_growth = 0  # 需要历史数据计算同比

            return {
                "symbol": stock_code,
                "name": f"股票{stock_code}",
                "metrics": {
                    "pe_ratio": float(pe_ratio) if pe_ratio else 0,
                    "pb_ratio": float(pb_ratio) if pb_ratio else 0,
                    "roe": float(roe),
                    "debt_ratio": float(debt_ratio),
                    "current_ratio": float(current_ratio),
                    "dividend_yield": float(dividend_yield),
                    "revenue_growth": float(revenue_growth),
                    "profit_growth": float(profit_growth),
                    "total_mv": float(total_mv),
                    "net_profit": float(net_profit),
                    "operating_cash_flow": float(operating_cash_flow),
                },
                "moat_indicators": {
                    # 这些指标需要额外的数据源或分析模型
                    "brand_strength": 5,  # 默认中等
                    "market_share": 0,  # 需要行业数据
                    "competitive_advantage": None,  # 需要分析模型
                }
            }

        except Exception as e:
            print(f"获取股票 {stock_code} 数据失败: {e}")
            # 返回空数据
            return {
                "symbol": stock_code,
                "name": f"股票{stock_code}",
                "metrics": {},
                "moat_indicators": {}
            }

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        metrics = stock_data.get("metrics", {})
        moat_indicators = stock_data.get("moat_indicators", {})

        # 提取关键指标
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        roe = metrics.get("roe", 0)
        debt_ratio = metrics.get("debt_ratio", 100)
        current_ratio = metrics.get("current_ratio", 1.0)
        dividend_yield = metrics.get("dividend_yield", 0)
        revenue_growth = metrics.get("revenue_growth", 0)
        profit_growth = metrics.get("profit_growth", 0)

        # 护城河指标
        brand_strength = moat_indicators.get("brand_strength", 5)
        market_share = moat_indicators.get("market_share", 0)
        has_advantage = moat_indicators.get("competitive_advantage", False)

        # 评分系统 (0-100)
        scores = {
            "moat": self._evaluate_moat(brand_strength, market_share, has_advantage),
            "financial_health": self._evaluate_financial_health(roe, debt_ratio, current_ratio),
            "valuation": self._evaluate_valuation(pe_ratio, pb_ratio, revenue_growth, profit_growth),
            "quality": self._evaluate_quality(dividend_yield, roe, revenue_growth),
        }

        # 计算总分
        total_score = sum(scores.values()) / len(scores)

        # 计算置信度
        confidence = min(total_score / 100, 1.0)

        # 做出决策
        action = self._make_decision(total_score, scores)

        # 生成理由和关键因素
        reasoning = self._generate_reasoning(action, scores, stock_data)
        key_factors = self._extract_key_factors(scores, stock_data)

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_metrics": {"scores": scores},
            "total_score": total_score,
        }
        metrics = stock_data.get("metrics", {})
        moat_indicators = stock_data.get("moat_indicators", {})

        # 提取关键指标
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        roe = metrics.get("roe", 0)
        debt_ratio = metrics.get("debt_ratio", 100)
        current_ratio = metrics.get("current_ratio", 1.0)
        dividend_yield = metrics.get("dividend_yield", 0)
        revenue_growth = metrics.get("revenue_growth", 0)
        profit_growth = metrics.get("profit_growth", 0)

        # 护城河指标
        brand_strength = moat_indicators.get("brand_strength", 5)
        market_share = moat_indicators.get("market_share", 0)
        has_advantage = moat_indicators.get("competitive_advantage", False)

        # 评分系统 (0-100)
        scores = {
            "moat": self._evaluate_moat(brand_strength, market_share, has_advantage),
            "financial_health": self._evaluate_financial_health(roe, debt_ratio, current_ratio),
            "valuation": self._evaluate_valuation(pe_ratio, pb_ratio, revenue_growth, profit_growth),
            "quality": self._evaluate_quality(dividend_yield, roe, revenue_growth),
        }

        # 计算总分
        total_score = sum(scores.values()) / len(scores)

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

    def _evaluate_moat(self, brand_strength: int, market_share: float, has_advantage: bool) -> float:
        """评估护城河强度 (0-100)"""
        score = 50  # 基础分

        # 品牌强度 (1-10)
        score += (brand_strength - 5) * 5

        # 市场份额
        if market_share > 30:
            score += 20
        elif market_share > 15:
            score += 10
        elif market_share > 5:
            score += 5

        # 竞争优势
        if has_advantage:
            score += 15

        return max(0, min(100, score))

    def _evaluate_financial_health(self, roe: float, debt_ratio: float, current_ratio: float) -> float:
        """评估财务健康度 (0-100)"""
        score = 50  # 基础分

        # ROE评估
        if roe > 20:
            score += 20
        elif roe > 15:
            score += 15
        elif roe > 10:
            score += 10
        elif roe > 5:
            score += 5

        # 负债率评估（越低越好）
        if debt_ratio < 30:
            score += 20
        elif debt_ratio < 50:
            score += 15
        elif debt_ratio < 70:
            score += 5

        # 流动比率
        if current_ratio > 2:
            score += 10
        elif current_ratio > 1.5:
            score += 5

        return max(0, min(100, score))

    def _evaluate_valuation(self, pe: float, pb: float, revenue_growth: float, profit_growth: float) -> float:
        """评估估值安全边际 (0-100)"""
        score = 50  # 基础分

        # PE评估（考虑增长率）
        peg_ratio = pe / (profit_growth + 1) if profit_growth > 0 else pe
        if peg_ratio < 1:
            score += 25
        elif peg_ratio < 1.5:
            score += 15
        elif peg_ratio < 2:
            score += 5
        elif peg_ratio > 3:
            score -= 20

        # PB评估
        if pb < 1:
            score += 20
        elif pb < 1.5:
            score += 15
        elif pb < 3:
            score += 5
        elif pb > 5:
            score -= 15

        return max(0, min(100, score))

    def _evaluate_quality(self, dividend_yield: float, roe: float, revenue_growth: float) -> float:
        """评估盈利质量 (0-100)"""
        score = 50  # 基础分

        # 股息收益率
        if dividend_yield > 4:
            score += 15
        elif dividend_yield > 2:
            score += 10
        elif dividend_yield > 0:
            score += 5

        # 增长稳定性
        if revenue_growth > 15 and revenue_growth < 50:  # 避免过热
            score += 15
        elif revenue_growth > 10:
            score += 10
        elif revenue_growth > 5:
            score += 5
        elif revenue_growth < 0:
            score -= 20

        # ROE质量
        if roe > 15:
            score += 20
        elif roe > 10:
            score += 10

        return max(0, min(100, score))

    def _make_decision(self, total_score: float, scores: dict) -> str:
        """基于评分做出决策"""
        # 护城河和财务健康是必要条件
        if scores["moat"] < 40 or scores["financial_health"] < 40:
            return "sell"

        # 估值和质量的综合判断
        if total_score >= 75:
            return "buy"
        elif total_score >= 60:
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

        # 护城河评价
        moat_score = scores["moat"]
        if moat_score >= 70:
            reasoning_parts.append("公司具有强大的护城河和竞争优势。")
        elif moat_score >= 50:
            reasoning_parts.append("公司护城河一般。")
        else:
            reasoning_parts.append("公司缺乏足够的护城河保护。")

        # 财务健康度
        health_score = scores["financial_health"]
        if health_score >= 70:
            reasoning_parts.append("财务状况健康。")
        elif health_score < 40:
            reasoning_parts.append("财务状况存在风险。")

        # 估值评价
        valuation_score = scores["valuation"]
        if valuation_score >= 70:
            reasoning_parts.append("当前估值提供了良好的安全边际。")
        elif valuation_score < 40:
            reasoning_parts.append("估值过高，缺乏安全边际。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(self, scores: dict, stock_data: dict) -> list:
        """提取关键投资因素"""
        factors = []

        # 根据评分提取关键因素
        if scores["moat"] >= 70:
            factors.append("强大护城河")
        elif scores["moat"] < 40:
            factors.append("护城河薄弱")

        if scores["financial_health"] >= 70:
            factors.append("财务健康")
        elif scores["financial_health"] < 40:
            factors.append("财务风险")

        if scores["valuation"] >= 70:
            factors.append("估值合理")
        elif scores["valuation"] < 40:
            factors.append("估值过高")

        if scores["quality"] >= 70:
            factors.append("盈利质量高")

        # 添加具体的财务指标
        metrics = stock_data.get("metrics", {})
        if metrics.get("roe", 0) > 15:
            factors.append(f"高ROE({metrics['roe']:.1f}%)")
        if metrics.get("debt_ratio", 100) < 30:
            factors.append("低负债")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        巴菲特风格：
        - 高置信度(>0.7)的买入分析 → buy
        - 高置信度(>0.7)的卖出分析 → sell
        - 其他情况 → hold（等待更好的机会）

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        action = analysis.get("action", "hold")
        confidence = analysis.get("confidence", 0.5)

        # 只有高置信度时才跟随分析决策
        if confidence > 0.7:
            return action

        # 低置信度时倾向于保守（hold）
        return "hold"

    async def debate(self, message: dict) -> dict:
        """
        参与投资辩论

        巴菲特会强调：
        1. 时间是优秀企业的朋友
        2. 护城河的重要性
        3. 在别人贪婪时恐惧，在别人恐惧时贪婪
        4. 以合理的价格购买优秀的企业

        Args:
            message: 辩论消息，包含round、content等信息

        Returns:
            巴菲特风格的观点回应
        """
        round_num = message.get("round", 0)

        # 根据轮次生成不同的观点
        if round_num == 1:
            content = (
                "我关注三个核心问题："
                "1. 这家企业是否有持久的护城河？"
                "2. 财务状况是否健康？"
                "3. 当前价格是否提供了安全边际？"
            )
        elif round_num == 2:
            content = (
                "在投资时，时间是优秀企业的朋友。"
                "如果这是一家有护城河的优质企业，我们应该长期持有。"
            )
        else:
            content = (
                "记住：在别人贪婪时恐惧，在别人恐惧时贪婪。"
                "安全边际是投资成功的关键。"
            )

        return {
            "agent_name": self.name,
            "content": content,
            "round": round_num
        }
