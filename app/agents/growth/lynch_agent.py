"""彼得·林奇风格GARP投资Agent"""
import logging
import pandas as pd
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


class LynchAgent(BaseAgent):
    """
    彼得·林奇风格的GARP (Growth At Reasonable Price) 投资Agent

    投资理念:
    1. PEG比率：PE/增长率 < 1 表示合理价格
    2. 买你所知：投资日常生活中熟悉的公司
    3. 十倍股潜力：寻找能够成长10倍的股票
    4. 股票分类：慢速增长、稳健增长、快速增长、周期性、困境反转
    5. 13个选股标准
    """

    # Peter Lynch的13个选股标准
    SELECTION_CRITERIA = [
        "名字枯燥乏味",
        "业务枯燥乏味",
        "令人厌恶",
        "有子公司被华尔街忽略",
        "被机构投资者忽视",
        "有谣言传言",
        "处于增长行业",
        "护城河保护",
        "人们必须持续购买产品",
        "技术领先者",
        "内部人买入",
        "回购股票",
        "低PEG比率"
    ]

    # 股票分类
    STOCK_CATEGORIES = {
        "slow_grower": "慢速增长股",
        "stalwart": "稳健增长股",
        "fast_grower": "快速增长股",
        "cyclical": "周期性股票",
        "turnaround": "困境反转股",
        "asset_play": "资产重组股"
    }

    def __init__(self, tushare_service):
        """
        初始化Lynch Agent

        Args:
            tushare_service: Tushare数据服务实例
        """
        super().__init__(tushare_service)

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Peter Lynch"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "GARP投资：以合理价格买入增长股，关注PEG比率、十倍股潜力和日常生活熟悉的公司"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于彼得·林奇理念分析股票

        评估维度:
        1. PEG比率（核心指标）
        2. 增长率合理性
        3. 股票分类
        4. 十倍股潜力
        5. 熟悉度（买你所知）
        6. 13个选股标准符合度

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
                "reasoning": f"缺少关键数据({missing})，无法进行林奇风格分析。林奇GARP策略需要PE和增长率来计算PEG比率。",
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

        # 解析daily_basic数据（可选）
        daily_basic = fundamentals.get("daily_basic", pd.DataFrame())
        if not daily_basic.empty:
            latest = daily_basic.iloc[0]
            pe_ratio = float(latest.get("pe", 0) or 0)
            pb_ratio = float(latest.get("pb", 0) or 0)
            dividend_yield = float(latest.get("dv_ratio", 0) or 0)
        else:
            pe_ratio = 0.0
            pb_ratio = 0.0
            dividend_yield = 0.0

        # 解析利润表数据
        income = fundamentals["income"]
        latest_income = income.iloc[0]
        total_revenue = float(latest_income.get("total_revenue", 0) or 0)

        # 解析资产负债表数据
        balancesheet = fundamentals["balancesheet"]
        latest_bs = balancesheet.iloc[0]
        total_assets = float(latest_bs.get("total_assets", 0) or 0)
        equity = float(latest_bs.get("total_hldr_eqy_exc_min_int", 0) or 0)
        total_liab = float(latest_bs.get("total_liab", 0) or 0)

        # 解析现金流量表数据
        cashflow = fundamentals["cashflow"]
        latest_cf = cashflow.iloc[0]
        net_profit = float(latest_cf.get("net_profit", 0) or 0)

        # 解析财务指标（fina_indicator提供预计算的指标）
        fina = fundamentals["fina_indicator"]
        latest_fina = fina.iloc[0]
        roe = float(latest_fina.get("roe", 0) or 0)
        revenue_growth = float(latest_fina.get("rev_yoy", 0) or 0)
        profit_growth = float(latest_fina.get("netprofit_yoy", 0) or 0)

        # 计算衍生指标
        debt_ratio = (total_liab / total_assets * 100) if total_assets > 0 else 0

        # 构建metrics字典
        metrics = {
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "roe": roe,
            "debt_ratio": debt_ratio,
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "dividend_yield": dividend_yield,
        }

        # 数据质量验证
        stock_data_temp = {
            "symbol": stock_code,
            "name": f"股票{stock_code}",
            "metrics": metrics
        }

        validation_result = DataValidator.validate_stock_data(
            stock_data_temp,
            agent_name=self.name,
            strict_mode=True
        )

        stock_data_temp["data_quality"] = validation_result
        stock_data_temp["business_info"] = {
            "industry": "未知",
            "main_product": "未知",
            "is_dull_name": False,
            "is_dull_business": False,
            "has_subsidiary": None,
            "is_in_ignored_sector": False,
            "has_rumor": False,
        }
        stock_data_temp["insider_info"] = {
            "insider_buying": None,
            "share_buyback": None,
            "insider_holdings_pct": 0,
        }

        return stock_data_temp

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        metrics = stock_data.get("metrics", {})
        business_info = stock_data.get("business_info", {})
        insider_info = stock_data.get("insider_info", {})

        # 提取关键指标（已验证，不使用默认值）
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        roe = metrics.get("roe", 0)
        debt_ratio = metrics["debt_ratio"]
        revenue_growth = metrics["revenue_growth"]
        profit_growth = metrics["profit_growth"]
        dividend_yield = metrics.get("dividend_yield", 0)

        # 计算PEG比率（最重要指标）
        peg_ratio = self._calculate_peg(pe_ratio, profit_growth)

        # 评分系统 (0-100)
        scores = {
            "peg": self._evaluate_peg(peg_ratio),
            "growth": self._evaluate_growth(revenue_growth, profit_growth),
            "category": self._evaluate_category(metrics, business_info),
            "tenbagger": self._evaluate_tenbagger_potential(metrics, business_info),
            "familiarity": self._evaluate_familiarity(business_info),
            "lynch_criteria": self._evaluate_lynch_criteria(business_info, insider_info)
        }

        # 计算总分
        total_score = sum(scores.values()) / len(scores)

        # 计算置信度
        confidence = min(total_score / 100, 1.0)

        # 做出决策
        decision = self._make_decision(total_score, scores, peg_ratio)

        # 生成理由和关键因素
        reasoning = self._generate_reasoning(decision, scores, stock_data, peg_ratio)
        key_factors = self._extract_key_factors(scores, stock_data, peg_ratio)

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "scores": scores,
            "total_score": total_score,
            "peg_ratio": peg_ratio,
            "category": self._classify_stock(metrics, business_info)
        }

    def _calculate_peg(self, pe_ratio: float, growth_rate: float) -> float:
        """
        计算PEG比率

        PEG = PE / 增长率
        PEG < 1: 股票被低估
        PEG = 1: 股票估值合理
        PEG > 1: 股票被高估

        Args:
            pe_ratio: 市盈率
            growth_rate: 盈利增长率

        Returns:
            PEG比率
        """
        if growth_rate <= 0:
            return float('inf')  # 负增长的公司PEG为无穷大
        return pe_ratio / growth_rate

    def _evaluate_peg(self, peg_ratio: float) -> float:
        """
        评估PEG比率 (0-100)

        Peter Lynch认为:
        - PEG < 1: 被低估，买入机会
        - PEG = 1: 估值合理
        - PEG > 1.5: 被高估
        """
        if peg_ratio == float('inf'):
            return 0  # 负增长的公司

        score = 50  # 基础分

        if peg_ratio < 0.5:
            score += 40  # 严重低估
        elif peg_ratio < 0.8:
            score += 30  # 低估
        elif peg_ratio < 1.0:
            score += 20  # 略微低估
        elif peg_ratio < 1.2:
            score += 10  # 合理
        elif peg_ratio < 1.5:
            score += 0   # 略高
        elif peg_ratio < 2.0:
            score -= 20  # 高估
        else:
            score -= 40  # 严重高估

        return max(0, min(100, score))

    def _evaluate_growth(self, revenue_growth: float, profit_growth: float) -> float:
        """
        评估增长合理性 (0-100)

        林奇喜欢20-25%的稳定增长率，过高的增长率难以持续
        """
        score = 50  # 基础分

        # 利润增长率评估
        if profit_growth > 50:
            score += 10  # 增长过快，难以持续
        elif profit_growth > 25:
            score += 30  # 理想增长
        elif profit_growth > 15:
            score += 25
        elif profit_growth > 10:
            score += 15
        elif profit_growth > 5:
            score += 5
        elif profit_growth < 0:
            score -= 40  # 负增长

        # 收入增长验证
        if revenue_growth > 0 and profit_growth > 0:
            # 收入增长应该支持利润增长
            if abs(revenue_growth - profit_growth) < 10:
                score += 10  # 增长一致性好

        return max(0, min(100, score))

    def _evaluate_category(self, metrics: dict, business_info: dict) -> float:
        """
        评估股票类别及其适合性 (0-100)

        林奇最偏好:
        1. 稳健增长股（10-20%增长）
        2. 快速增长股（20-25%增长）
        3. 困境反转股
        """
        revenue_growth = metrics.get("revenue_growth", 0)
        profit_growth = metrics.get("profit_growth", 0)
        dividend_yield = metrics.get("dividend_yield", 0)

        avg_growth = (revenue_growth + profit_growth) / 2

        score = 50  # 基础分

        # 快速增长股（林奇的最爱）
        if 20 <= avg_growth <= 25:
            score += 30
        # 稳健增长股
        elif 10 <= avg_growth < 20:
            score += 25
        # 慢速增长但有股息
        elif avg_growth < 10 and dividend_yield > 3:
            score += 20
        # 困境反转股
        elif business_info.get("is_turnaround", False):
            score += 15
        # 周期性股票（需要特殊技巧）
        elif business_info.get("is_cyclical", False):
            score += 5

        return max(0, min(100, score))

    def _evaluate_tenbagger_potential(self, metrics: dict, business_info: dict) -> float:
        """
        评估十倍股潜力 (0-100)

        十倍股特征:
        1. 小市值（更容易翻倍）
        2. 高增长潜力
        3. 大市场空间
        4. 强竞争优势
        """
        market_cap = business_info.get("market_cap", 0)
        market_size = business_info.get("market_size", 0)
        competitive_position = business_info.get("competitive_position", 5)  # 1-10

        score = 50  # 基础分

        # 小市值公司更容易成为十倍股
        if market_cap > 0:
            if market_cap < 10_000_000_000:  # 100亿以下
                score += 25
            elif market_cap < 50_000_000_000:  # 500亿以下
                score += 15
            elif market_cap < 100_000_000_000:  # 1000亿以下
                score += 5

        # 市场空间
        if market_size > 0:
            if market_size > 1_000_000_000_000:  # 万亿市场
                score += 15
            elif market_size > 100_000_000_000:  # 千亿市场
                score += 10

        # 竞争地位
        if competitive_position >= 8:
            score += 10
        elif competitive_position >= 6:
            score += 5

        return max(0, min(100, score))

    def _evaluate_familiarity(self, business_info: dict) -> float:
        """
        评估熟悉度（买你所知）(0-100)

        林奇建议投资日常生活中熟悉的公司
        """
        product_familiarity = business_info.get("product_familiarity", 0)  # 1-10
        brand_recognition = business_info.get("brand_recognition", 0)  # 1-10
        consumer_business = business_info.get("is_consumer_business", False)

        score = 50  # 基础分

        # 消费者业务更容易理解
        if consumer_business:
            score += 20

        # 产品熟悉度
        if product_familiarity >= 8:
            score += 20
        elif product_familiarity >= 5:
            score += 10

        # 品牌认知度
        if brand_recognition >= 8:
            score += 10
        elif brand_recognition >= 5:
            score += 5

        return max(0, min(100, score))

    def _evaluate_lynch_criteria(self, business_info: dict, insider_info: dict) -> float:
        """
        评估林奇13个选股标准的符合度 (0-100)

        每符合一个标准得7.7分（13个标准）
        """
        score = 0
        criteria_count = 0

        # 检查各项标准
        criteria_checks = {
            "boring_name": business_info.get("has_boring_name", False),
            "boring_business": business_info.get("has_boring_business", False),
            "distasteful": business_info.get("is_distasteful", False),
            "ignored_subsidiary": business_info.get("has_ignored_subsidiary", False),
            "institutional_neglect": business_info.get("institutional_ownership", 100) < 30,
            "rumors": business_info.get("has_rumors", False),
            "growth_industry": business_info.get("is_growth_industry", False),
            "moat": business_info.get("has_moat", False),
            "essential_product": business_info.get("has_essential_product", False),
            "tech_leader": business_info.get("is_tech_leader", False),
            "insider_buying": insider_info.get("insider_buying", False),
            "share_buyback": insider_info.get("share_buyback", False),
            "low_peg": True  # 这个已经在PEG评分中单独评估
        }

        for met, value in criteria_checks.items():
            if value:
                criteria_count += 1

        # 每个标准约7.7分，总共100分
        score = (criteria_count / 13) * 100

        return score

    def _classify_stock(self, metrics: dict, business_info: dict) -> str:
        """
        对股票进行分类

        Returns:
            股票类别
        """
        revenue_growth = metrics.get("revenue_growth", 0)
        profit_growth = metrics.get("profit_growth", 0)
        dividend_yield = metrics.get("dividend_yield", 0)
        avg_growth = (revenue_growth + profit_growth) / 2

        # 快速增长股
        if avg_growth >= 20:
            return self.STOCK_CATEGORIES["fast_grower"]

        # 稳健增长股
        elif 10 <= avg_growth < 20:
            return self.STOCK_CATEGORIES["stalwart"]

        # 慢速增长股
        elif avg_growth < 10 and dividend_yield > 3:
            return self.STOCK_CATEGORIES["slow_grower"]

        # 困境反转股
        elif business_info.get("is_turnaround", False):
            return self.STOCK_CATEGORIES["turnaround"]

        # 周期性股票
        elif business_info.get("is_cyclical", False):
            return self.STOCK_CATEGORIES["cyclical"]

        # 资产重组股
        elif business_info.get("is_asset_play", False):
            return self.STOCK_CATEGORIES["asset_play"]

        # 默认为稳健增长
        return self.STOCK_CATEGORIES["stalwart"]

    def _make_decision(self, total_score: float, scores: dict, peg_ratio: float) -> str:
        """
        基于评分做出决策

        林奇的决策逻辑:
        1. PEG比率是最重要的单一指标
        2. 总体评分要高
        3. 十倍股潜力和熟悉度加分
        """
        # PEG < 1是林奇的核心标准
        if peg_ratio > 2.0:
            return "sell"  # PEG过高，估值过热

        # 综合评分决策
        if total_score >= 75 and peg_ratio < 1.2:
            return "buy"
        elif total_score >= 60:
            return "hold"
        else:
            return "sell"

    def _generate_reasoning(self, decision: str, scores: dict, stock_data: dict, peg_ratio: float) -> str:
        """生成投资理由"""
        symbol = stock_data.get("symbol", "")
        name = stock_data.get("name", "")
        category = self._classify_stock(stock_data.get("metrics", {}), stock_data.get("business_info", {}))

        reasoning_parts = []

        # 决策说明
        if decision == "buy":
            reasoning_parts.append(f"建议{name}({symbol})买入。")
        elif decision == "hold":
            reasoning_parts.append(f"建议{name}({symbol})持有观望。")
        else:
            reasoning_parts.append(f"建议{name}({symbol})卖出或回避。")

        # PEG评价
        if peg_ratio == float('inf'):
            reasoning_parts.append("公司盈利增长为负，不符合GARP策略。")
        elif peg_ratio < 0.8:
            reasoning_parts.append(f"PEG比率{peg_ratio:.2f}较低，股价相对增长被低估。")
        elif peg_ratio < 1.2:
            reasoning_parts.append(f"PEG比率{peg_ratio:.2f}合理，估值与增长匹配。")
        else:
            reasoning_parts.append(f"PEG比率{peg_ratio:.2f}偏高，可能存在估值风险。")

        # 股票分类说明
        reasoning_parts.append(f"该股票属于{category}。")

        # 十倍股潜力
        if scores["tenbagger"] >= 70:
            reasoning_parts.append("具有十倍股潜力。")

        # 熟悉度
        if scores["familiarity"] >= 70:
            reasoning_parts.append("是日常生活中熟悉的优秀公司。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(self, scores: dict, stock_data: dict, peg_ratio: float) -> list:
        """提取关键投资因素"""
        factors = []

        # PEG相关
        if peg_ratio < 1.0:
            factors.append(f"低PEG({peg_ratio:.2f})")
        elif peg_ratio > 2.0:
            factors.append(f"高PEG({peg_ratio:.2f})")

        # 增长相关
        metrics = stock_data.get("metrics", {})
        profit_growth = metrics.get("profit_growth", 0)
        if profit_growth > 20:
            factors.append(f"高增长({profit_growth:.1f}%)")

        # 十倍股潜力
        if scores["tenbagger"] >= 70:
            factors.append("十倍股潜力")

        # 熟悉度
        if scores["familiarity"] >= 70:
            factors.append("买你所知")

        # 股票分类
        category = self._classify_stock(metrics, stock_data.get("business_info", {}))
        factors.append(category)

        # 林奇标准符合度
        if scores["lynch_criteria"] >= 70:
            factors.append("符合多项林奇标准")

        # 内部人交易
        insider_info = stock_data.get("insider_info", {})
        if insider_info.get("insider_buying", False):
            factors.append("内部人买入")
        if insider_info.get("share_buyback", False):
            factors.append("股票回购")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        林奇风格：
        - 高置信度(>0.6)的买入分析 → buy
        - 高置信度(>0.6)的卖出分析 → sell
        - 其他情况 → hold

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        decision = analysis.get("decision", "hold")
        confidence = analysis.get("confidence", 0.5)

        # 林奇愿意承担合理风险
        if confidence > 0.6:
            return decision

        # 中等置信度倾向于持有
        return "hold"

    def debate(self, context: dict) -> str:
        """
        参与投资辩论

        林奇会强调：
        1. 买你所知
        2. PEG比率的重要性
        3. 寻找十倍股
        4. 关注日常生活
        5. 小公司更有潜力

        Args:
            context: 包含股票信息、市场情绪、其他观点的字典

        Returns:
            林奇风格的观点陈述
        """
        stock = context.get("stock", {})
        stock_name = stock.get("name", "该公司")
        market_sentiment = context.get("market_sentiment", "neutral")

        # 根据市场情绪调整论点
        if market_sentiment == "bullish":
            return (
                f"关于{stock_name}，我关注两个核心问题："
                "1. 这家公司的PEG比率是否合理？如果增长率能够支撑当前PE，那么股价就不是泡沫。"
                "2. 这是否是你熟悉的行业？如果你不了解它做什么，就不应该投资。"
                "记住：最好的投资机会往往在日常生活中，而不是华尔街的热门股。"
            )
        elif market_sentiment == "bearish":
            return (
                f"关于{stock_name}，市场恐慌时可能发现被错杀的成长股。"
                "如果这家公司的PEG比率小于1，而且你了解它的产品和服务，"
                "这可能是一个绝佳的买入机会。小公司在市场恐慌时往往被过度抛售。"
            )
        else:
            return (
                f"关于{stock_name}，我问几个简单的问题："
                "1. PEG比率是否小于1？"
                "2. 你是否了解这家公司的产品？"
                "3. 它是否有可能成为十倍股？"
                "4. 是否符合我的13个选股标准？"
                "如果答案都是肯定的，这就是一个值得研究的投资机会。"
            )
