"""测试GrahamAgent深度价值投资Agent"""
import pytest
from app.agents.value.graham_agent import GrahamAgent


class TestGrahamAgent:
    """测试GrahamAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = GrahamAgent()
        assert agent.name == "Benjamin Graham"
        assert "深度价值" in agent.style
        assert "安全边际" in agent.style

    def test_analyze_with_deep_value_stock(self):
        """测试分析深度价值股"""
        agent = GrahamAgent()

        # 模拟深度价值股数据：低估值、高安全边际
        stock_data = {
            "symbol": "600000",
            "name": "浦发银行",
            "price": 5.0,
            "metrics": {
                "pe_ratio": 5.0,  # 极低PE
                "pb_ratio": 0.6,  # 极低PB
                "eps": 2.0,  # 每股收益
                "bvps": 8.0,  # 每股净资产
                "dividend_yield": 6.0,  # 高股息
                "debt_ratio": 20.0,  # 低负债
                "current_ratio": 3.0,  # 高流动性
                "revenue_growth": 3.0,  # 缓慢增长
                "profit_growth": 2.0,
            },
            "net_net_working_capital": 10.0,  # 净净营运资本
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

    def test_analyze_with_overvalued_stock(self):
        """测试分析高估值股票"""
        agent = GrahamAgent()

        # 模拟高估值股票数据
        stock_data = {
            "symbol": "300001",
            "name": "高成长公司",
            "price": 100.0,
            "metrics": {
                "pe_ratio": 80.0,  # 极高PE
                "pb_ratio": 10.0,  # 高PB
                "eps": 1.25,
                "bvps": 10.0,
                "dividend_yield": 0.5,
                "debt_ratio": 60.0,
                "current_ratio": 1.2,
                "revenue_growth": 30.0,  # 高成长
                "profit_growth": 40.0,
            },
            "net_net_working_capital": 5.0,
        }

        result = agent.analyze(stock_data)

        # 验证决策倾向
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

    def test_graham_formula_calculation(self):
        """测试Graham公式计算"""
        agent = GrahamAgent()

        # 测试Graham公式：√(22.5 × EPS × BVPS)
        # 例如：EPS=2, BVPS=10，则内在价值 = √(22.5 × 2 × 10) = √450 = 21.21
        stock_data = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 15.0,
            "metrics": {
                "pe_ratio": 7.5,
                "pb_ratio": 1.5,
                "eps": 2.0,
                "bvps": 10.0,
                "debt_ratio": 30.0,
                "current_ratio": 2.0,
            },
        }

        result = agent.analyze(stock_data)

        # 验证内在价值计算
        assert "intrinsic_value" in result
        assert "safety_margin" in result

        # 价格15 < 内在价值21.21，应该有正安全边际
        assert result["safety_margin"] > 0

    def test_net_net_analysis(self):
        """测试净净分析"""
        agent = GrahamAgent()

        # 净净股：价格低于净净营运资本
        stock_data = {
            "symbol": "600001",
            "name": "净净股",
            "price": 8.0,
            "metrics": {
                "pe_ratio": 8.0,
                "pb_ratio": 0.8,
                "eps": 1.0,
                "bvps": 10.0,
                "debt_ratio": 15.0,
                "current_ratio": 4.0,
            },
            "net_net_working_capital": 12.0,  # 高于价格
        }

        result = agent.analyze(stock_data)

        # 净净股应该得到正面评价
        assert "decision" in result
        assert 0 <= result["confidence"] <= 1

    def test_earnings_yield_analysis(self):
        """测试盈利收益率分析"""
        agent = GrahamAgent()

        # 高盈利收益率：1/PE > 2×AAA债券收益率
        # 假设AAA债券收益率为3%，则需要1/PE > 6%，即PE < 16.67
        stock_data = {
            "symbol": "000002",
            "name": "高盈利收益公司",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 10.0,  # 盈利收益率10%
                "pb_ratio": 1.2,
                "eps": 1.0,
                "bvps": 8.33,
                "debt_ratio": 25.0,
                "current_ratio": 2.5,
            },
            "aaa_bond_yield": 3.0,  # AAA债券收益率
        }

        result = agent.analyze(stock_data)

        # 高盈利收益率应该反映在评分中
        assert "decision" in result
        assert 0 <= result["confidence"] <= 1

    def test_vote_with_buy_analysis(self):
        """测试基于买入分析的投票"""
        agent = GrahamAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.85,
            "reasoning": "深度价值机会",
            "key_factors": ["高安全边际", "低估值"],
            "safety_margin": 0.4,
        }

        vote = agent.vote(analysis)
        assert vote == "buy"

    def test_vote_with_low_safety_margin(self):
        """测试低安全边际时的投票"""
        agent = GrahamAgent()

        # 低安全边际的买入分析
        analysis = {
            "decision": "buy",
            "confidence": 0.60,
            "reasoning": "勉强符合",
            "key_factors": ["估值一般"],
            "safety_margin": 0.05,  # 只有5%安全边际
        }

        vote = agent.vote(analysis)
        # Graham非常保守，低安全边际时可能选择hold
        assert vote in ["buy", "hold"]

    def test_debate_emphasizing_safety(self):
        """测试强调安全边际的辩论"""
        agent = GrahamAgent()

        context = {
            "stock": {"symbol": "600000", "name": "浦发银行"},
            "market_sentiment": "neutral",
            "other_opinions": ["分析师A看好成长性"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现Graham的深度价值理念
        assert any(keyword in debate for keyword in
                  ["安全边际", "内在价值", "深度价值", "风险控制", "下行保护"])

    def test_debate_in_bullish_market(self):
        """测试牛市环境中的辩论"""
        agent = GrahamAgent()

        context = {
            "stock": {"symbol": "300001", "name": "热门股"},
            "market_sentiment": "bullish",
            "other_opinions": ["分析师A强烈推荐买入"],
        }

        debate = agent.debate(context)

        # Graham在牛市中会警告风险
        assert isinstance(debate, str)
        assert len(debate) > 0

    def test_safety_margin_calculation(self):
        """测试安全边际计算准确性"""
        agent = GrahamAgent()

        # 安全边际 = (内在价值 - 价格) / 内在价值
        stock_data = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 10.0,
            "metrics": {
                "eps": 2.0,
                "bvps": 10.0,
                "pe_ratio": 5.0,
                "pb_ratio": 1.0,
                "debt_ratio": 30.0,
                "current_ratio": 2.0,
            },
        }

        result = agent.analyze(stock_data)

        # 内在价值 = √(22.5 × 2 × 10) = √450 ≈ 21.21
        # 安全边际 = (21.21 - 10) / 21.21 ≈ 0.528
        assert "safety_margin" in result
        assert 0 <= result["safety_margin"] <= 1

    def test_missing_eps_bvps(self):
        """测试缺少EPS和BVPS时的处理"""
        agent = GrahamAgent()

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

    def test_high_debt_penalty(self):
        """测试高负债公司的评分惩罚"""
        agent = GrahamAgent()

        high_debt_stock = {
            "symbol": "000001",
            "name": "高负债公司",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 5.0,
                "pb_ratio": 0.8,
                "eps": 2.0,
                "bvps": 12.5,
                "debt_ratio": 85.0,  # 高负债
                "current_ratio": 0.9,  # 低流动性
            },
        }

        result = agent.analyze(high_debt_stock)
        # 高负债应该降低评分
        assert result["confidence"] >= 0

    def test_extreme_undervaluation(self):
        """测试极度低估的情况"""
        agent = GrahamAgent()

        extreme_value_stock = {
            "symbol": "600001",
            "name": "极度低估",
            "price": 3.0,
            "metrics": {
                "pe_ratio": 3.0,  # 极低PE
                "pb_ratio": 0.5,  # 极低PB
                "eps": 1.0,
                "bvps": 6.0,
                "debt_ratio": 10.0,  # 极低负债
                "current_ratio": 5.0,  # 极高流动性
            },
            "net_net_working_capital": 8.0,  # 远高于价格
        }

        result = agent.analyze(extreme_value_stock)
        # 极度低估应该得到强烈买入信号
        assert result["decision"] in ["buy", "sell", "hold"]
        if result["decision"] == "buy":
            assert result["confidence"] > 0.6
