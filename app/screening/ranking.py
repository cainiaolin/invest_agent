"""
股票排名 - 对筛选结果进行排名和打分
"""
from typing import List, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class Ranker:
    """排名器基类"""

    def __init__(self, name: str = "基础排名器"):
        self.name = name

    def rank(self, stocks: List[Dict]) -> List[Dict]:
        """
        对股票进行排名

        Args:
            stocks: 股票列表

        Returns:
            排序后的股票列表
        """
        raise NotImplementedError("子类必须实现rank方法")

    def get_top_n(self, stocks: List[Dict], n: int) -> List[Dict]:
        """
        获取前N只股票

        Args:
            stocks: 股票列表
            n: 返回数量

        Returns:
            前N只股票
        """
        ranked = self.rank(stocks)
        return ranked[:n]


class ScoreRanker(Ranker):
    """综合评分排名器 - 基于多个因子综合评分"""

    def __init__(
        self,
        score_func: Optional[Callable] = None,
        ascending: bool = False  # False表示降序（高分在前）
    ):
        super().__init__("综合评分排名器")
        self.score_func = score_func or self._default_score_func
        self.ascending = ascending

    def _default_score_func(self, stock: Dict) -> float:
        """默认评分函数"""
        score = 0.0

        # ROE权重
        roe = stock.get('roe', 0)
        score += roe * 0.3

        # 营收增长率权重
        revenue_growth = stock.get('revenue_growth', 0)
        score += revenue_growth * 0.2

        # 利润增长率权重
        profit_growth = stock.get('profit_growth', 0)
        score += profit_growth * 0.2

        # 市盈率倒数（越低越好）
        pe = stock.get('pe', 100)
        if pe > 0:
            score += (1 / pe) * 10

        # 市净率倒数
        pb = stock.get('pb', 100)
        if pb > 0:
            score += (1 / pb) * 5

        return score

    def rank(self, stocks: List[Dict]) -> List[Dict]:
        """按综合评分排序"""
        # 计算每只股票的得分
        scored_stocks = []
        for stock in stocks:
            try:
                score = self.score_func(stock)
                stock_with_score = {**stock, '_score': score}
                scored_stocks.append(stock_with_score)
            except Exception as e:
                logger.warning(f"计算股票 {stock.get('name', '')} 得分失败: {e}")
                stock_with_score = {**stock, '_score': 0.0}
                scored_stocks.append(stock_with_score)

        # 按得分排序
        reverse = not self.ascending
        scored_stocks.sort(key=lambda x: x['_score'], reverse=reverse)

        logger.info(
            f"综合评分排名: 完成排名，最高分={scored_stocks[0]['_score']:.2f}"
        )

        return scored_stocks


class FactorRanker(Ranker):
    """单因子排名器 - 基于单个因子排名"""

    def __init__(
        self,
        factor: str,
        ascending: bool = False  # False表示降序（大值在前）
    ):
        super().__init__("单因子排名器")
        self.factor = factor
        self.ascending = ascending

    def rank(self, stocks: List[Dict]) -> List[Dict]:
        """按单因子排序"""
        # 过滤掉没有该因子的股票
        valid_stocks = [
            stock for stock in stocks
            if self.factor in stock and stock[self.factor] is not None
        ]

        # 按因子排序
        reverse = not self.ascending
        sorted_stocks = sorted(
            valid_stocks,
            key=lambda x: x[self.factor],
            reverse=reverse
        )

        logger.info(
            f"单因子排名[{self.factor}]: 完成，"
            f"最高值={sorted_stocks[0].get(self.factor, 'N/A')}"
        )

        return sorted_stocks


class MultiFactorRanker(Ranker):
    """多因子排名器 - 基于多个因子加权排名"""

    def __init__(
        self,
        factors: Dict[str, float],  # {因子名: 权重}
        ascending: Dict[str, bool] = None  # {因子名: 是否升序}
    ):
        super().__init__("多因子排名器")
        self.factors = factors
        self.ascending = ascending or {}

    def rank(self, stocks: List[Dict]) -> List[Dict]:
        """按多因子加权排序"""
        # 计算加权得分
        scored_stocks = []
        for stock in stocks:
            total_score = 0.0
            total_weight = 0.0

            for factor, weight in self.factors.items():
                value = stock.get(factor)

                if value is None:
                    continue

                # 标准化处理（简化版：除以最大值）
                # 实际应用中应该更复杂
                normalized_value = float(value)

                # 考虑排序方向
                is_ascending = self.ascending.get(factor, False)
                if not is_ascending:
                    normalized_value = -normalized_value  # 降序时取负

                total_score += normalized_value * weight
                total_weight += weight

            if total_weight > 0:
                avg_score = total_score / total_weight
                stock_with_score = {**stock, '_multi_factor_score': avg_score}
                scored_stocks.append(stock_with_score)

        # 按加权得分排序（降序）
        scored_stocks.sort(key=lambda x: x['_multi_factor_score'], reverse=True)

        logger.info(
            f"多因子排名: 完成排名，最高分={scored_stocks[0]['_multi_factor_score']:.2f}"
        )

        return scored_stocks


class AgentBasedRanker(Ranker):
    """基于Agent的排名器 - 使用投资Agent进行分析"""

    def __init__(
        self,
        agents: List,  # Agent列表
        weight_func: Optional[Callable] = None  # Agent权重函数
    ):
        super().__init__("Agent排名器")
        self.agents = agents
        self.weight_func = weight_func or self._default_weight_func

    def _default_weight_func(self, agent) -> float:
        """默认权重函数"""
        # 可以根据Agent类型、历史表现等确定权重
        return 1.0

    def rank(self, stocks: List[Dict]) -> List[Dict]:
        """使用Agent分析并排名"""
        scored_stocks = []

        for stock in stocks:
            agent_scores = []
            agent_weights = []

            # 让每个Agent分析该股票
            for agent in self.agents:
                try:
                    # 调用Agent的分析方法
                    result = agent.analyze(stock['ts_code'])

                    # 提取评分（简化版）
                    score = result.get('score', 50)  # 默认50分
                    weight = self.weight_func(agent)

                    agent_scores.append(score)
                    agent_weights.append(weight)

                except Exception as e:
                    logger.warning(
                        f"Agent {agent.name} 分析 {stock.get('name', '')} 失败: {e}"
                    )

            # 计算加权平均得分
            if agent_scores:
                total_weight = sum(agent_weights)
                weighted_score = sum(
                    score * weight for score, weight in zip(agent_scores, agent_weights)
                ) / total_weight if total_weight > 0 else 50

                stock_with_score = {
                    **stock,
                    '_agent_score': weighted_score,
                    '_agent_scores': agent_scores
                }
                scored_stocks.append(stock_with_score)

        # 按Agent得分排序
        scored_stocks.sort(key=lambda x: x['_agent_score'], reverse=True)

        logger.info(
            f"Agent排名: 完成排名，最高分={scored_stocks[0]['_agent_score']:.2f}"
        )

        return scored_stocks
