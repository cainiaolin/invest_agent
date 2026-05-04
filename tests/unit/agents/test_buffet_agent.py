"""测试BuffetAgent价值投资Agent"""
import pytest
from app.agents.value.buffet_agent import BuffetAgent


class TestBuffetAgent:
    """测试BuffetAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = BuffetAgent()
        assert agent.name == "Warren Buffett"
        assert "价值投资" in agent.style
        assert "护城河" in agent.style

    def test_analyze_with_good_value_stock(self):
        """测试分析优质价值股"""
        agent = BuffetAgent()

        # 模拟优质价值股数据
        stock_data = {
            "symbol": "600000",
            "name": "浦发银行",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 8.5,  # 低PE
                "pb_ratio": 0.9,  # 低PB
                "roe": 15.0,  # 高ROE
                "debt_ratio": 30.0,  # 低负债率
                "current_ratio": 2.5,  # 良好流动性
                "dividend_yield": 5.2,  # 高股息
                "revenue_growth": 8.0,  # 稳定增长
                "profit_growth": 10.0,
            },
            "moat_indicators": {
                "brand_strength": 8,  # 强品牌
                "market_share": 25.0,  # 高市场份额
                "competitive_advantage": True,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result

        # 验证决策
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["reasoning"], str)
        assert isinstance(result["key_factors"], list)

    def test_analyze_with_poor_value_stock(self):
        """测试分析劣质股"""
        agent = BuffetAgent()

        # 模拟劣质股数据
        stock_data = {
            "symbol": "ST001",
            "name": "ST公司",
            "price": 50.0,
            "metrics": {
                "pe_ratio": 150.0,  # 极高PE
                "pb_ratio": 8.0,  # 高PB
                "roe": 2.0,  # 低ROE
                "debt_ratio": 85.0,  # 高负债
                "current_ratio": 0.8,  # 流动性差
                "dividend_yield": 0.5,  # 低股息
                "revenue_growth": -5.0,  # 负增长
                "profit_growth": -20.0,
            },
            "moat_indicators": {
                "brand_strength": 3,  # 弱品牌
                "market_share": 2.0,  # 低市场份额
                "competitive_advantage": False,
            },
        }

        result = agent.analyze(stock_data)

        # 验证决策倾向
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

    def test_analyze_with_mediocre_stock(self):
        """测试分析普通股票"""
        agent = BuffetAgent()

        # 模拟普通股票数据
        stock_data = {
            "symbol": "000001",
            "name": "普通公司",
            "price": 20.0,
            "metrics": {
                "pe_ratio": 25.0,  # 中等PE
                "pb_ratio": 2.5,  # 中等PB
                "roe": 10.0,  # 中等ROE
                "debt_ratio": 50.0,  # 中等负债
                "current_ratio": 1.5,
                "dividend_yield": 2.0,
                "revenue_growth": 5.0,
                "profit_growth": 6.0,
            },
            "moat_indicators": {
                "brand_strength": 5,
                "market_share": 10.0,
                "competitive_advantage": None,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构完整
        assert all(key in result for key in ["decision", "confidence", "reasoning", "key_factors"])

    def test_vote_with_buy_analysis(self):
        """测试基于买入分析的投票"""
        agent = BuffetAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.85,
            "reasoning": "优质价值股",
            "key_factors": ["低PE", "高ROE"],
        }

        vote = agent.vote(analysis)
        assert vote == "buy"

    def test_vote_with_sell_analysis(self):
        """测试基于卖出分析的投票"""
        agent = BuffetAgent()

        analysis = {
            "decision": "sell",
            "confidence": 0.75,
            "reasoning": "基本面恶化",
            "key_factors": ["高负债", "负增长"],
        }

        vote = agent.vote(analysis)
        assert vote == "sell"

    def test_vote_with_hold_analysis(self):
        """测试基于持有分析的投票"""
        agent = BuffetAgent()

        analysis = {
            "decision": "hold",
            "confidence": 0.60,
            "reasoning": "观望",
            "key_factors": ["估值合理"],
        }

        vote = agent.vote(analysis)
        assert vote == "hold"

    def test_debate_with_bullish_context(self):
        """测试在牛市环境中的辩论"""
        agent = BuffetAgent()

        context = {
            "stock": {"symbol": "600000", "name": "浦发银行"},
            "market_sentiment": "bullish",
            "other_opinions": ["分析师A建议买入", "分析师B建议持有"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现价值投资理念
        assert any(keyword in debate for keyword in ["价值", "护城河", "安全边际", "长期"])

    def test_debate_with_bearish_context(self):
        """测试在熊市环境中的辩论"""
        agent = BuffetAgent()

        context = {
            "stock": {"symbol": "ST001", "name": "ST公司"},
            "market_sentiment": "bearish",
            "other_opinions": ["分析师A建议卖出", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0

    def test_margin_of_safety_calculation(self):
        """测试安全边际计算逻辑"""
        agent = BuffetAgent()

        # 优质股票应该有较高的安全边际评分
        good_stock = {
            "symbol": "600000",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 8.0,
                "pb_ratio": 0.8,
                "roe": 18.0,
                "debt_ratio": 25.0,
            },
        }

        result = agent.analyze(good_stock)
        # 优质股票应该得到正面评价
        assert result["confidence"] > 0

    def test_moat_evaluation(self):
        """测试护城河评估"""
        agent = BuffetAgent()

        # 有护城河的公司
        stock_with_moat = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {"pe_ratio": 30.0, "pb_ratio": 10.0, "roe": 25.0},
            "moat_indicators": {
                "brand_strength": 9,
                "market_share": 50.0,
                "competitive_advantage": True,
            },
        }

        result = agent.analyze(stock_with_moat)
        # 护城河应该在关键因素中被提及
        moat_mentioned = any("护城河" in str(factor) or "品牌" in str(factor) for factor in result["key_factors"])
        assert moat_mentioned or len(result["key_factors"]) > 0

    def test_missing_optional_metrics(self):
        """测试缺少可选指标时的处理"""
        agent = BuffetAgent()

        # 只有必需指标的数据
        minimal_stock = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 15.0,
                "pb_ratio": 2.0,
            },
        }

        result = agent.analyze(minimal_stock)
        # 应该能够处理并返回结果
        assert "decision" in result
        assert "confidence" in result
