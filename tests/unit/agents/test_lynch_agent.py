"""测试LynchAgent GARP投资Agent"""
import pytest
from app.agents.growth.lynch_agent import LynchAgent


class TestLynchAgent:
    """测试LynchAgent实现"""

    def test_agent_properties(self):
        """测试Agent基本属性"""
        agent = LynchAgent()
        assert agent.name == "Peter Lynch"
        assert "GARP" in agent.style
        assert "合理价格" in agent.style
        assert "增长" in agent.style

    def test_selection_criteria(self):
        """测试13个选股标准"""
        agent = LynchAgent()
        assert len(agent.SELECTION_CRITERIA) == 13
        assert "低PEG比率" in agent.SELECTION_CRITERIA
        assert "内部人买入" in agent.SELECTION_CRITERIA
        assert "回购股票" in agent.SELECTION_CRITERIA

    def test_stock_categories(self):
        """测试股票分类"""
        agent = LynchAgent()
        assert "fast_grower" in agent.STOCK_CATEGORIES
        assert "stalwart" in agent.STOCK_CATEGORIES
        assert "turnaround" in agent.STOCK_CATEGORIES

    def test_analyze_perfect_garp_stock(self):
        """测试分析完美GARP股票"""
        agent = LynchAgent()

        # 模拟完美的GARP股票
        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 25.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                "revenue_growth": 20.0,
                "profit_growth": 25.0,
                "dividend_yield": 2.5,
            },
            "business_info": {
                "product_familiarity": 9,
                "brand_recognition": 10,
                "is_consumer_business": True,
                "market_cap": 2_000_000_000_000,
                "market_size": 500_000_000_000,
                "competitive_position": 9,
                "has_moat": True,
                "is_growth_industry": True,
                "has_essential_product": True,
            },
            "insider_info": {
                "insider_buying": True,
                "share_buyback": True,
            }
        }

        result = agent.analyze(stock_data)

        # 验证返回结构
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert "key_factors" in result
        assert "peg_ratio" in result
        assert "category" in result

        # 验证决策
        assert result["decision"] in ["buy", "sell", "hold"]
        assert 0 <= result["confidence"] <= 1

        # 验证PEG计算
        expected_peg = 25.0 / 25.0  # PE / 增长率
        assert result["peg_ratio"] == expected_peg

    def test_analyze_overvalued_growth_stock(self):
        """测试分析高估成长股"""
        agent = LynchAgent()

        # 模拟高估的成长股
        stock_data = {
            "symbol": "300001",
            "name": "高估科技股",
            "price": 100.0,
            "metrics": {
                "pe_ratio": 100.0,
                "pb_ratio": 15.0,
                "roe": 10.0,
                "debt_ratio": 40.0,
                "revenue_growth": 20.0,
                "profit_growth": 15.0,
                "dividend_yield": 0.5,
            },
            "business_info": {
                "product_familiarity": 7,
                "brand_recognition": 6,
                "is_consumer_business": True,
                "market_cap": 50_000_000_000,
                "has_moat": False,
                "is_tech_leader": False,
            },
            "insider_info": {
                "insider_buying": False,
                "share_buyback": False,
            }
        }

        result = agent.analyze(stock_data)

        # 高PEG应该导致负面评价
        expected_peg = 100.0 / 15.0  # 高PEG
        assert result["peg_ratio"] == expected_peg
        assert expected_peg > 3.0  # 确认是高PEG

        # 验证决策倾向
        assert result["decision"] in ["buy", "sell", "hold"]

    def test_analyze_fast_grower_small_cap(self):
        """测试分析小盘快速成长股（十倍股潜力）"""
        agent = LynchAgent()

        # 模拟小盘快速成长股
        stock_data = {
            "symbol": "688XXX",
            "name": "科创板新秀",
            "price": 50.0,
            "metrics": {
                "pe_ratio": 30.0,
                "pb_ratio": 5.0,
                "roe": 18.0,
                "debt_ratio": 30.0,
                "revenue_growth": 35.0,
                "profit_growth": 30.0,
                "dividend_yield": 0.0,
            },
            "business_info": {
                "product_familiarity": 8,
                "brand_recognition": 5,
                "is_consumer_business": True,
                "market_cap": 5_000_000_000,  # 50亿市值
                "market_size": 200_000_000_000,
                "competitive_position": 7,
                "has_moat": True,
                "is_growth_industry": True,
                "is_tech_leader": True,
            },
            "insider_info": {
                "insider_buying": True,
                "share_buyback": False,
            }
        }

        result = agent.analyze(stock_data)

        # 验证PEG合理
        expected_peg = 30.0 / 30.0  # PEG = 1
        assert result["peg_ratio"] == expected_peg

        # 验证被分类为快速成长股
        assert "快速" in result["category"] or "增长" in result["category"]

        # 验证十倍股潜力得分较高
        assert result["scores"]["tenbagger"] > 60

    def test_analyze_turnaround_stock(self):
        """测试分析困境反转股"""
        agent = LynchAgent()

        # 模拟困境反转股
        stock_data = {
            "symbol": "ST002",
            "name": "转型公司",
            "price": 5.0,
            "metrics": {
                "pe_ratio": 50.0,
                "pb_ratio": 1.2,
                "roe": 2.0,
                "debt_ratio": 60.0,
                "revenue_growth": -10.0,  # 负增长
                "profit_growth": -5.0,
                "dividend_yield": 0.0,
            },
            "business_info": {
                "product_familiarity": 6,
                "brand_recognition": 5,
                "is_consumer_business": True,
                "market_cap": 3_000_000_000,
                "is_turnaround": True,  # 标记为困境反转
                "has_moat": False,
            },
            "insider_info": {
                "insider_buying": True,
                "share_buyback": False,
            }
        }

        result = agent.analyze(stock_data)

        # 困境反转股的PEG可能为无穷大（负增长）
        assert result["peg_ratio"] == float('inf')

        # 应该被分类为困境反转股
        assert "反转" in result["category"]

    def test_analyze_slow_grower_with_dividend(self):
        """测试分析慢速增长但有股息的股票"""
        agent = LynchAgent()

        # 模拟慢速增长股
        stock_data = {
            "symbol": "600000",
            "name": "银行股",
            "price": 5.0,
            "metrics": {
                "pe_ratio": 6.0,
                "pb_ratio": 0.6,
                "roe": 12.0,
                "debt_ratio": 50.0,
                "revenue_growth": 3.0,
                "profit_growth": 5.0,
                "dividend_yield": 5.0,  # 高股息
            },
            "business_info": {
                "product_familiarity": 10,
                "brand_recognition": 9,
                "is_consumer_business": True,
                "market_cap": 100_000_000_000,
                "has_moat": True,
            },
            "insider_info": {
                "insider_buying": False,
                "share_buyback": True,
            }
        }

        result = agent.analyze(stock_data)

        # 验证PEG合理
        expected_peg = 6.0 / 5.0  # PEG = 1.2
        assert result["peg_ratio"] == expected_peg

        # 应该被分类为慢速增长股
        assert "慢速" in result["category"] or "增长" in result["category"]

    def test_peg_calculation(self):
        """测试PEG比率计算"""
        agent = LynchAgent()

        # 正常情况
        peg = agent._calculate_peg(20.0, 20.0)
        assert peg == 1.0

        # 低PEG
        peg = agent._calculate_peg(10.0, 20.0)
        assert peg == 0.5

        # 高PEG
        peg = agent._calculate_peg(30.0, 10.0)
        assert peg == 3.0

        # 负增长
        peg = agent._calculate_peg(20.0, -5.0)
        assert peg == float('inf')

    def test_peg_evaluation(self):
        """测试PEG评分"""
        agent = LynchAgent()

        # PEG < 1 应该高分
        score = agent._evaluate_peg(0.5)
        assert score >= 80

        # PEG = 1 应该中等偏上
        score = agent._evaluate_peg(1.0)
        assert score >= 70

        # PEG > 2 应该低分
        score = agent._evaluate_peg(2.5)
        assert score <= 40

        # 负增长应该最低分
        score = agent._evaluate_peg(float('inf'))
        assert score == 0

    def test_tenbagger_potential(self):
        """测试十倍股潜力评估"""
        agent = LynchAgent()

        # 小盘 + 高增长 + 大市场
        business_info = {
            "market_cap": 5_000_000_000,  # 50亿
            "market_size": 1_000_000_000_000,  # 万亿市场
            "competitive_position": 9
        }
        score = agent._evaluate_tenbagger_potential({}, business_info)
        assert score >= 70

        # 大盘股
        business_info = {
            "market_cap": 500_000_000_000,  # 5000亿
            "market_size": 100_000_000_000,
            "competitive_position": 7
        }
        score = agent._evaluate_tenbagger_potential({}, business_info)
        assert score < 70

    def test_familiarity_evaluation(self):
        """测试熟悉度评估"""
        agent = LynchAgent()

        # 高熟悉度
        business_info = {
            "product_familiarity": 9,
            "brand_recognition": 9,
            "is_consumer_business": True
        }
        score = agent._evaluate_familiarity(business_info)
        assert score >= 80

        # 低熟悉度
        business_info = {
            "product_familiarity": 2,
            "brand_recognition": 2,
            "is_consumer_business": False
        }
        score = agent._evaluate_familiarity(business_info)
        assert score < 70

    def test_lynch_criteria_evaluation(self):
        """测试13个选股标准评估"""
        agent = LynchAgent()

        # 符合多项标准
        business_info = {
            "has_boring_name": True,
            "has_boring_business": True,
            "is_distasteful": False,
            "has_ignored_subsidiary": True,
            "institutional_ownership": 20,  # 低机构持股
            "has_rumors": True,
            "is_growth_industry": True,
            "has_moat": True,
            "has_essential_product": True,
            "is_tech_leader": True,
        }
        insider_info = {
            "insider_buying": True,
            "share_buyback": True
        }

        score = agent._evaluate_lynch_criteria(business_info, insider_info)
        # 应该符合多项标准，得分较高
        assert score > 50

    def test_vote_with_buy_analysis(self):
        """测试基于买入分析的投票"""
        agent = LynchAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.75,
            "reasoning": "GARP策略推荐买入",
            "key_factors": ["低PEG", "高增长"],
        }

        vote = agent.vote(analysis)
        assert vote == "buy"

    def test_vote_with_low_confidence(self):
        """测试低置信度投票"""
        agent = LynchAgent()

        analysis = {
            "decision": "buy",
            "confidence": 0.5,
            "reasoning": "中等机会",
            "key_factors": ["PEG合理"],
        }

        vote = agent.vote(analysis)
        assert vote == "hold"

    def test_debate_with_bullish_context(self):
        """测试在牛市环境中的辩论"""
        agent = LynchAgent()

        context = {
            "stock": {"symbol": "600519", "name": "贵州茅台"},
            "market_sentiment": "bullish",
            "other_opinions": ["分析师A推荐买入", "分析师B认为合理"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证辩论内容体现GARP理念
        assert any(keyword in debate for keyword in ["PEG", "熟悉", "增长", "日常生活"])

    def test_debate_with_bearish_context(self):
        """测试在熊市环境中的辩论"""
        agent = LynchAgent()

        context = {
            "stock": {"symbol": "300001", "name": "科技股"},
            "market_sentiment": "bearish",
            "other_opinions": ["分析师A建议卖出", "分析师B建议观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0

    def test_debate_with_neutral_context(self):
        """测试在中性环境中的辩论"""
        agent = LynchAgent()

        context = {
            "stock": {"symbol": "688XXX", "name": "科创板公司"},
            "market_sentiment": "neutral",
            "other_opinions": ["分析师A持有", "分析师B观望"],
        }

        debate = agent.debate(context)

        assert isinstance(debate, str)
        assert len(debate) > 0
        # 验证提到了关键问题
        assert "PEG" in debate

    def test_missing_optional_metrics(self):
        """测试缺少可选指标时的处理"""
        agent = LynchAgent()

        # 只有必需指标的数据
        minimal_stock = {
            "symbol": "000001",
            "name": "测试公司",
            "price": 10.0,
            "metrics": {
                "pe_ratio": 15.0,
                "pb_ratio": 2.0,
                "profit_growth": 10.0,
            },
        }

        result = agent.analyze(minimal_stock)
        # 应该能够处理并返回结果
        assert "decision" in result
        assert "confidence" in result
        assert "peg_ratio" in result

    def test_key_factors_extraction(self):
        """测试关键因素提取"""
        agent = LynchAgent()

        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 20.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                "revenue_growth": 20.0,
                "profit_growth": 25.0,
                "dividend_yield": 2.5,
            },
            "business_info": {
                "product_familiarity": 9,
                "brand_recognition": 10,
                "is_consumer_business": True,
                "market_cap": 2_000_000_000_000,
                "has_moat": True,
            },
            "insider_info": {
                "insider_buying": True,
                "share_buyback": True,
            }
        }

        result = agent.analyze(stock_data)

        # 验证关键因素包含重要信息
        key_factors = result["key_factors"]
        assert len(key_factors) > 0
        assert isinstance(key_factors, list)

        # 应该包含PEG相关信息
        has_peg_info = any("PEG" in str(factor) for factor in key_factors)
        assert has_peg_info

    def test_category_classification(self):
        """测试股票分类逻辑"""
        agent = LynchAgent()

        # 快速增长股
        fast_grower = {
            "metrics": {"revenue_growth": 25, "profit_growth": 30, "dividend_yield": 0.5},
            "business_info": {}
        }
        category = agent._classify_stock(fast_grower["metrics"], fast_grower["business_info"])
        assert "快速" in category or "fast" in category.lower()

        # 稳健增长股
        stalwart = {
            "metrics": {"revenue_growth": 15, "profit_growth": 15, "dividend_yield": 1.5},
            "business_info": {}
        }
        category = agent._classify_stock(stalwart["metrics"], stalwart["business_info"])
        assert "稳健" in category or "stalwart" in category.lower()

        # 慢速增长股
        slow_grower = {
            "metrics": {"revenue_growth": 5, "profit_growth": 3, "dividend_yield": 5.0},
            "business_info": {}
        }
        category = agent._classify_stock(slow_grower["metrics"], slow_grower["business_info"])
        assert "慢速" in category or "slow" in category.lower()

        # 困境反转股
        turnaround = {
            "metrics": {"revenue_growth": -5, "profit_growth": -10, "dividend_yield": 0},
            "business_info": {"is_turnaround": True}
        }
        category = agent._classify_stock(turnaround["metrics"], turnaround["business_info"])
        assert "反转" in category or "turnaround" in category.lower()

    def test_scores_completeness(self):
        """测试评分系统完整性"""
        agent = LynchAgent()

        stock_data = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 25.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "debt_ratio": 20.0,
                "revenue_growth": 20.0,
                "profit_growth": 25.0,
                "dividend_yield": 2.5,
            },
            "business_info": {
                "product_familiarity": 9,
                "brand_recognition": 10,
                "is_consumer_business": True,
            },
            "insider_info": {}
        }

        result = agent.analyze(stock_data)

        # 验证所有评分维度都存在
        scores = result["scores"]
        expected_keys = ["peg", "growth", "category", "tenbagger", "familiarity", "lynch_criteria"]
        for key in expected_keys:
            assert key in scores
            assert isinstance(scores[key], (int, float))
            assert 0 <= scores[key] <= 100

    def test_confidence_calculation(self):
        """测试置信度计算"""
        agent = LynchAgent()

        # 高质量股票应该有高置信度
        good_stock = {
            "symbol": "600519",
            "name": "优质股",
            "price": 1500.0,
            "metrics": {
                "pe_ratio": 20.0,
                "pb_ratio": 10.0,
                "roe": 25.0,
                "revenue_growth": 25.0,
                "profit_growth": 25.0,
            },
            "business_info": {
                "product_familiarity": 10,
                "brand_recognition": 10,
                "is_consumer_business": True,
                "has_moat": True,
                "is_growth_industry": True,
                "market_cap": 10_000_000_000,
            },
            "insider_info": {
                "insider_buying": True,
                "share_buyback": True,
            }
        }

        result = agent.analyze(good_stock)
        assert result["confidence"] > 0.6
