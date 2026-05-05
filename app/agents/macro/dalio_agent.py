"""Ray Dalio风格宏观经济分析Agent"""
import logging
import pandas as pd
from typing import Dict, List, Optional
from enum import Enum
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


class EconomicCycleStage(Enum):
    """经济周期阶段"""
    INFLATION = "inflation"          # 通货膨胀期
    RECESSION = "recession"          # 经济衰退期
    DEPRESSION = "depression"        # 经济萧条期
    RECOVERY = "recovery"            # 经济复苏期


class DebtCyclePhase(Enum):
    """债务周期阶段"""
    SHORT_TERM_EXPANSION = "short_term_expansion"    # 短期债务扩张
    SHORT_TERM_CONTRACTION = "short_term_contraction"  # 短期债务收缩
    LONG_TERM_DEBT_CRISIS = "long_term_debt_crisis"    # 长期债务危机
    DEBT_DELEVERAGING = "debt_deleveraging"            # 去杠杆化


class DalioAgent(BaseAgent):
    """
    Ray Dalio风格的宏观经济分析Agent

    核心投资理念:
    1. 经济周期分析：识别经济所处的周期阶段
    2. 债务周期分析：短期和长期债务周期
    3. 全天候策略：资产配置以适应不同经济环境
    4. 分散化投资：在不同资产类别间分散风险

    全天候策略资产配置:
    - 股票 30%
    - 长期国债 40%
    - 中期国债 15%
    - 黄金 7.5%
    - 大宗商品 7.5%
    """

    # 全天候策略标准配置
    ALL_WEATHER_ALLOCATION = {
        "stocks": 0.30,           # 股票
        "long_term_bonds": 0.40,  # 长期国债
        "mid_term_bonds": 0.15,   # 中期国债
        "gold": 0.075,            # 黄金
        "commodities": 0.075,     # 大宗商品
    }

    def __init__(self, tushare_service):
        """
        初始化达里奥Agent

        Args:
            tushare_service: Tushare数据服务实例
        """
        super().__init__(tushare_service)

    @property
    def name(self) -> str:
        """Agent名称"""
        return "Ray Dalio"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "宏观经济分析：关注经济周期、债务周期和全天候资产配置"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于Dalio宏观经济理念分析股票

        评估维度:
        1. 经济周期阶段识别
        2. 短期债务周期位置
        3. 长期债务周期风险
        4. 资产类别配置建议
        5. 通胀/通缩环境判断

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
                "reasoning": f"缺少关键数据({missing})，无法进行达利欧风格分析。达利欧关注经济周期和债务周期。",
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

        # 获取日线数据（用于计算beta）
        import asyncio
        loop = asyncio.get_event_loop()

        formatted_code = self.tushare._format_stock_code(stock_code)

        daily_df = await loop.run_in_executor(
            None,
            lambda: self.tushare.api.daily(
                ts_code=formatted_code,
                start_date="20230101",
                end_date=""
            )
        )

        # 解析资产负债表数据
        balancesheet = fundamentals["balancesheet"]
        latest_bs = balancesheet.iloc[0]
        total_assets = float(latest_bs.get("total_assets", 0) or 0)
        equity = float(latest_bs.get("total_hldr_eqy_exc_min_int", 0) or 0)
        total_liab = float(latest_bs.get("total_liab", 0) or 0)

        # 解析财务指标（fina_indicator提供预计算的指标）
        fina = fundamentals["fina_indicator"]
        latest_fina = fina.iloc[0]
        debt_to_assets = float(latest_fina.get("debt_to_assets", 0) or 0)

        # 计算债务比率
        debt_to_equity = (total_liab / equity) if equity > 0 else 0

        # 计算波动率（用于周期敏感性估算）
        if not daily_df.empty and len(daily_df) > 20:
            returns = daily_df.head(20)["pct_chg"]
            volatility = returns.std()
            cyclical_sensitivity = min(volatility / 2, 2.0)
        else:
            cyclical_sensitivity = 1.0

        # 构建metrics字典
        metrics = {
            "debt_to_assets": debt_to_assets,
            "debt_to_equity": debt_to_equity,
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
        stock_data_temp["macro_indicators"] = {
            "gdp_growth": 0,
            "inflation_rate": 0,
            "interest_rate": 0,
            "unemployment_rate": 0,
            "credit_growth": 0,
            "debt_to_gdp": 0,
        }
        stock_data_temp["company_data"] = {
            "beta": 1.0,
            "cyclical_sensitivity": float(cyclical_sensitivity),
            "industry": "未知",
        }

        return stock_data_temp

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        # 提取数据
        macro_data = stock_data.get("macro_indicators", {})
        company_data = stock_data.get("company_data", {})

        # 分析经济周期阶段
        cycle_stage = self._identify_economic_cycle_stage(macro_data)

        # 分析债务周期阶段
        debt_phase = self._identify_debt_cycle_phase(macro_data)

        # 评估通胀环境
        inflation_environment = self._assess_inflation_environment(macro_data)

        # 计算周期适配度
        cycle_fitness = self._calculate_cycle_fitness(
            company_data, cycle_stage, debt_phase, inflation_environment
        )

        # 计算风险调整收益
        risk_adjusted_return = self._calculate_risk_adjusted_return(
            company_data, macro_data
        )

        # 计算全天候配置权重
        allocation_weights = self._calculate_allocation_weights(
            cycle_stage, inflation_environment
        )

        # 综合评分
        scores = {
            "cycle_timing": cycle_fitness,
            "risk_adjusted_return": risk_adjusted_return,
            "macro_environment": self._score_macro_environment(macro_data),
            "debt_sustainability": self._score_debt_sustainability(macro_data),
        }

        total_score = sum(scores.values()) / len(scores)

        # 计算置信度（基于宏观经济数据的完整性）
        confidence = self._calculate_confidence(macro_data, total_score)

        # 做出决策
        decision = self._make_decision(total_score, scores, cycle_stage)

        # 生成理由和关键因素
        reasoning = self._generate_reasoning(
            decision, scores, cycle_stage, debt_phase, inflation_environment, stock_data
        )
        key_factors = self._extract_key_factors(
            scores, cycle_stage, debt_phase, inflation_environment
        )

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "key_factors": key_factors,
            "scores": scores,
            "total_score": total_score,
            "cycle_stage": cycle_stage.value,
            "debt_phase": debt_phase.value,
            "inflation_environment": inflation_environment,
            "allocation_weights": allocation_weights,
        }

    def _identify_economic_cycle_stage(self, macro_data: dict) -> EconomicCycleStage:
        """
        识别经济周期阶段

        依据指标:
        - GDP增长率
        - 失业率变化
        - 产能利用率
        - PMI指数
        """
        gdp_growth = macro_data.get("gdp_growth", 0)
        unemployment = macro_data.get("unemployment_rate", 5)
        pm_index = macro_data.get("pmi", 50)
        capacity_utilization = macro_data.get("capacity_utilization", 75)

        # 判断逻辑
        if gdp_growth > 3 and pm_index > 52 and unemployment < 5:
            return EconomicCycleStage.RECOVERY
        elif gdp_growth > 2 and pm_index > 50 and capacity_utilization > 80:
            return EconomicCycleStage.INFLATION
        elif gdp_growth < 0 or pm_index < 48 or unemployment > 7:
            return EconomicCycleStage.RECESSION
        elif gdp_growth < -2 and unemployment > 9 and pm_index < 45:
            return EconomicCycleStage.DEPRESSION
        else:
            return EconomicCycleStage.RECOVERY

    def _identify_debt_cycle_phase(self, macro_data: dict) -> DebtCyclePhase:
        """
        识别债务周期阶段

        依据指标:
        - 债务/GDP比率
        - 债务增长率
        - 利率水平
        - 信贷增长率
        """
        debt_to_gdp = macro_data.get("debt_to_gdp", 100)
        debt_growth = macro_data.get("debt_growth", 0)
        interest_rates = macro_data.get("interest_rate", 5)
        credit_growth = macro_data.get("credit_growth", 0)

        # 短期债务周期判断
        if credit_growth > 10 and interest_rates < 3:
            return DebtCyclePhase.SHORT_TERM_EXPANSION
        elif credit_growth < 0 and interest_rates > 5:
            return DebtCyclePhase.SHORT_TERM_CONTRACTION

        # 长期债务周期判断
        if debt_to_gdp > 300 and debt_growth > 15:
            return DebtCyclePhase.LONG_TERM_DEBT_CRISIS
        elif debt_to_gdp > 250 and (credit_growth < -5 or debt_growth < -5):
            return DebtCyclePhase.DEBT_DELEVERAGING

        # 默认情况
        return DebtCyclePhase.SHORT_TERM_EXPANSION

    def _assess_inflation_environment(self, macro_data: dict) -> str:
        """
        评估通胀环境

        Returns:
            "high_inflation": 高通胀 (>5%)
            "moderate_inflation": 温和通胀 (2-5%)
            "low_inflation": 低通胀/通缩风险 (<2%)
            "deflation": 通缩 (<0%)
        """
        cpi = macro_data.get("cpi", 2)
        ppi = macro_data.get("ppi", 2)

        avg_inflation = (cpi + ppi) / 2

        if avg_inflation > 5:
            return "high_inflation"
        elif avg_inflation > 2:
            return "moderate_inflation"
        elif avg_inflation > 0:
            return "low_inflation"
        else:
            return "deflation"

    def _calculate_cycle_fitness(
        self,
        company_data: dict,
        cycle_stage: EconomicCycleStage,
        debt_phase: DebtCyclePhase,
        inflation_env: str
    ) -> float:
        """
        计算企业在当前经济周期中的适应度 (0-100)
        """
        score = 50  # 基础分

        # 行业周期适应性
        industry = company_data.get("industry", "")
        cycle_sensitivity = company_data.get("cycle_sensitivity", 0.5)  # 0=防御性, 1=周期性

        # 根据经济周期阶段调整评分
        if cycle_stage == EconomicCycleStage.RECOVERY:
            # 复苏期：周期性行业表现更好
            score += (cycle_sensitivity - 0.5) * 40

        elif cycle_stage == EconomicCycleStage.INFLATION:
            # 通胀期：具有定价权的公司表现更好
            pricing_power = company_data.get("pricing_power", 0.5)
            score += (pricing_power - 0.5) * 30

        elif cycle_stage == EconomicCycleStage.RECESSION:
            # 衰退期：防御性行业表现更好
            score += (0.5 - cycle_sensitivity) * 40

        elif cycle_stage == EconomicCycleStage.DEPRESSION:
            # 萧条期：现金流充裕、低负债的公司更安全
            cash_ratio = company_data.get("cash_ratio", 0.1)
            score += min(cash_ratio * 100, 30)

        # 债务周期调整
        if debt_phase == DebtCyclePhase.DEBT_DELEVERAGING:
            # 去杠杆期：低负债公司更安全
            debt_ratio = company_data.get("debt_ratio", 50)
            score += max(0, (50 - debt_ratio) / 2)

        return max(0, min(100, score))

    def _calculate_risk_adjusted_return(self, company_data: dict, macro_data: dict) -> float:
        """
        计算风险调整后收益预期 (0-100)
        """
        # 基础收益率
        roe = company_data.get("roe", 10)
        revenue_growth = company_data.get("revenue_growth", 5)

        # 风险指标
        volatility = company_data.get("volatility", 20)
        beta = company_data.get("beta", 1.0)
        debt_ratio = company_data.get("debt_ratio", 50)

        # 夏普比率简化计算
        risk_free_rate = macro_data.get("risk_free_rate", 3)
        expected_return = (roe * 0.7 + revenue_growth * 0.3)
        sharpe_ratio = (expected_return - risk_free_rate) / (volatility / 100) if volatility > 0 else 0

        # 根据夏普比率评分
        score = 50
        if sharpe_ratio > 1.5:
            score += 30
        elif sharpe_ratio > 1.0:
            score += 20
        elif sharpe_ratio > 0.5:
            score += 10
        elif sharpe_ratio < 0:
            score -= 30

        # Beta调整（在宏观不稳定时期，低Beta更好）
        if beta < 0.8:
            score += 10
        elif beta > 1.3:
            score -= 10

        return max(0, min(100, score))

    def _score_macro_environment(self, macro_data: dict) -> float:
        """
        评估宏观环境健康度 (0-100)
        """
        score = 50

        # GDP增长评分
        gdp_growth = macro_data.get("gdp_growth", 2)
        if gdp_growth > 3:
            score += 15
        elif gdp_growth > 2:
            score += 10
        elif gdp_growth < 0:
            score -= 20

        # 失业率评分
        unemployment = macro_data.get("unemployment_rate", 5)
        if unemployment < 5:
            score += 10
        elif unemployment > 7:
            score -= 15

        # PMI评分
        pmi = macro_data.get("pmi", 50)
        if pmi > 52:
            score += 10
        elif pmi < 48:
            score -= 15

        return max(0, min(100, score))

    def _score_debt_sustainability(self, macro_data: dict) -> float:
        """
        评估债务可持续性 (0-100)
        """
        score = 50

        debt_to_gdp = macro_data.get("debt_to_gdp", 100)
        deficit = macro_data.get("fiscal_deficit", 3)

        # 债务占GDP比率
        if debt_to_gdp < 60:
            score += 20
        elif debt_to_gdp < 100:
            score += 10
        elif debt_to_gdp > 250:
            score -= 30

        # 财政赤字
        if deficit < 3:
            score += 15
        elif deficit > 10:
            score -= 20

        return max(0, min(100, score))

    def _calculate_allocation_weights(
        self,
        cycle_stage: EconomicCycleStage,
        inflation_env: str
    ) -> dict:
        """
        根据经济周期和通胀环境计算资产配置权重

        Returns:
            调整后的资产配置权重
        """
        # 从基准配置开始
        weights = self.ALL_WEATHER_ALLOCATION.copy()

        # 根据经济周期调整
        if cycle_stage == EconomicCycleStage.RECOVERY:
            # 复苏期：增加股票，减少债券
            weights["stocks"] += 0.10
            weights["long_term_bonds"] -= 0.05
            weights["mid_term_bonds"] -= 0.05

        elif cycle_stage == EconomicCycleStage.INFLATION:
            # 通胀期：增加大宗商品和黄金，减少长期债券
            weights["commodities"] += 0.10
            weights["gold"] += 0.05
            weights["long_term_bonds"] -= 0.15

        elif cycle_stage == EconomicCycleStage.RECESSION:
            # 衰退期：增加债券，减少股票
            weights["long_term_bonds"] += 0.15
            weights["mid_term_bonds"] += 0.05
            weights["stocks"] -= 0.20

        elif cycle_stage == EconomicCycleStage.DEPRESSION:
            # 萧条期：大幅增加债券和黄金，减少股票和大宗商品
            weights["long_term_bonds"] += 0.20
            weights["gold"] += 0.10
            weights["stocks"] -= 0.20
            weights["commodities"] -= 0.10

        # 根据通胀环境调整
        if inflation_env == "high_inflation":
            # 高通胀：增加TIPS和大宗商品
            weights["commodities"] += 0.05
            weights["gold"] += 0.05
            weights["long_term_bonds"] -= 0.10

        elif inflation_env == "deflation":
            # 通缩：增加长期国债
            weights["long_term_bonds"] += 0.10
            weights["commodities"] -= 0.05
            weights["stocks"] -= 0.05

        # 确保权重总和为1
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

        return weights

    def _calculate_confidence(self, macro_data: dict, total_score: float) -> float:
        """
        计算置信度

        宏观数据越完整，置信度越高
        """
        # 检查关键宏观数据的可用性
        key_indicators = [
            "gdp_growth", "unemployment_rate", "pmi",
            "cpi", "debt_to_gdp", "interest_rate"
        ]

        available_count = sum(1 for indicator in key_indicators if indicator in macro_data)
        completeness = available_count / len(key_indicators)

        # 基于数据完整性和评分的置信度
        base_confidence = total_score / 100
        adjusted_confidence = base_confidence * (0.5 + completeness * 0.5)

        return max(0, min(1, adjusted_confidence))

    def _make_decision(
        self,
        total_score: float,
        scores: dict,
        cycle_stage: EconomicCycleStage
    ) -> str:
        """
        基于评分做出投资决策
        """
        # 危机时期更保守
        if cycle_stage in [EconomicCycleStage.RECESSION, EconomicCycleStage.DEPRESSION]:
            if total_score >= 70 and scores["risk_adjusted_return"] > 70:
                return "buy"
            elif total_score >= 50:
                return "hold"
            else:
                return "sell"

        # 正常时期
        if total_score >= 70:
            return "buy"
        elif total_score >= 55:
            return "hold"
        else:
            return "sell"

    def _generate_reasoning(
        self,
        decision: str,
        scores: dict,
        cycle_stage: EconomicCycleStage,
        debt_phase: DebtCyclePhase,
        inflation_env: str,
        stock_data: dict
    ) -> str:
        """
        生成投资理由
        """
        symbol = stock_data.get("symbol", "")
        name = stock_data.get("name", "")

        reasoning_parts = []

        # 基本决策说明
        if decision == "buy":
            reasoning_parts.append(f"建议{name}({symbol})买入。")
        elif decision == "hold":
            reasoning_parts.append(f"建议{name}({symbol})持有观望。")
        else:
            reasoning_parts.append(f"建议{name}({symbol})卖出或回避。")

        # 经济周期说明
        cycle_descriptions = {
            EconomicCycleStage.RECOVERY: "经济处于复苏期，",
            EconomicCycleStage.INFLATION: "经济处于通胀期，",
            EconomicCycleStage.RECESSION: "经济处于衰退期，",
            EconomicCycleStage.DEPRESSION: "经济处于萧条期，",
        }
        reasoning_parts.append(cycle_descriptions.get(cycle_stage, ""))

        # 通胀环境说明
        inflation_descriptions = {
            "high_inflation": "高通胀环境下",
            "moderate_inflation": "温和通胀环境下",
            "low_inflation": "低通胀环境下",
            "deflation": "通缩环境下",
        }
        reasoning_parts.append(inflation_descriptions.get(inflation_env, ""))

        # 周期适应性评价
        cycle_fitness = scores.get("cycle_timing", 50)
        if cycle_fitness >= 70:
            reasoning_parts.append("该公司具有良好的周期适应性。")
        elif cycle_fitness < 40:
            reasoning_parts.append("该公司当前周期适应性较弱。")

        # 风险调整收益评价
        risk_return = scores.get("risk_adjusted_return", 50)
        if risk_return >= 70:
            reasoning_parts.append("风险调整后收益预期良好。")
        elif risk_return < 40:
            reasoning_parts.append("风险调整后收益预期不佳。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(
        self,
        scores: dict,
        cycle_stage: EconomicCycleStage,
        debt_phase: DebtCyclePhase,
        inflation_env: str
    ) -> list:
        """
        提取关键投资因素
        """
        factors = []

        # 经济周期因素
        cycle_names = {
            EconomicCycleStage.RECOVERY: "经济复苏",
            EconomicCycleStage.INFLATION: "通胀期",
            EconomicCycleStage.RECESSION: "经济衰退",
            EconomicCycleStage.DEPRESSION: "经济萧条",
        }
        factors.append(cycle_names.get(cycle_stage, "经济周期分析"))

        # 通胀环境因素
        inflation_factors = {
            "high_inflation": "高通胀",
            "moderate_inflation": "温和通胀",
            "low_inflation": "低通胀",
            "deflation": "通缩",
        }
        factors.append(inflation_factors.get(inflation_env, "通胀分析"))

        # 评分相关因素
        if scores.get("cycle_timing", 0) >= 70:
            factors.append("周期适应性强")
        elif scores.get("cycle_timing", 0) < 40:
            factors.append("周期适应性弱")

        if scores.get("risk_adjusted_return", 0) >= 70:
            factors.append("风险调整收益高")

        if scores.get("debt_sustainability", 0) < 40:
            factors.append("债务风险高")

        # 债务周期因素
        if debt_phase == DebtCyclePhase.DEBT_DELEVERAGING:
            factors.append("去杠杆化")
        elif debt_phase == DebtCyclePhase.LONG_TERM_DEBT_CRISIS:
            factors.append("债务危机")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        Dalio风格：
        - 重点考虑宏观经济环境
        - 在周期转折点更谨慎
        - 优先选择风险调整后收益好的标的

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        decision = analysis.get("decision", "hold")
        confidence = analysis.get("confidence", 0.5)
        scores = analysis.get("scores", {})

        # 检查是否处于危机时期
        cycle_stage = analysis.get("cycle_stage", "")

        # 危机时期更保守
        if cycle_stage in ["recession", "depression"]:
            if confidence > 0.8 and scores.get("risk_adjusted_return", 0) > 75:
                return decision
            else:
                return "hold"

        # 正常时期跟随分析决策
        if confidence > 0.6:
            return decision

        return "hold"

    def debate(self, context: dict) -> str:
        """
        参与投资辩论

        Dalio会强调：
        1. 经济周期的重要性
        2. 分散化投资的价值
        3. 理解当前所处的历史阶段
        4. 全天候策略的风险平衡

        Args:
            context: 包含股票信息、市场环境、其他观点的字典

        Returns:
            Dalio风格的观点陈述
        """
        stock = context.get("stock", {})
        stock_name = stock.get("name", "该公司")

        # 尝试获取宏观经济信息
        macro_context = context.get("macro_context", {})
        cycle_stage = macro_context.get("cycle_stage", "未知")

        # 根据经济周期阶段调整论点
        if cycle_stage == "inflation":
            return (
                f"关于{stock_name}，在通胀上升期，我们需要特别关注企业的定价能力。"
                "能够将成本上涨转嫁给消费者的公司将在通胀环境中表现更好。"
                "同时，我们在资产配置上应该增加大宗商品和通胀保值债券的比例，"
                "减少对长期国债的敞口。历史告诉我们，通胀环境下实际回报最关键。"
            )
        elif cycle_stage == "recession":
            return (
                f"关于{stock_name}，在经济衰退期，现金流充裕和低负债的公司更安全。"
                "这个时候不是追求增长的时候，而是要保住资本。"
                "我们应该增加优质债券的配置，为经济复苏储备弹药。"
                "记住，现金在衰退期是王者，但也要为复苏期的机会做准备。"
            )
        elif cycle_stage == "recovery":
            return (
                f"关于{stock_name}，经济复苏期通常是最好的投资时机。"
                "此时应该适度增加股票配置，特别是周期性行业。"
                "但要注意，复苏不意味着没有风险，保持适当的债券配置来平衡组合。"
                "关键是要识别出真正受益于经济复苏的优质企业。"
            )
        else:
            return (
                f"关于{stock_name}，我认为最关键的是理解我们处在经济周期的哪个阶段。"
                "不同的周期阶段需要不同的投资策略和资产配置。"
                "全天候策略的核心是在任何经济环境下都能获得稳定的回报，"
                "通过在不同资产类别间分散来降低风险而不降低收益。"
                "我们需要平衡配置股票、债券、黄金和大宗商品。"
            )
