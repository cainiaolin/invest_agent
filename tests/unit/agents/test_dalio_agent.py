"""测试DalioAgent宏观经济分析Agent"""
import pytest
from app.agents.macro.dalio_agent import (
    DalioAgent,
    EconomicCycleStage,
    DebtCyclePhase,
)


class TestDalioAgent:
    """测试DalioAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = DalioAgent()
        assert agent.name == "Ray Dalio"
        assert "宏观经济" in agent.style
        assert "经济周期" in agent.style

    def test_all_weather_allocation(self):
        """测试全天候策略配置"""
        agent = DalioAgent()

        # 验证全天候配置
        allocation = agent.ALL_WEATHER_ALLOCATION
        assert "stocks" in allocation
        assert "long_term_bonds" in allocation
        assert "mid_term_bonds" in allocation
        assert "gold" in allocation
        assert "commodities" in allocation

        # 验证配置总和为1
        total = sum(allocation.values())
        assert abs(total - 1.0) < 0.01

    def test_analyze_with_recovery_data(self):
        """测试分析经济复苏期数据"""
        agent = DalioAgent()

        # 模拟经济复苏期数据
        stock_data = {
            "symbol": "600000",
            "name": "浦发银行",
            "price": 10.0,
            "macro_indicators": {
                "gdp_growth": 4.5,  # 高增长
                "unemployment_rate": 4.5,  # 低失业
                "pmi": 53,  # PMI扩张
                "capacity_utilization": 78,
                "cpi": 2.5,  # 温和通胀
                "ppi": 2.0,
                "debt_to_gdp": 80,  # 低债务
                "debt_growth": 5,
                "interest_rate": 3.0,  # 低利率
                "credit_growth": 8,
                "fiscal_deficit": 2.5,
                "risk_free_rate": 2.5,
            },
            "company_data": {
                "industry": "金融",
                "cycle_sensitivity": 0.7,  # 周期性
                "pricing_power": 0.6,
                "roe": 15.0,
                "revenue_growth": 12.0,
                "volatility": 25,
                "beta": 1.2,
                "debt_ratio": 40,
                "cash_ratio": 0.15,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result
        assert "cycle_stage" in result
        assert "debt_phase" in result
        assert "inflation_environment" in result
        assert "allocation_weights" in result

        # 验证决策
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1
        assert result["cycle_stage"] == EconomicCycleStage.RECOVERY.value

    def test_analyze_with_inflation_data(self):
        """测试分析通胀期数据"""
        agent = DalioAgent()

        # 模拟通胀期数据
        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "macro_indicators": {
                "gdp_growth": 3.5,
                "unemployment_rate": 4.0,
                "pmi": 51,
                "capacity_utilization": 82,  # 高产能利用
                "cpi": 6.5,  # 高通胀
                "ppi": 8.0,
                "debt_to_gdp": 100,
                "interest_rate": 5.5,
                "risk_free_rate": 4.0,
            },
            "company_data": {
                "industry": "消费",
                "cycle_sensitivity": 0.4,
                "pricing_power": 0.9,  # 强定价权
                "roe": 25.0,
                "revenue_growth": 15.0,
                "volatility": 30,
                "beta": 0.8,
                "debt_ratio": 20,
                "cash_ratio": 0.25,
            },
        }

        result = agent.analyze(stock_data)

        # 验证通胀期识别
        assert result["inflation_environment"] == "high_inflation"
        assert result["cycle_stage"] in [EconomicCycleStage.INFLATION.value, EconomicCycleStage.RECOVERY.value]

    def test_analyze_with_recession_data(self):
        """测试分析衰退期数据"""
        agent = DalioAgent()

        # 模拟衰退期数据
        stock_data = {
            "symbol": "000001",
            "name": "平安银行",
            "price": 15.0,
            "macro_indicators": {
                "gdp_growth": -1.5,  # 负增长
                "unemployment_rate": 8.5,  # 高失业
                "pmi": 46,  # PMI收缩
                "capacity_utilization": 72,
                "cpi": 1.5,  # 低通胀
                "ppi": 1.0,
                "debt_to_gdp": 120,
                "interest_rate": 4.0,
                "credit_growth": -3,  # 信贷收缩
                "risk_free_rate": 3.0,
            },
            "company_data": {
                "industry": "金融",
                "cycle_sensitivity": 0.8,
                "pricing_power": 0.5,
                "roe": 8.0,
                "revenue_growth": -2.0,
                "volatility": 35,
                "beta": 1.5,
                "debt_ratio": 60,
                "cash_ratio": 0.10,
            },
        }

        result = agent.analyze(stock_data)

        # 验证衰退期识别
        assert result["cycle_stage"] == EconomicCycleStage.RECESSION.value
        assert result["inflation_environment"] in ["low_inflation", "moderate_inflation"]

    def test_analyze_with_depression_data(self):
        """测试分析萧条期数据"""
        agent = DalioAgent()

        # 模拟萧条期数据
        stock_data = {
            "symbol": "ST001",
            "name": "ST公司",
            "price": 5.0,
            "macro_indicators": {
                "gdp_growth": -4.0,  # 严重负增长
                "unemployment_rate": 12.0,  # 极高失业
                "pmi": 42,  # PMI严重收缩
                "capacity_utilization": 65,
                "cpi": -0.5,  # 通缩
                "ppi": -1.0,
                "debt_to_gdp": 180,
                "interest_rate": 2.0,
                "credit_growth": -8,
                "risk_free_rate": 1.5,
            },
            "company_data": {
                "industry": "制造",
                "cycle_sensitivity": 0.9,
                "pricing_power": 0.3,
                "roe": -5.0,
                "revenue_growth": -15.0,
                "volatility": 50,
                "beta": 2.0,
                "debt_ratio": 80,
                "cash_ratio": 0.05,
            },
        }

        result = agent.analyze(stock_data)

        # 验证萧条期识别
        assert result["cycle_stage"] == EconomicCycleStage.DEPRESSION.value
        assert result["inflation_environment"] in ["deflation", "low_inflation"]

    def test_identify_economic_cycle_stages(self):
        """测试经济周期阶段识别"""
        agent = DalioAgent()

        # 测试不同阶段的经济数据
        test_cases = [
            # (macro_data, expected_stage)
            (
                {"gdp_growth": 4.0, "unemployment_rate": 4.0, "pmi": 54, "capacity_utilization": 77},
                EconomicCycleStage.RECOVERY
            ),
            (
                {"gdp_growth": 2.5, "unemployment_rate": 4.5, "pmi": 51, "capacity_utilization": 82},
                EconomicCycleStage.INFLATION
            ),
            (
                {"gdp_growth": -0.5, "unemployment_rate": 8.0, "pmi": 47, "capacity_utilization": 74},
                EconomicCycleStage.RECESSION
            ),
            (
                {"gdp_growth": -3.0, "unemployment_rate": 10.0, "pmi": 43, "capacity_utilization": 68},
                EconomicCycleStage.DEPRESSION
            ),
        ]

        for macro_data, expected_stage in test_cases:
            stage = agent._identify_economic_cycle_stage(macro_data)
            assert stage == expected_stage, f"Expected {expected_stage}, got {stage} for {macro_data}"

    def test_identify_debt_cycle_phases(self):
        """测试债务周期阶段识别"""
        agent = DalioAgent()

        # 测试不同阶段的债务数据
        test_cases = [
            # (macro_data, expected_phase)
            (
                {"debt_to_gdp": 80, "debt_growth": 5, "interest_rate": 2.5, "credit_growth": 12},
                DebtCyclePhase.SHORT_TERM_EXPANSION
            ),
            (
                {"debt_to_gdp": 150, "debt_growth": -5, "interest_rate": 6.0, "credit_growth": -8},
                DebtCyclePhase.SHORT_TERM_CONTRACTION
            ),
            (
                {"debt_to_gdp": 350, "debt_growth": 20, "interest_rate": 5.0, "credit_growth": 8},
                DebtCyclePhase.LONG_TERM_DEBT_CRISIS
            ),
            (
                {"debt_to_gdp": 280, "debt_growth": -10, "interest_rate": 4.0, "credit_growth": -12},
                DebtCyclePhase.DEBT_DELEVERAGING
            ),
        ]

        for macro_data, expected_phase in test_cases:
            phase = agent._identify_debt_cycle_phase(macro_data)
            assert phase == expected_phase, f"Expected {expected_phase}, got {phase} for {macro_data}"

    def test_assess_inflation_environment(self):
        """测试通胀环境评估"""
        agent = DalioAgent()

        # 测试不同通胀环境
        test_cases = [
            # (macro_data, expected_environment)
            ({"cpi": 7.0, "ppi": 6.0}, "high_inflation"),
            ({"cpi": 3.5, "ppi": 3.0}, "moderate_inflation"),
            ({"cpi": 1.0, "ppi": 0.5}, "low_inflation"),
            ({"cpi": -0.5, "ppi": -1.0}, "deflation"),
        ]

        for macro_data, expected_env in test_cases:
            env = agent._assess_inflation_environment(macro_data)
            assert env == expected_env, f"Expected {expected_env}, got {env} for {macro_data}"

    def test_allocation_weights_adjustment(self):
        """测试资产配置权重调整"""
        agent = DalioAgent()

        # 测试不同经济环境下的配置调整
        test_cases = [
            # (cycle_stage, inflation_env, check_function)
            (
                EconomicCycleStage.RECOVERY,
                "moderate_inflation",
                lambda weights: weights["stocks"] > 0.35  # 复苏期增加股票
            ),
            (
                EconomicCycleStage.INFLATION,
                "high_inflation",
                lambda weights: weights["commodities"] > 0.10  # 通胀期增加商品
            ),
            (
                EconomicCycleStage.RECESSION,
                "moderate_inflation",
                lambda weights: weights["long_term_bonds"] > 0.45  # 衰退期增加债券
            ),
        ]

        for cycle_stage, inflation_env, check_func in test_cases:
            weights = agent._calculate_allocation_weights(cycle_stage, inflation_env)
            # 验证权重总和为1
            assert abs(sum(weights.values()) - 1.0) < 0.01
            # 验证特定环境的配置调整
            assert check_func(weights), f"Allocation check failed for {cycle_stage}, {inflation_env}"

    def test_vote_with_recession_context(self):
        """测试衰退期投票决策"""
        agent = DalioAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.75,
            "scores": {"risk_adjusted_return": 70, "cycle_timing": 60},
            "cycle_stage": "recession",
        }

        vote = agent.vote(analysis)
        # 衰退期应该更保守，中等置信度不会买入
        assert vote == "hold"

    def test_vote_with_recovery_context(self):
        """测试复苏期投票决策"""
        agent = DalioAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.75,
            "scores": {"risk_adjusted_return": 80, "cycle_timing": 75},
            "cycle_stage": "recovery",
        }

        vote = agent.vote(analysis)
        # 复苏期高置信度应该买入
        assert vote == "buy"

    def test_debate_with_inflation_context(self):
        """测试通胀环境辩论"""
        agent = DalioAgent()

        context = {
            "stock": {"symbol": "600519", "name": "贵州茅台"},
            "macro_context": {"cycle_stage": "inflation"},
            "other_opinions": ["分析师A建议持有", "分析师B建议买入"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现宏观经济理念
        assert any(keyword in debate for keyword in ["定价能力", "通胀", "分散", "配置"])

    def test_debate_with_recession_context(self):
        """测试衰退环境辩论"""
        agent = DalioAgent()

        context = {
            "stock": {"symbol": "000001", "name": "平安银行"},
            "macro_context": {"cycle_stage": "recession"},
            "other_opinions": ["分析师A建议卖出", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0

    def test_debate_with_default_context(self):
        """测试默认环境辩论"""
        agent = DalioAgent()

        context = {
            "stock": {"symbol": "600000", "name": "浦发银行"},
            "other_opinions": ["分析师A建议买入"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证全天候策略理念
        assert any(keyword in debate for keyword in ["全天候", "分散", "周期", "配置"])

    def test_cycle_fitness_calculation(self):
        """测试周期适应度计算"""
        agent = DalioAgent()

        # 测试复苏期周期性公司
        company_data = {
            "industry": "周期性",
            "cycle_sensitivity": 0.8,
            "pricing_power": 0.6,
            "debt_ratio": 40,
            "cash_ratio": 0.15,
        }

        fitness = agent._calculate_cycle_fitness(
            company_data,
            EconomicCycleStage.RECOVERY,
            DebtCyclePhase.SHORT_TERM_EXPANSION,
            "moderate_inflation"
        )

        # 周期性公司在复苏期应该有较高适应度
        assert fitness > 50

    def test_risk_adjusted_return_calculation(self):
        """测试风险调整收益计算"""
        agent = DalioAgent()

        company_data = {
            "roe": 20.0,
            "revenue_growth": 15.0,
            "volatility": 20,
            "beta": 0.9,
            "debt_ratio": 30,
        }

        macro_data = {
            "risk_free_rate": 3.0,
        }

        risk_return = agent._calculate_risk_adjusted_return(company_data, macro_data)

        # 高ROE低波动应该有较高的风险调整收益
        assert 0 <= risk_return <= 100

    def test_missing_macro_data(self):
        """测试缺少宏观数据时的处理"""
        agent = DalioAgent()

        # 最少数据
        minimal_data = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 10.0,
            "macro_indicators": {
                "gdp_growth": 2.0,
            },
            "company_data": {
                "industry": "金融",
            },
        }

        result = agent.analyze(minimal_data)

        # 应该能够处理并返回结果
        assert "decision" in result
        assert "confidence" in result
        assert "cycle_stage" in result

    def test_comprehensive_analysis(self):
        """测试综合分析能力"""
        agent = DalioAgent()

        # 完整的经济数据
        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "macro_indicators": {
                "gdp_growth": 3.0,
                "unemployment_rate": 5.0,
                "pmi": 50,
                "capacity_utilization": 76,
                "cpi": 2.5,
                "ppi": 2.0,
                "debt_to_gdp": 90,
                "debt_growth": 6,
                "interest_rate": 3.5,
                "credit_growth": 7,
                "fiscal_deficit": 3.0,
                "risk_free_rate": 2.8,
            },
            "company_data": {
                "industry": "消费",
                "cycle_sensitivity": 0.3,
                "pricing_power": 0.95,
                "roe": 25.0,
                "revenue_growth": 12.0,
                "volatility": 25,
                "beta": 0.7,
                "debt_ratio": 15,
                "cash_ratio": 0.30,
            },
        }

        result = agent.analyze(stock_data)

        # 验证分析结果的完整性
        assert all(key in result for key in [
            "decision", "confidence", "reasoning", "key_factors",
            "scores", "total_score", "cycle_stage", "debt_phase",
            "inflation_environment", "allocation_weights"
        ])

        # 验证评分系统
        assert all(0 <= score <= 100 for score in result["scores"].values())
        assert 0 <= result["total_score"] <= 100

        # 验证资产配置
        assert all(0 <= weight <= 1 for weight in result["allocation_weights"].values())
        assert abs(sum(result["allocation_weights"].values()) - 1.0) < 0.01
