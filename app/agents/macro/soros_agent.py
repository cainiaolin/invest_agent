"""索罗斯风格宏观对冲Agent"""
from app.agents.base import BaseAgent
from app.core.state import AnalysisState


class SorosAgent(BaseAgent):
    """
    索罗斯风格的宏观对冲Agent

    投资理念:
    1. 反身性理论：市场偏见影响价格，价格变化反过来影响基本面
    2. 繁荣-崩溃周期：识别市场泡沫和拐点
    3. 逆向投资：在市场极端情况下采取相反立场
    4. 动态调整：根据市场变化灵活调整仓位
    """

    @property
    def name(self) -> str:
        """Agent名称"""
        return "George Soros"

    @property
    def style(self) -> str:
        """投资风格描述"""
        return "宏观对冲：关注反身性、市场泡沫和拐点识别"

    async def analyze(self, state: AnalysisState) -> dict:
        """
        基于索罗斯理念分析股票

        评估维度:
        1. 反身性强度（价格与基本面偏离程度）
        2. 周期位置（处于繁荣-崩溃周期的哪个阶段）
        3. 市场偏见程度（投资者情绪过度乐观或悲观）
        4. 趋势可持续性（当前趋势是否接近拐点）

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

        # 添加agent_name并统一返回格式
        result["agent_name"] = self.name
        if "decision" in result and "action" not in result:
            result["action"] = result.pop("decision")
        if "key_factors" in result and "key_metrics" not in result:
            result["key_metrics"] = {"key_factors": result.pop("key_factors")}

        return result

    async def _get_stock_data(self, stock_code: str) -> dict:
        """获取股票数据"""
        import random
        random.seed(hash(stock_code) % 10000)

        return {
            "symbol": stock_code,
            "name": f"股票{stock_code}",
            "metrics": {
                "pe_ratio": round(random.uniform(8, 60), 2),
                "pb_ratio": round(random.uniform(0.8, 12), 2),
                "price_momentum": round(random.uniform(-30, 50), 2),
                "volatility": round(random.uniform(10, 60), 2),
            },
            "macro_indicators": {
                "liquidity_cycle": random.choice(["expansion", "neutral", "contraction"]),
                "credit_spread": round(random.uniform(1, 8), 2),
                "yield_curve": random.choice(["normal", "flat", "inverted"]),
            },
            "market_sentiment": {
                "score": random.randint(20, 80),
                "put_call_ratio": round(random.uniform(0.5, 2.0), 2),
                "margin_debt_growth": round(random.uniform(-20, 40), 2),
            },
        }

    def _analyze_stock_data(self, stock_data: dict) -> dict:
        """分析股票数据（内部方法）"""
        metrics = stock_data.get("metrics", {})
        macro_indicators = stock_data.get("macro_indicators", {})
        market_sentiment = stock_data.get("market_sentiment", {})

        # 提取关键指标
        pe_ratio = metrics.get("pe_ratio", 0)
        pb_ratio = metrics.get("pb_ratio", 0)
        price_momentum = metrics.get("price_momentum", 0)  # 价格动量
        volatility = metrics.get("volatility", 0)  # 波动率

        # 宏观指标
        liquidity_cycle = macro_indicators.get("liquidity_cycle", "neutral")  # 流动性周期
        credit_spread = macro_indicators.get("credit_spread", 0)  # 信用利差
        yield_curve = macro_indicators.get("yield_curve", "normal")  # 收益率曲线

        # 市场情绪
        sentiment_score = market_sentiment.get("score", 50)  # 0-100, 50为中性
        put_call_ratio = market_sentiment.get("put_call_ratio", 1.0)  # 看跌/看涨比率
        margin_debt = market_sentiment.get("margin_debt_growth", 0)  # 融资余额增长

        # 评分系统 (0-100)
        scores = {
            "reflexivity": self._evaluate_reflexivity(
                pe_ratio, pb_ratio, price_momentum, sentiment_score
            ),
            "cycle_position": self._evaluate_cycle_position(
                liquidity_cycle, credit_spread, yield_curve, margin_debt
            ),
            "market_bias": self._evaluate_market_bias(
                sentiment_score, put_call_ratio, volatility
            ),
            "trend_sustainability": self._evaluate_trend_sustainability(
                price_momentum, volatility, credit_spread
            ),
        }

        # 计算总分
        total_score = sum(scores.values()) / len(scores)

        # 计算置信度
        confidence = min(abs(total_score - 50) / 50, 1.0)  # 偏离中性的程度

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

    def _evaluate_reflexivity(
        self, pe: float, pb: float, momentum: float, sentiment: float
    ) -> float:
        """评估反身性强度 (0-100)

        高反身性特征：价格与基本面严重偏离，自我强化循环
        """
        score = 50  # 基础分

        # PE偏离度（历史平均PE约15）
        pe_deviation = abs(pe - 15) / 15
        if pe_deviation > 1.5:  # PE严重偏离
            score += 30
        elif pe_deviation > 1.0:
            score += 15
        elif pe_deviation > 0.5:
            score += 5

        # 价格动量与情绪的正反馈
        if momentum > 20 and sentiment > 70:  # 强烈正反馈
            score += 25
        elif momentum > 10 and sentiment > 60:
            score += 15
        elif momentum < -10 and sentiment < 30:  # 强烈负反馈
            score += 25
        elif momentum < -20 and sentiment < 40:  # 极端负反馈（恐慌抛售）
            score += 35  # 更高的分数，因为恐慌时的反身性更强

        # PB极端值
        if pb > 5 or pb < 0.5:
            score += 10

        return max(0, min(100, score))

    def _evaluate_cycle_position(
        self, liquidity: str, credit_spread: float, yield_curve: str, margin_debt: float
    ) -> float:
        """评估周期位置 (0-100)

        识别处于繁荣-崩溃周期的哪个阶段
        """
        score = 50  # 基础分

        # 流动性周期
        if liquidity == "expansion":
            score += 20
        elif liquidity == "contraction":
            score -= 20

        # 信用利差（利差扩大通常预示风险增加）
        if credit_spread > 3:  # 高风险
            score -= 25
        elif credit_spread > 2:
            score -= 10
        elif credit_spread < 1:  # 低风险，可能过度乐观
            score += 15

        # 收益率曲线
        if yield_curve == "inverted":  # 倒挂预示衰退
            score -= 30
        elif yield_curve == "flat":
            score -= 15

        # 融资余额增长（过度杠杆）
        if margin_debt > 30:  # 过度杠杆
            score -= 20
        elif margin_debt < 0:  # 去杠杆
            score += 10

        return max(0, min(100, score))

    def _evaluate_market_bias(
        self, sentiment: float, put_call_ratio: float, volatility: float
    ) -> float:
        """评估市场偏见程度 (0-100)

        极端情绪往往预示拐点
        """
        score = 50  # 基础分

        # 情绪分数极端化
        if sentiment > 80:  # 极度贪婪
            score += 30
        elif sentiment > 70:
            score += 15
        elif sentiment < 20:  # 极度恐惧
            score -= 30
        elif sentiment < 30:
            score -= 15

        # 看跌/看涨比率
        if put_call_ratio < 0.5:  # 过度看涨
            score += 20
        elif put_call_ratio > 1.5:  # 过度看跌
            score -= 20

        # 波动率（低波动率可能导致过度自满）
        if volatility < 10:
            score += 10
        elif volatility > 40:  # 高波动可能预示转折
            score -= 10

        return max(0, min(100, score))

    def _evaluate_trend_sustainability(
        self, momentum: float, volatility: float, credit_spread: float
    ) -> float:
        """评估趋势可持续性 (0-100)

        识别趋势是否接近拐点
        """
        score = 50  # 基础分

        # 动量衰减
        if momentum > 30:  # 过热可能回调
            score += 25
        elif momentum > 20:
            score += 15
        elif momentum < -30:  # 过度下跌可能反弹
            score -= 25

        # 波动率突增
        if volatility > 30:
            score += 15  # 趋势可能反转

        # 信用风险上升
        if credit_spread > 2.5:
            score += 20  # 宏观风险增加

        return max(0, min(100, score))

    def _make_decision(self, total_score: float, scores: dict) -> str:
        """基于评分做出决策

        索罗斯风格：在极端情况下采取相反立场
        """
        # 极端高评分：市场泡沫，考虑做空
        if total_score >= 75:
            return "sell"
        # 极端低评分：市场恐慌，考虑买入
        elif total_score <= 25:
            return "buy"
        # 中等区域：观望或反向操作
        elif scores["market_bias"] > 70:
            return "sell"  # 市场过度乐观，做空
        elif scores["market_bias"] < 30:
            return "buy"  # 市场过度悲观，买入
        else:
            return "hold"

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
            reasoning_parts.append(f"建议{name}({symbol})卖出或做空。")

        # 反身性分析
        reflexivity_score = scores["reflexivity"]
        if reflexivity_score >= 70:
            reasoning_parts.append("市场出现强烈的反身性循环，价格严重偏离基本面。")
        elif reflexivity_score <= 30:
            reasoning_parts.append("反身性效应较弱，价格相对合理。")

        # 周期位置
        cycle_score = scores["cycle_position"]
        if cycle_score >= 70:
            reasoning_parts.append("处于泡沫后期，警惕趋势反转。")
        elif cycle_score <= 30:
            reasoning_parts.append("处于恐慌阶段，可能存在机会。")

        # 市场偏见
        bias_score = scores["market_bias"]
        if bias_score >= 70:
            reasoning_parts.append("市场情绪过度乐观，存在逆向投资机会。")
        elif bias_score <= 30:
            reasoning_parts.append("市场情绪过度悲观，可能被低估。")

        return " ".join(reasoning_parts)

    def _extract_key_factors(self, scores: dict, stock_data: dict) -> list:
        """提取关键投资因素"""
        factors = []

        # 根据评分提取关键因素
        if scores["reflexivity"] >= 70:
            factors.append("强反身性")
        elif scores["reflexivity"] <= 30:
            factors.append("弱反身性")

        if scores["cycle_position"] >= 70:
            factors.append("泡沫阶段")
        elif scores["cycle_position"] <= 30:
            factors.append("恐慌阶段")

        if scores["market_bias"] >= 70:
            factors.append("市场过度乐观")
        elif scores["market_bias"] <= 30:
            factors.append("市场过度悲观")

        if scores["trend_sustainability"] >= 70:
            factors.append("趋势接近拐点")

        # 添加具体的宏观指标
        macro_indicators = stock_data.get("macro_indicators", {})
        if macro_indicators.get("liquidity_cycle") == "contraction":
            factors.append("流动性紧缩")
        if macro_indicators.get("yield_curve") == "inverted":
            factors.append("收益率曲线倒挂")

        return factors

    def vote(self, analysis: dict) -> str:
        """
        根据分析结果投票

        索罗斯风格：
        - 极端情况下的高置信度 → 坚决执行
        - 中等置信度 → 谨慎或小仓位试探
        - 低置信度 → 观望

        Args:
            analysis: analyze()方法返回的分析结果

        Returns:
            投票结果
        """
        decision = analysis.get("decision", "hold")
        confidence = analysis.get("confidence", 0.5)

        # 高置信度时果断执行
        if confidence > 0.7:
            return decision

        # 中等置信度时倾向于保守
        if confidence > 0.4:
            if decision == "buy":
                return "hold"  # 谨慎买入
            elif decision == "sell":
                return "hold"  # 谨慎卖出
            else:
                return "hold"

        # 低置信度时保持观望
        return "hold"

    def debate(self, context: dict) -> str:
        """
        参与投资辩论

        索罗斯会强调：
        1. 市场总是错的
        2. 反身性循环的存在
        3. 在泡沫中寻找做空机会
        4. 在恐慌中寻找买入机会

        Args:
            context: 包含股票信息、市场情绪、其他观点的字典

        Returns:
            索罗斯风格的观点陈述
        """
        stock = context.get("stock", {})
        stock_name = stock.get("name", "该公司")
        market_sentiment = context.get("market_sentiment", "neutral")

        # 根据市场情绪调整论点
        if market_sentiment == "bullish":
            return (
                f"关于{stock_name}，我需要提醒大家注意反身性风险。"
                "当前市场存在强烈的正反馈循环：价格上涨改善了基本面，"
                "基本面的改善又进一步推动价格上涨。但这种循环是不可持续的。"
                "当趋势逆转时，下跌同样会自我强化。现在可能是建立空头头寸的时候。"
            )
        elif market_sentiment == "bearish":
            return (
                f"关于{stock_name}，市场恐慌正在创造机会。"
                "当所有人都在卖出时，资产价格往往低于其内在价值。"
                "但重要的是要区分：这只是暂时的流动性危机，还是基本面的真正恶化？"
                "如果是前者，这可能是建立多头头寸的良机。"
            )
        else:
            return (
                f"关于{stock_name}，我在寻找市场的错误定价。"
                "关键问题是：当前价格是否反映了所有已知信息？"
                "如果市场正在形成某种共识，我通常会问自己：这个共识可能是错的吗？"
                "投资的机会往往存在于市场偏见与现实之间的差距中。"
            )