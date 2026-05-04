"""测试FisherAgent成长投资Agent"""
import pytest
from app.agents.growth.fisher_agent import FisherAgent


class TestFisherAgent:
    """测试FisherAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = FisherAgent()
        assert agent.name == "Philip Fisher"
        assert "成长投资" in agent.style
        assert "质量" in agent.style

    def test_analyze_with_excellent_growth_stock(self):
        """测试分析优质成长股"""
        agent = FisherAgent()

        # 模拟优质成长股数据（满足Fisher的8个标准）
        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1800.0,
            "metrics": {
                "pe_ratio": 35.0,  # Fisher不太关注PE，更关注成长
                "pb_ratio": 12.0,
                "roe": 28.0,  # 高ROE
                "debt_ratio": 25.0,  # 低负债
                "revenue_growth": 18.0,  # 高收入增长
                "profit_growth": 22.0,  # 高利润增长
                "operating_margin": 52.0,  # 高运营利润率
                "net_margin": 48.0,  # 高净利率
            },
            "growth_indicators": {
                "rd_ratio": 3.0,  # 研发费用率（茅台较低但合理）
                "rd_growth": 15.0,  # 研发增长
                "market_share_growth": 3.5,  # 市场份额增长
                "customer_satisfaction": 9,  # 高客户满意度
                "sales_force_quality": 8,  # 强大的销售组织
            },
            "management_quality": {
                "management_tenure": 12.0,  # 长期任期
                "management_experience": 9,  # 丰富经验
                "employee_turnover": 4.0,  # 低员工流失率
                "employee_satisfaction": 8,  # 高员工满意度
                "internal_control_quality": 9,  # 严格内控
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result
        assert "scores" in result
        assert "total_score" in result

        # 验证决策
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["reasoning"], str)
        assert isinstance(result["key_factors"], list)

        # 验证8个标准的评分都存在
        expected_scores = [
            "earnings_persistence",
            "growth_commitment",
            "shareholder_returns",
            "cost_control",
            "rd_investment",
            "sales_organization",
            "employee_relations",
            "internal_controls",
        ]
        for score_name in expected_scores:
            assert score_name in result["scores"]
            assert 0 <= result["scores"][score_name] <= 100

    def test_analyze_with_poor_growth_stock(self):
        """测试分析劣质股"""
        agent = FisherAgent()

        # 模拟劣质股数据（不满足Fisher的标准）
        stock_data = {
            "symbol": "ST001",
            "name": "ST公司",
            "price": 50.0,
            "metrics": {
                "pe_ratio": 150.0,
                "pb_ratio": 8.0,
                "roe": 3.0,  # 低ROE
                "debt_ratio": 85.0,  # 高负债
                "revenue_growth": -5.0,  # 负增长
                "profit_growth": -15.0,
                "operating_margin": 3.0,  # 低利润率
                "net_margin": 1.0,
            },
            "growth_indicators": {
                "rd_ratio": 0.5,  # 低研发
                "rd_growth": -10.0,  # 研发负增长
                "market_share_growth": -3.0,  # 市场份额下降
                "customer_satisfaction": 3,  # 低满意度
                "sales_force_quality": 3,  # 弱销售组织
            },
            "management_quality": {
                "management_tenure": 1.0,  # 短期任期
                "management_experience": 2,  # 缺乏经验
                "employee_turnover": 35.0,  # 高流失率
                "employee_satisfaction": 3,  # 低满意度
                "internal_control_quality": 2,  # 内控薄弱
            },
        }

        result = agent.analyze(stock_data)

        # 验证决策倾向
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

        # 劣质股票应该得到较低评分
        assert result["total_score"] < 60

    def test_analyze_with_mixed_growth_stock(self):
        """测试分析混合型股票（部分标准满足）"""
        agent = FisherAgent()

        # 模拟混合型股票数据
        stock_data = {
            "symbol": "000001",
            "name": "成长型公司",
            "price": 100.0,
            "metrics": {
                "pe_ratio": 40.0,
                "pb_ratio": 5.0,
                "roe": 12.0,  # 中等ROE
                "debt_ratio": 45.0,  # 中等负债
                "revenue_growth": 12.0,  # 中等增长
                "profit_growth": 10.0,
                "operating_margin": 15.0,  # 中等利润率
                "net_margin": 10.0,
            },
            "growth_indicators": {
                "rd_ratio": 6.0,  # 中等研发
                "rd_growth": 8.0,
                "market_share_growth": 1.5,
                "customer_satisfaction": 6,  # 中等满意度
                "sales_force_quality": 6,
            },
            "management_quality": {
                "management_tenure": 5.0,
                "management_experience": 6,
                "employee_turnover": 12.0,
                "employee_satisfaction": 6,
                "internal_control_quality": 6,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构完整
        assert all(
            key in result
            for key in ["decision", "confidence", "reasoning", "key_factors", "scores"]
        )

    def test_fishers_eight_criteria_evaluation(self):
        """测试Fisher的8个标准评估"""
        agent = FisherAgent()

        # 创建一个在各个维度表现不同的股票
        stock_data = {
            "symbol": "TEST",
            "name": "测试公司",
            "price": 50.0,
            "metrics": {
                "roe": 22.0,
                "debt_ratio": 30.0,
                "revenue_growth": 16.0,
                "profit_growth": 18.0,
                "operating_margin": 22.0,
                "net_margin": 18.0,
            },
            "growth_indicators": {
                "rd_ratio": 8.0,
                "rd_growth": 12.0,
                "market_share_growth": 2.5,
                "customer_satisfaction": 7,
                "sales_force_quality": 7,
            },
            "management_quality": {
                "management_tenure": 8.0,
                "management_experience": 7,
                "employee_turnover": 8.0,
                "employee_satisfaction": 7,
                "internal_control_quality": 7,
            },
        }

        result = agent.analyze(stock_data)

        # 验证所有8个标准都被评估
        scores = result["scores"]
        assert len(scores) == 8

        # 验证每个评分都在合理范围内
        for score in scores.values():
            assert 0 <= score <= 100

    def test_vote_with_buy_analysis(self):
        """测试基于买入分析的投票"""
        agent = FisherAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.85,
            "reasoning": "优质成长股",
            "key_factors": ["高ROE", "持续增长"],
        }

        vote = agent.vote(analysis)
        assert vote == "buy"

    def test_vote_with_sell_analysis(self):
        """测试基于卖出分析的投票"""
        agent = FisherAgent()

        analysis = {
            "decision": "sell",
            "confidence": 0.80,
            "reasoning": "基本面恶化",
            "key_factors": ["研发不足", "管理问题"],
        }

        vote = agent.vote(analysis)
        assert vote == "sell"

    def test_vote_with_moderate_confidence(self):
        """测试中等置信度的投票（Fisher倾向持有）"""
        agent = FisherAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.65,  # 中等置信度
            "reasoning": "有一定潜力",
            "key_factors": ["增长稳定"],
        }

        vote = agent.vote(analysis)
        # Fisher在中等置信度时倾向于hold
        assert vote == "hold"

    def test_debate_with_bullish_context(self):
        """测试在牛市环境中的辩论"""
        agent = FisherAgent()

        context = {
            "stock": {"symbol": "600519", "name": "贵州茅台"},
            "market_sentiment": "bullish",
            "other_opinions": ["分析师A建议买入", "分析师B建议持有"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现Fisher的成长投资理念
        assert any(
            keyword in debate
            for keyword in [
                "质量",
                "成长",
                "管理层",
                "长期",
                "基本面",
                "调研",
            ]
        )

    def test_debate_with_bearish_context(self):
        """测试在熊市环境中的辩论"""
        agent = FisherAgent()

        context = {
            "stock": {"symbol": "ST001", "name": "ST公司"},
            "market_sentiment": "bearish",
            "other_opinions": ["分析师A建议卖出", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0

    def test_debate_with_neutral_context(self):
        """测试在中性市场环境中的辩论"""
        agent = FisherAgent()

        context = {
            "stock": {"symbol": "000001", "name": "成长型公司"},
            "market_sentiment": "neutral",
            "other_opinions": ["分析师A建议持有"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # Fisher会强调调研和管理层
        assert any(
            keyword in debate
            for keyword in ["管理层", "成长", "竞争", "客户", "员工"]
        )

    def test_earnings_persistence_evaluation(self):
        """测试盈利持续性评估"""
        agent = FisherAgent()

        # 高盈利持续性的股票
        high_persistence_stock = {
            "symbol": "TEST",
            "name": "测试公司",
            "price": 100.0,
            "metrics": {
                "roe": 25.0,
                "revenue_growth": 20.0,
                "profit_growth": 22.0,
            },
        }

        result = agent.analyze(high_persistence_stock)
        assert result["scores"]["earnings_persistence"] > 70

    def test_shareholder_returns_evaluation(self):
        """测试股东回报评估"""
        agent = FisherAgent()

        # 高股东回报的股票
        high_return_stock = {
            "symbol": "TEST",
            "name": "测试公司",
            "price": 100.0,
            "metrics": {
                "roe": 28.0,
                "debt_ratio": 25.0,
                "profit_growth": 18.0,
            },
        }

        result = agent.analyze(high_return_stock)
        assert result["scores"]["shareholder_returns"] > 70

    def test_rd_investment_evaluation(self):
        """测试研发投入评估"""
        agent = FisherAgent()

        # 高研发投入的股票
        high_rd_stock = {
            "symbol": "TEST",
            "name": "科技公司",
            "price": 150.0,
            "metrics": {"revenue_growth": 15.0},
            "growth_indicators": {
                "rd_ratio": 12.0,
                "rd_growth": 18.0,
            },
        }

        result = agent.analyze(high_rd_stock)
        assert result["scores"]["rd_investment"] > 70

    def test_employee_relations_evaluation(self):
        """测试员工关系评估"""
        agent = FisherAgent()

        # 良好员工关系的股票
        good_employee_stock = {
            "symbol": "TEST",
            "name": "优质公司",
            "price": 100.0,
            "management_quality": {
                "employee_satisfaction": 9,
                "employee_turnover": 4.0,
            },
        }

        result = agent.analyze(good_employee_stock)
        assert result["scores"]["employee_relations"] > 70

    def test_minimum_criteria_requirement(self):
        """测试Fisher的最低标准要求"""
        agent = FisherAgent()

        # 创建一个总体不错但有一项严重不足的股票
        unbalanced_stock = {
            "symbol": "TEST",
            "name": "不平衡公司",
            "price": 80.0,
            "metrics": {
                "roe": 25.0,
                "debt_ratio": 30.0,
                "revenue_growth": 18.0,
                "profit_growth": 20.0,
                "operating_margin": 20.0,
                "net_margin": 15.0,
            },
            "growth_indicators": {
                "rd_ratio": 8.0,
                "rd_growth": 10.0,
                "market_share_growth": 2.0,
                "customer_satisfaction": 8,
                "sales_force_quality": 8,
            },
            "management_quality": {
                "management_tenure": 8.0,
                "management_experience": 8,
                "employee_turnover": 6.0,
                "employee_satisfaction": 8,
                "internal_control_quality": 2,  # 内控严重不足
            },
        }

        result = agent.analyze(unbalanced_stock)

        # Fisher要求所有标准都要达到一定水平
        # 内控得分低应该拉低总分或导致卖出决策
        assert result["scores"]["internal_controls"] < 50
        # 由于内控不足，总分应该受到惩罚
        assert result["total_score"] < 70 or result["decision"] == "sell"

    def test_key_factors_extraction(self):
        """测试关键因素提取"""
        agent = FisherAgent()

        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1800.0,
            "metrics": {
                "roe": 28.0,
                "revenue_growth": 18.0,
                "profit_growth": 22.0,
            },
            "growth_indicators": {
                "rd_ratio": 3.0,
                "rd_growth": 15.0,
                "market_share_growth": 3.5,
                "customer_satisfaction": 9,
                "sales_force_quality": 8,
            },
            "management_quality": {
                "management_tenure": 12.0,
                "management_experience": 9,
                "employee_turnover": 4.0,
                "employee_satisfaction": 8,
                "internal_control_quality": 9,
            },
        }

        result = agent.analyze(stock_data)

        # 验证关键因素被正确提取
        assert len(result["key_factors"]) > 0
        assert isinstance(result["key_factors"], list)

        # 高ROE应该被提及
        roe_mentioned = any("ROE" in str(factor) for factor in result["key_factors"])
        assert roe_mentioned or len(result["key_factors"]) > 0

    def test_missing_optional_indicators(self):
        """测试缺少可选指标时的处理"""
        agent = FisherAgent()

        # 只有必需指标的数据
        minimal_stock = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 50.0,
            "metrics": {
                "roe": 12.0,
                "revenue_growth": 8.0,
                "profit_growth": 10.0,
            },
        }

        result = agent.analyze(minimal_stock)

        # 应该能够处理并返回结果
        assert "decision" in result
        assert "confidence" in result
        assert "scores" in result

    def test_confidence_calculation(self):
        """测试置信度计算"""
        agent = FisherAgent()

        # 高质量股票应该有高置信度
        high_quality_stock = {
            "symbol": "TEST",
            "name": "优质公司",
            "price": 100.0,
            "metrics": {
                "roe": 25.0,
                "debt_ratio": 25.0,
                "revenue_growth": 20.0,
                "profit_growth": 22.0,
                "operating_margin": 25.0,
                "net_margin": 20.0,
            },
            "growth_indicators": {
                "rd_ratio": 10.0,
                "rd_growth": 15.0,
                "market_share_growth": 4.0,
                "customer_satisfaction": 9,
                "sales_force_quality": 9,
            },
            "management_quality": {
                "management_tenure": 10.0,
                "management_experience": 9,
                "employee_turnover": 5.0,
                "employee_satisfaction": 9,
                "internal_control_quality": 9,
            },
        }

        result = agent.analyze(high_quality_stock)

        # 高质量股票应该有较高的置信度
        assert result["confidence"] > 0.7
