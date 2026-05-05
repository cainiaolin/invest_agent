"""本杰明·格雷厄姆风格深度价值投资Agent"""
import math
import logging
import pandas as pd
import asyncio
from app.agents.base import BaseAgent
from app.core.state import AnalysisState
from app.services.exceptions import (
    TushareAPIError,
    TushareDataNotFoundError,
    MissingCriticalDataError,
    TusharePermissionError
)
from app.services.data_validator import DataValidator

logger = logging.getLogger(__name__)


class GrahamAgent(BaseAgent):
    """
    本杰明·格雷厄姆风格的深度价值投资Agent

    投资理念:
    1. Graham公式计算内在价值: √(22.5 × EPS × BVPS)
    2. 净净分析(Net-Net): 价格低于净净营运资本
    3. 盈利收益率: 要求>2倍AAA债券收益率
    4. 安全边际: 强调下行保护和风险控制
    5. 深度价值: 寻找市场错误定价的优质资产
    """

    # Graham公式常数
    GRAHAM_CONSTANT = 22.5

    # 默认AAA债券收益率（当未提供时）
    DEFAULT_AAA_BOND_YIELD = 3.0

    def __init__(self, tushare_service):
        """
        初始化格雷厄姆Agent

        Args:
            tushare_service: Tushare数据服务实例
        """
        super().__init__(tushare_service)

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Benjamin Graham"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "深度价值投资：关注安全边际、内在价值和下行保护"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于格雷厄姆理念分析股票

        评估维度:
        1. Graham公式估值：内在价值vs市场价格
        2. 安全边际：价格低于内在价值的程度
        3. 净净分析：价格是否低于净净营运资本
        4. 盈利收益率：是否超过2倍AAA债券收益率
        5. 财务安全性：负债率和流动性

        Args:
            state: 分析状态，包含股票代码等信息

        Returns:
            包含action、confidence、reasoning、key_metrics的字典
        """
        stock_code = state.get("stock_code", "")

        try:
            # 获取并验证股票数据
            stock_data = await self._get_validated_stock_data(stock_code)

            # 执行分析
            result = self._analyze_stock_data(stock_data)
            result["agent_name"] = self.name

            # 统一返回格式
            if "decision" in result and "action" not in result:
                result["action"] = result.pop("decision")
            if "key_factors" in result and "key_metrics" not in result:
                result["key_metrics"] = {"key_factors": result.pop("key_factors")}

            return result

        except TusharePermissionError as e:
            logger.error(f"Tushare权限不足: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"数据权限不足，无法进行分析。请检查Tushare积分是否达到{e.required_points}积分要求。",
                "error_type": "permission_error",
                "agent_name": self.name
            }

        except TushareDataNotFoundError as e:
            logger.warning(f"股票数据不存在: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"无法找到股票数据：{e.message}",
                "error_type": "data_not_found",
                "agent_name": self.name
            }

        except MissingCriticalDataError as e:
            logger.warning(f"关键数据缺失: {e}")
            missing = ", ".join(e.missing_fields)
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"缺少关键数据({missing})，无法进行格雷厄姆分析。格雷厄姆方法需要准确的财务数据来计算内在价值和安全边际。",
                "error_type": "missing_critical_data",
                "missing_fields": e.missing_fields,
                "agent_name": self.name
            }

        except TushareAPIError as e:
            logger.error(f"API调用失败: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"数据获取失败：{e.message}",
                "error_type": "api_error",
                "agent_name": self.name
            }

        except Exception as e:
            logger.error(f"分析失败: {e}", exc_info=True)
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"分析过程中发生错误：{str(e)}",
                "error_type": "unknown_error",
                "agent_name": self.name
            }

    async def _get_validated_stock_data(self, stock_code: str) -> dict:
        """
        获取并验证股票数据

        Args:
            stock_code: 股票代码

        Returns:
            验证通过的股票数据

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
            MissingCriticalDataError: 关键数据缺失
        """
        # 获取完整基本面数据
        fundamentals = await self.tushare.get_stock_fundamentals(stock_code)

        # 获取日线数据（用于获取价格）
        loop = asyncio.get_event_loop()
        formatted_code = self.tushare._format_stock_code(stock_code)

        daily_df = await loop.run_in_executor(
            None,
            lambda: self.tushare.api.daily(
                ts_code=formatted_code,
                start_date="20200101",
                end_date=""
            )
        )

        price = float(daily_df.iloc[0]["close"]) if not daily_df.empty else 0.0

        # 解析daily_basic数据（可选）
        daily_basic = fundamentals.get("daily_basic", pd.DataFrame())
        if not daily_basic.empty:
            latest = daily_basic.iloc[0]
            pe_ratio = float(latest.get("pe", 0) or 0)
            pb_ratio = float(latest.get("pb", 0) or 0)
        else:
            pe_ratio = 0.0
            pb_ratio = 0.0

        # 解析利润表数据
        income = fundamentals["income"]
        latest_income = income.iloc[0]
        basic_eps = float(latest_income.get("basic_eps", 0) or 0)
        total_revenue = float(latest_income.get("total_revenue", 0) or 0)
        oper_cost = float(latest_income.get("oper_cost", 0) or 0)

        # 解析资产负债表数据
        balancesheet = fundamentals["balancesheet"]
        latest_bs = balancesheet.iloc[0]
        total_assets = float(latest_bs.get("total_assets", 0) or 0)
        equity = float(latest_bs.get("total_hldr_eqy_exc_min_int", 0) or 0)
        total_liab = float(latest_bs.get("total_liab", 0) or 0)
        current_assets = float(latest_bs.get("total_cur_assets", 0) or 0)
        current_liab = float(latest_bs.get("total_cur_liab", 0) or 0)

        # 解析现金流量表数据
        cashflow = fundamentals["cashflow"]
        latest_cf = cashflow.iloc[0]
        net_profit_cf = float(latest_cf.get("net_profit", 0) or 0)
        operating_cash_flow = float(latest_cf.get("n_cashflow_act", 0) or 0)

        # 解析财务指标（fina_indicator提供预计算的ROE、利润率等）
        fina = fundamentals["fina_indicator"]
        latest_fina = fina.iloc[0]
        roe = float(latest_fina.get("roe", 0) or 0)
        gross_margin = float(latest_fina.get("grossprofit_margin", 0) or 0)
        net_margin = float(latest_fina.get("netprofit_margin", 0) or 0)
        fina_current_ratio = float(latest_fina.get("current_ratio", 0) or 0)
        debt_to_assets = float(latest_fina.get("debt_to_assets", 0) or 0)
        revenue_growth = float(latest_fina.get("rev_yoy", 0) or 0)
        profit_growth = float(latest_fina.get("netprofit_yoy", 0) or 0)

        # 衍生指标：优先用fina_indicator，回退到手动计算
        debt_ratio = debt_to_assets if debt_to_assets > 0 else (total_liab / total_assets * 100 if total_assets > 0 else 0)
        current_ratio = fina_current_ratio if fina_current_ratio > 0 else (current_assets / current_liab if current_liab > 0 else 0)

        # 计算BVPS (每股净资产)
        bvps = (equity / 100000000) if equity > 0 else 0

        # 计算净净营运资本 (Net-Net Working Capital)
        net_net_working_capital = (current_assets - total_liab) / 100000000

        # 构建metrics字典
        metrics = {
            "eps": basic_eps,
            "bvps": bvps,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "roe": roe,
            "debt_ratio": debt_ratio,
            "current_ratio": current_ratio,
            "gross_margin": gross_margin,
            "net_margin": net_margin,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
        }

        # 数据质量验证
        stock_data_temp = {
            "symbol": stock_code,
            "name": f"股票{stock_code}",
            "price": price,
            "metrics": metrics
        }

        validation_result = DataValidator.validate_stock_data(
            stock_data_temp,
            agent_name=self.name,
            strict_mode=True
        )

        stock_data_temp["data_quality"] = validation_result
        stock_data_temp["net_net_working_capital"] = net_net_working_capital
        stock_data_temp["aaa_bond_yield"] = self.DEFAULT_AAA_BOND_YIELD

        return stock_data_temp

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        metrics = stock_data.get("metrics", {})
        price = stock_data.get("price", 0)

        # 提取关键指标（已验证，不使用默认值）
        eps = metrics["eps"]
        bvps = metrics["bvps"]
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        debt_ratio = metrics["debt_ratio"]
        current_ratio = metrics["current_ratio"]

        # 可选指标
        net_net_wc = stock_data.get("net_net_working_capital", 0)
        aaa_bond_yield = stock_data.get("aaa_bond_yield", self.DEFAULT_AAA_BOND_YIELD)

        # 1. 计算Graham公式内在价值
        intrinsic_value = self._calculate_graham_intrinsic_value(eps, bvps)

        # 2. 计算安全边际
        safety_margin = self._calculate_safety_margin(intrinsic_value, price)

        # 3. 评估净净机会
        net_net_score = self._evaluate_net_net(price, net_net_wc)

        # 4. 评估盈利收益率
        earnings_yield_score = self._evaluate_earnings_yield(pe_ratio, aaa_bond_yield)

        # 5. 评估财务安全性
        safety_score = self._evaluate_financial_safety(debt_ratio, current_ratio)

        # 6. 评估估值吸引力
        valuation_score = self._evaluate_valuation_attractiveness(
            pe_ratio, pb_ratio, safety_margin
        )

        # 综合评分 (0-100)
        scores = {
            "intrinsic_value": self._score_intrinsic_value(safety_margin),
            "net_net": net_net_score,
            "earnings_yield": earnings_yield_score,
            "financial_safety": safety_score,
            "valuation": valuation_score,
        }

        # 计算加权总分（Graham更看重安全边际和财务安全）
        weights = {
            "intrinsic_value": 0.30,
            "net_net": 0.15,
            "earnings_yield": 0.20,
            "financial_safety": 0.25,
            "valuation": 0.10,
        }

        total_score = sum(scores[k] * weights[k] for k in scores.keys())

        # 计算置信度
        confidence = min(total_score / 100, 1.0)

        # 做出决策
        decision = self._make_decision(total_score, scores, safety_margin)

        # 生成理由和关键因素
        reasoning = self._generate_reasoning(
            decision, scores, safety_margin, intrinsic_value, price, stock_data
        )
        key_factors = self._extract_key_factors(
            scores, safety_margin, intrinsic_value, price, pe_ratio, stock_data
        )

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "scores": scores,
            "total_score": total_score,
            "intrinsic_value": intrinsic_value,
            "safety_margin": safety_margin,
        }

    def _calculate_graham_intrinsic_value(self, eps: float, bvps: float) -> float:
        """
        使用Graham公式计算内在价值

        公式: √(22.5 × EPS × BVPS)

        Args:
            eps: 每股收益
            bvps: 每股账面价值

        Returns:
            内在价值
        """
        if eps <= 0 or bvps <= 0:
            return 0

        try:
            intrinsic_value = math.sqrt(self.GRAHAM_CONSTANT * eps * bvps)
            return round(intrinsic_value, 2)
        except (ValueError, TypeError):
            return 0

    def _calculate_safety_margin(self, intrinsic_value: float, price: float) -> float:
        """
        计算安全边际

        安全边际 = (内在价值 - 价格) / 内在价值

        Args:
            intrinsic_value: 内在价值
            price: 当前价格

        Returns:
            安全边际 (0-1)
        """
        if intrinsic_value <= 0 or price <= 0:
            return 0

        safety_margin = (intrinsic_value - price) / intrinsic_value
        return max(0, min(1, safety_margin))

    def _evaluate_net_net(self, price: float, net_net_wc: float) -> float:
        """
        评估净净机会

        Net-Net原则: 价格应该低于净净营运资本的2/3

        Args:
            price: 股票价格
            net_net_wc: 净净营运资本

        Returns:
            净净评分 (0-100)
        """
        if net_net_wc <= 0:
            return 50  # 没有净净数据，给中性分

        # 计算净净折扣率
        discount_rate = (net_net_wc - price) / net_net_wc if net_net_wc > 0 else 0

        # Graham要求价格 <= 2/3净净营运资本
        required_discount = 1 / 3  # 至少33%折扣

        if discount_rate >= required_discount:
            # 极佳的净净机会
            base_score = 100
            bonus = min(20, (discount_rate - required_discount) * 100)
            return min(100, base_score + bonus)
        elif discount_rate >= 0:
            # 价格低于净净营运资本，但折扣不足
            return 50 + discount_rate * 100
        else:
            # 价格高于净净营运资本
            return max(0, 50 + discount_rate * 100)

    def _evaluate_earnings_yield(self, pe_ratio: float, aaa_bond_yield: float) -> float:
        """
        评估盈利收益率

        Graham要求: 盈利收益率(1/PE) >= 2倍AAA债券收益率

        Args:
            pe_ratio: 市盈率
            aaa_bond_yield: AAA债券收益率(%)

        Returns:
            盈利收益率评分 (0-100)
        """
        if pe_ratio <= 0:
            return 0

        earnings_yield = 1.0 / pe_ratio  # 盈利收益率
        required_yield = (aaa_bond_yield / 100) * 2  # 要求的收益率

        if earnings_yield >= required_yield:
            # 满足Graham要求
            excess = earnings_yield - required_yield
            base_score = 80
            bonus = min(20, excess * 100)
            return min(100, base_score + bonus)
        else:
            # 不满足要求
            deficit = required_yield - earnings_yield
            score = 80 - deficit * 200
            return max(0, score)

    def _evaluate_financial_safety(self, debt_ratio: float, current_ratio: float) -> float:
        """
        评估财务安全性

        Graham偏好低负债、高流动性的公司

        Args:
            debt_ratio: 负债率
            current_ratio: 流动比率

        Returns:
            财务安全性评分 (0-100)
        """
        score = 50  # 基础分

        # 负债率评估（越低越好）
        if debt_ratio < 20:
            score += 30
        elif debt_ratio < 40:
            score += 20
        elif debt_ratio < 60:
            score += 10
        elif debt_ratio > 80:
            score -= 20

        # 流动比率评估（越高越好）
        if current_ratio > 2:
            score += 20
        elif current_ratio > 1.5:
            score += 10
        elif current_ratio < 1:
            score -= 30

        return max(0, min(100, score))

    def _evaluate_valuation_attractiveness(
        self, pe_ratio: float, pb_ratio: float, safety_margin: float
    ) -> float:
        """
        评估估值吸引力

        综合PE、PB和安全边际

        Args:
            pe_ratio: 市盈率
            pb_ratio: 市净率
            safety_margin: 安全边际

        Returns:
            估值吸引力评分 (0-100)
        """
        score = 50  # 基础分

        # PE评估（Graham偏好低PE）
        if pe_ratio > 0 and pe_ratio < 10:
            score += 25
        elif pe_ratio < 15:
            score += 15
        elif pe_ratio < 20:
            score += 5
        elif pe_ratio > 30:
            score -= 20

        # PB评估（Graham偏好PB < 1.5）
        if pb_ratio > 0 and pb_ratio < 1:
            score += 25
        elif pb_ratio < 1.5:
            score += 15
        elif pb_ratio < 2.5:
            score += 5
        elif pb_ratio > 4:
            score -= 15

        return max(0, min(100, score))

    def _score_intrinsic_value(self, safety_margin: float) -> float:
        """
        基于安全边际评分内在价值

        Args:
            safety_margin: 安全边际

        Returns:
            内在价值评分 (0-100)
        """
        if safety_margin >= 0.5:  # 50%以上安全边际
            return 100
        elif safety_margin >= 0.3:  # 30-50%安全边际
            return 80 + (safety_margin - 0.3) * 100
        elif safety_margin >= 0.2:  # 20-30%安全边际
            return 60 + (safety_margin - 0.2) * 200
        elif safety_margin >= 0.1:  # 10-20%安全边际
            return 40 + (safety_margin - 0.1) * 200
        elif safety_margin > 0:  # 0-10%安全边际
            return 30 + safety_margin * 100
        else:  # 无安全边际
            return 0

    def _make_decision(
        self, total_score: float, scores: dict, safety_margin: float
    ) -> str:
        """
        基于评分做出决策

        Graham的决策标准：
        1. 财务安全性是前提条件
        2. 要求至少30%安全边际
        3. 综合评分>70分才考虑买入

        Args:
            total_score: 总分
            scores: 各维度评分
            safety_margin: 安全边际

        Returns:
            决策 (buy/sell/hold)
        """
        # 财务安全性不达标，直接回避
        if scores["financial_safety"] < 50:
            return "sell"

        # 安全边际不足30%，回避或观望
        if safety_margin < 0.2:  # 20%安全边际是最低要求
            return "sell"
        elif safety_margin < 0.3:  # 30%以下，观望
            return "hold"

        # 综合评分判断
        if total_score >= 70:
            return "buy"
        elif total_score >= 60:
            return "hold"
        else:
            return "sell"

    def _generate_reasoning(
        self,
        decision: str,
        scores: dict,
        safety_margin: float,
        intrinsic_value: float,
        price: float,
        stock_data: dict,
    ) -> str:
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
            reasoning_parts.append(f"建议{name}({symbol})回避。")

        # 内在价值和安全边际
        if intrinsic_value > 0:
            margin_pct = safety_margin * 100
            reasoning_parts.append(
                f"Graham公式计算的内在价值为{intrinsic_value:.2f}元，"
                f"当前价格{price:.2f}元，安全边际{margin_pct:.1f}%。"
            )
            reasoning_parts[-1] = reasoning_parts[-1].replace("。", "") + "。"  # 修复结尾

        # 财务安全性
        safety_score = scores["financial_safety"]
        if safety_score >= 70:
            reasoning_parts.append("财务状况稳健，负债合理。")
        elif safety_score < 50:
            reasoning_parts.append("财务安全性不足，存在风险。")

        # 盈利收益率
        earnings_score = scores["earnings_yield"]
        if earnings_score >= 80:
            reasoning_parts.append("盈利收益率满足深度价值要求。")
        elif earnings_score < 50:
            reasoning_parts.append("盈利收益率不足。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(
        self,
        scores: dict,
        safety_margin: float,
        intrinsic_value: float,
        price: float,
        pe_ratio: float,
        stock_data: dict,
    ) -> list:
        """提取关键投资因素"""
        factors = []

        # 安全边际
        if safety_margin >= 0.5:
            factors.append(f"高安全边际({safety_margin*100:.1f}%)")
        elif safety_margin >= 0.3:
            factors.append(f"安全边际({safety_margin*100:.1f}%)")
        elif safety_margin < 0.1:
            factors.append("缺乏安全边际")

        # 内在价值
        if intrinsic_value > 0:
            if price < intrinsic_value:
                factors.append(f"价格低于内在价值({intrinsic_value:.2f}元)")

        # 估值
        if pe_ratio > 0 and pe_ratio < 10:
            factors.append(f"低PE({pe_ratio:.1f})")

        # 净净机会
        net_net_wc = stock_data.get("net_net_working_capital", 0)
        if net_net_wc > 0 and price < net_net_wc:
            factors.append("净净机会")

        # 财务安全
        if scores["financial_safety"] >= 80:
            factors.append("财务安全")

        # 盈利收益率
        if scores["earnings_yield"] >= 80:
            factors.append("高盈利收益率")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        Graham风格：
        - 高安全边际(>30%)且高置信度(>0.7) → buy
        - 负安全边际 → sell
        - 其他情况 → hold（观望，等待更好价格）

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        decision = analysis.get("decision", "hold")
        confidence = analysis.get("confidence", 0.5)
        safety_margin = analysis.get("safety_margin", 0)

        # Graham非常保守，只有高安全边际和高置信度才买入
        if decision == "buy" and confidence > 0.7 and safety_margin > 0.3:
            return "buy"

        # 只有在价格高于内在价值（负安全边际）时才卖出
        if safety_margin < 0:
            return "sell"

        # 其他情况都保守持有/观望
        return "hold"

    def debate(self, context: dict) -> str:
        """
        参与投资辩论

        Graham会强调：
        1. 安全边际是投资的基石
        2. 在市场恐慌时寻找深度价值机会
        3. 避免追涨，控制下行风险
        4. 内在价值vs市场价格的偏离

        Args:
            context: 包含股票信息、市场情绪、其他观点的字典

        Returns:
            Graham风格的观点陈述
        """
        stock = context.get("stock", {})
        stock_name = stock.get("name", "该公司")
        market_sentiment = context.get("market_sentiment", "neutral")

        # 根据市场情绪调整论点
        if market_sentiment == "bullish":
            return (
                f"关于{stock_name}，在市场乐观时我保持谨慎。"
                "投资者往往在牛市中忽视风险，支付过高的价格。"
                "我关注的是：当前价格是否提供了足够的安全边际？"
                "如果价格远高于内在价值，即使是最优秀的公司也不是好的投资。"
                "记住：在别人贪婪时恐惧，保护本金永远是第一位的。"
            )
        elif market_sentiment == "bearish":
            return (
                f"关于{stock_name}，市场恐慌可能提供深度价值机会。"
                "当投资者因为恐惧而抛售时，优质资产可能被错误定价。"
                "我会寻找那些：价格远低于内在价值、财务稳健、有良好盈利能力的公司。"
                "净净策略告诉我们：在悲观时期，可以以低于清算价值的价格买入优质企业。"
                "但必须记住：只有在有足够安全边际时才行动。"
            )
        else:
            return (
                f"关于{stock_name}，我关注三个核心问题："
                "1. 内在价值是多少？使用Graham公式计算。"
                "2. 当前价格提供了多少安全边际？要求至少30%。"
                "3. 财务是否足够安全？低负债、高流动性是关键。"
                "只有当这三个问题的答案都令人满意时，这才是一个深度价值机会。"
            )
