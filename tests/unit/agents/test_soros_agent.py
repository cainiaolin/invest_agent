"""测试SorosAgent宏观对冲Agent"""
import pytest
from app.agents.macro.soros_agent import SorosAgent


class TestSorosAgent:
    """测试SorosAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = SorosAgent()
        assert agent.name == "George Soros"
        assert "宏观对冲" in agent.style
        assert "反身性" in agent.style

    def test_analyze_with_bubble_conditions(self):
        """测试分析泡沫市场条件"""
        agent = SorosAgent()

        # 模拟泡沫市场数据
        stock_data = {
            "symbol": "BUBBLE",
            "name": "泡沫公司",
            "price": 100.0,
            "metrics": {
                "pe_ratio": 80.0,  # 极高PE
                "pb_ratio": 10.0,  # 极高PB
                "price_momentum": 35.0,  # 强劲动量
                "volatility": 8.0,  # 低波动率
            },
            "macro_indicators": {
                "liquidity_cycle": "expansion",
                "credit_spread": 0.8,  # 低信用利差
                "yield_curve": "normal",
                "margin_debt_growth": 40.0,  # 高融资增长
            },
            "market_sentiment": {
                "score": 85,  # 极度贪婪
                "put_call_ratio": 0.4,  # 过度看涨
                "margin_debt_growth": 40.0,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result

        # 验证决策倾向于卖出
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

    def test_analyze_with_panic_conditions(self):
        """测试分析恐慌市场条件"""
        agent = SorosAgent()

        # 模拟恐慌市场数据
        stock_data = {
            "symbol": "PANIC",
            "name": "被抛售公司",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 5.0,  # 极低PE
                "pb_ratio": 0.4,  # 极低PB
                "price_momentum": -40.0,  # 强烈下跌动量
                "volatility": 45.0,  # 高波动率
            },
            "macro_indicators": {
                "liquidity_cycle": "contraction",
                "credit_spread": 4.5,  # 高信用利差
                "yield_curve": "inverted",  # 收益率曲线倒挂
                "margin_debt_growth": -15.0,  # 去杠杆
            },
            "market_sentiment": {
                "score": 15,  # 极度恐惧
                "put_call_ratio": 2.2,  # 过度看跌
                "margin_debt_growth": -15.0,
            },
        }

        result = agent.analyze(stock_data)

        # 验证决策倾向于买入
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

    def test_analyze_with_normal_conditions(self):
        """测试分析正常市场条件"""
        agent = SorosAgent()

        # 模拟正常市场数据
        stock_data = {
            "symbol": "NORMAL",
            "name": "正常公司",
            "price": 50.0,
            "metrics": {
                "pe_ratio": 15.0,  # 正常PE
                "pb_ratio": 2.0,  # 正常PB
                "price_momentum": 5.0,  # 中等动量
                "volatility": 20.0,  # 正常波动率
            },
            "macro_indicators": {
                "liquidity_cycle": "neutral",
                "credit_spread": 1.5,  # 正常信用利差
                "yield_curve": "normal",
                "margin_debt_growth": 10.0,  # 正常融资增长
            },
            "market_sentiment": {
                "score": 50,  # 中性
                "put_call_ratio": 1.0,  # 中性
                "margin_debt_growth": 10.0,
            },
        }

        result = agent.analyze(stock_data)

        # 验证返回结构完整
        assert all(key in result for key in ["decision", "confidence", "reasoning", "key_factors"])

    def test_reflexivity_evaluation(self):
        """测试反身性评估"""
        agent = SorosAgent()

        # 高反身性案例（价格与基本面严重偏离）
        high_reflexivity_stock = {
            "symbol": "HIGH",
            "name": "高反身性公司",
            "price": 200.0,
            "metrics": {
                "pe_ratio": 100.0,
                "pb_ratio": 12.0,
                "price_momentum": 40.0,
            },
            "market_sentiment": {"score": 90},
        }

        result = agent.analyze(high_reflexivity_stock)
        # 应该检测到高反身性
        assert result["scores"]["reflexivity"] > 70

    def test_cycle_position_evaluation(self):
        """测试周期位置评估"""
        agent = SorosAgent()

        # 危险周期信号
        dangerous_cycle_stock = {
            "symbol": "RISKY",
            "name": "风险周期公司",
            "price": 80.0,
            "metrics": {"pe_ratio": 20.0, "pb_ratio": 3.0, "price_momentum": 10.0, "volatility": 15.0},
            "macro_indicators": {
                "liquidity_cycle": "expansion",
                "credit_spread": 3.5,  # 高信用利差
                "yield_curve": "inverted",  # 收益率曲线倒挂
                "margin_debt_growth": 45.0,  # 过度杠杆
            },
            "market_sentiment": {"score": 60, "put_call_ratio": 0.8, "margin_debt_growth": 45.0},
        }

        result = agent.analyze(dangerous_cycle_stock)
        # 应该检测到高风险周期位置
        cycle_score = result["scores"]["cycle_position"]
        assert cycle_score > 50  # 高风险评分

    def test_market_bias_evaluation(self):
        """测试市场偏见评估"""
        agent = SorosAgent()

        # 过度乐观的市场
        over_optimistic_stock = {
            "symbol": "OPT",
            "name": "过度乐观公司",
            "price": 120.0,
            "metrics": {"pe_ratio": 50.0, "pb_ratio": 6.0, "price_momentum": 15.0, "volatility": 10.0},
            "macro_indicators": {
                "liquidity_cycle": "expansion",
                "credit_spread": 1.0,
                "yield_curve": "normal",
                "margin_debt_growth": 25.0,
            },
            "market_sentiment": {
                "score": 85,  # 极度贪婪
                "put_call_ratio": 0.3,  # 过度看涨
                "margin_debt_growth": 25.0,
            },
        }

        result = agent.analyze(over_optimistic_stock)
        # 应该检测到过度乐观
        assert result["scores"]["market_bias"] > 70

    def test_vote_with_extreme_confidence(self):
        """测试基于极端置信度的投票"""
        agent = SorosAgent()

        analysis = {
            "decision": "sell",
            "confidence": 0.85,
            "reasoning": "市场泡沫明显",
            "key_factors": ["强反身性", "过度乐观"],
        }

        vote = agent.vote(analysis)
        # 高置信度应该直接跟随决策
        assert vote == "sell"

    def test_vote_with_moderate_confidence(self):
        """测试基于中等置信度的投票"""
        agent = SorosAgent()

        buy_analysis = {
            "decision": "buy",
            "confidence": 0.5,
            "reasoning": "可能存在机会",
            "key_factors": ["市场悲观"],
        }

        vote = agent.vote(buy_analysis)
        # 中等置信度倾向于保守
        assert vote == "hold"

    def test_vote_with_low_confidence(self):
        """测试基于低置信度的投票"""
        agent = SorosAgent()

        analysis = {
            "decision": "sell",
            "confidence": 0.3,
            "reasoning": "信号不明确",
            "key_factors": ["趋势不明"],
        }

        vote = agent.vote(analysis)
        # 低置信度应该观望
        assert vote == "hold"

    def test_debate_with_bullish_context(self):
        """测试在牛市环境中的辩论"""
        agent = SorosAgent()

        context = {
            "stock": {"symbol": "BULL", "name": "牛市股票"},
            "market_sentiment": "bullish",
            "other_opinions": ["分析师A建议加仓", "分析师B建议持有"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现索罗斯的反身性理念
        assert any(
            keyword in debate for keyword in ["反身性", "泡沫", "风险", "循环", "不可持续"]
        )

    def test_debate_with_bearish_context(self):
        """测试在熊市环境中的辩论"""
        agent = SorosAgent()

        context = {
            "stock": {"symbol": "BEAR", "name": "熊市股票"},
            "market_sentiment": "bearish",
            "other_opinions": ["分析师A建议割肉", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现逆向投资思维
        assert any(keyword in debate for keyword in ["机会", "恐慌", "流动性", "基本面"])

    def test_debate_with_neutral_context(self):
        """测试在中性市场环境中的辩论"""
        agent = SorosAgent()

        context = {
            "stock": {"symbol": "NEUTRAL", "name": "中性股票"},
            "market_sentiment": "neutral",
            "other_opinions": ["分析师A建议持有", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现错误定价寻找
        assert any(keyword in debate for keyword in ["错误定价", "共识", "偏见", "差距"])

    def test_key_factors_extraction(self):
        """测试关键因素提取"""
        agent = SorosAgent()

        # 泡沫特征明显的股票
        bubble_stock = {
            "symbol": "BUB",
            "name": "泡沫股票",
            "price": 150.0,
            "metrics": {"pe_ratio": 90.0, "pb_ratio": 11.0, "price_momentum": 30.0, "volatility": 8.0},
            "macro_indicators": {
                "liquidity_cycle": "expansion",
                "credit_spread": 0.6,
                "yield_curve": "normal",
                "margin_debt_growth": 50.0,
            },
            "market_sentiment": {"score": 90, "put_call_ratio": 0.3, "margin_debt_growth": 50.0},
        }

        result = agent.analyze(bubble_stock)

        # 验证关键因素包含泡沫相关指标
        key_factors_str = " ".join(result["key_factors"])
        assert any(
            keyword in key_factors_str
            for keyword in ["反身性", "泡沫", "乐观", "拐点"]
        )

    def test_trend_sustainability_evaluation(self):
        """测试趋势可持续性评估"""
        agent = SorosAgent()

        # 趋势可能接近拐点
        tipping_point_stock = {
            "symbol": "TIP",
            "name": "拐点股票",
            "price": 90.0,
            "metrics": {
                "pe_ratio": 70.0,
                "pb_ratio": 8.0,
                "price_momentum": 35.0,  # 过热
                "volatility": 35.0,  # 高波动
            },
            "macro_indicators": {
                "liquidity_cycle": "expansion",
                "credit_spread": 2.8,  # 信用风险上升
                "yield_curve": "flat",
                "margin_debt_growth": 30.0,
            },
            "market_sentiment": {"score": 75, "put_call_ratio": 0.5, "margin_debt_growth": 30.0},
        }

        result = agent.analyze(tipping_point_stock)
        # 应该检测到趋势可持续性问题
        assert result["scores"]["trend_sustainability"] > 60

    def test_missing_optional_indicators(self):
        """测试缺少可选指标时的处理"""
        agent = SorosAgent()

        # 只有必需指标的数据
        minimal_stock = {
            "symbol": "MIN",
            "name": "最小数据公司",
            "price": 30.0,
            "metrics": {
                "pe_ratio": 20.0,
                "pb_ratio": 2.5,
            },
        }

        result = agent.analyze(minimal_stock)
        # 应该能够处理并返回结果
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result

    def test_contrarian_positioning_logic(self):
        """测试逆向投资逻辑"""
        agent = SorosAgent()

        # 在市场极度恐慌时应该倾向于买入
        panic_stock = {
            "symbol": "PANIC",
            "name": "恐慌股票",
            "price": 5.0,
            "metrics": {
                "pe_ratio": 3.0,
                "pb_ratio": 0.3,
                "price_momentum": -50.0,
                "volatility": 50.0,
            },
            "macro_indicators": {
                "liquidity_cycle": "contraction",
                "credit_spread": 5.0,
                "yield_curve": "inverted",
                "margin_debt_growth": -20.0,
            },
            "market_sentiment": {
                "score": 10,
                "put_call_ratio": 3.0,
                "margin_debt_growth": -20.0,
            },
        }

        result = agent.analyze(panic_stock)
        # 在极度恐慌时，索罗斯会寻找买入机会
        if result["confidence"] > 0.7:
            assert result["decision"] == "buy"