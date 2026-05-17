"""可信度评估器"""

import logging
from typing import List
from datetime import datetime, timedelta
from app.models.search import SearchResult, ReliabilityScore, SourceType, ContentType


logger = logging.getLogger(__name__)


class ReliabilityEvaluator:
    """
    信息可信度评估器

    两阶段评估：
    1. 规则过滤（来源白名单+时间窗口+基础打分）
    2. LLM深度分析（可选）
    """

    # 来源权威性白名单及得分
    SOURCE_AUTHORITY_SCORES = {
        # 官方渠道
        "巨潮资讯网": 1.0,
        "上海证券交易所": 1.0,
        "深圳证券交易所": 1.0,
        "北京证券交易所": 1.0,
        # 主流财经媒体
        "新浪财经": 0.8,
        "东方财富": 0.8,
        "同花顺": 0.8,
        "证券时报": 0.85,
        "上海证券报": 0.85,
        "中国证券报": 0.85,
        "证券日报": 0.8,
        "第一财经": 0.8,
        "财联社": 0.75,
        "华尔街见闻": 0.7,
        # 其他
        "雪球": 0.5,
        "今日头条": 0.4,
    }

    def __init__(self, use_llm_evaluation: bool = True, llm_service=None):
        """
        初始化评估器

        Args:
            use_llm_evaluation: 是否使用LLM深度评估
            llm_service: LLM服务实例
        """
        self.use_llm_evaluation = use_llm_evaluation
        self.llm_service = llm_service

    async def evaluate(self, result: SearchResult) -> ReliabilityScore:
        """
        评估单个搜索结果的可信度

        Args:
            result: 搜索结果

        Returns:
            可信度评分
        """
        # 第一阶段：规则评估
        score = self._rule_based_evaluation(result)

        # 第二阶段：LLM深度评估（可选）
        if self.use_llm_evaluation and self.llm_service:
            llm_score = await self._llm_evaluation(result)
            # 加权平均：规则70% + LLM30%
            final_score = (score.score * 0.7 + llm_score * 0.3)
            score.score = min(final_score, 1.0)
            score.reasons.append(f"LLM深度评估得分: {llm_score:.2f}")

        return score

    async def evaluate_batch(
        self,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """
        批量评估搜索结果

        Args:
            results: 搜索结果列表

        Returns:
            带可信度评分的搜索结果列表
        """
        for result in results:
            result.reliability_score = await self.evaluate(result)
        return results

    def _rule_based_evaluation(self, result: SearchResult) -> ReliabilityScore:
        """
        基于规则的可信度评估

        Args:
            result: 搜索结果

        Returns:
            可信度评分
        """
        reasons = []

        # 1. 来源权威性评估（权重0.4）
        source_authority = self._evaluate_source_authority(result.source)
        reasons.append(f"来源权威性: {source_authority:.2f}")

        # 2. 时效性评估（权重0.3）
        timeliness = self._evaluate_timeliness(result.publish_date)
        reasons.append(f"时效性: {timeliness:.2f}")

        # 3. 内容类型评估（权重0.2）
        content_type_score = self._evaluate_content_type(result.content_type)
        reasons.append(f"内容类型: {content_type_score:.2f}")

        # 4. 是否官方公告（权重0.1）
        is_official = result.content_type == ContentType.ANNOUNCEMENT
        official_score = 1.0 if is_official else 0.5
        reasons.append(f"官方公告: {'是' if is_official else '否'}")

        # 综合评分
        final_score = (
            source_authority * 0.4 +
            timeliness * 0.3 +
            content_type_score * 0.2 +
            official_score * 0.1
        )

        return ReliabilityScore(
            score=final_score,
            source_authority=source_authority,
            timeliness=timeliness,
            is_official=is_official,
            reasons=reasons
        )

    def _evaluate_source_authority(self, source: str) -> float:
        """
        评估来源权威性

        Args:
            source: 来源名称

        Returns:
            权威性得分 0-1
        """
        # 查找白名单
        for whitelist_source, score in self.SOURCE_AUTHORITY_SCORES.items():
            if whitelist_source in source:
                return score

        # 未在白名单中，根据来源类型判断
        if "官方" in source or "gov" in source.lower():
            return 0.9
        elif "交易所" in source:
            return 0.95
        elif "财经" in source or "证券" in source:
            return 0.7
        else:
            return 0.5

    def _evaluate_timeliness(
        self,
        publish_date: datetime | None
    ) -> float:
        """
        评估时效性

        Args:
            publish_date: 发布时间

        Returns:
            时效性得分 0-1
        """
        if not publish_date:
            return 0.3  # 没有时间信息，得分较低

        now = datetime.now()
        days_ago = (now - publish_date).days

        if days_ago <= 1:
            return 1.0  # 1天内
        elif days_ago <= 7:
            return 0.9  # 1周内
        elif days_ago <= 30:
            return 0.7  # 1月内
        elif days_ago <= 90:
            return 0.5  # 3月内
        else:
            return 0.3  # 更早

    def _evaluate_content_type(self, content_type: ContentType) -> float:
        """
        评估内容类型

        Args:
            content_type: 内容类型

        Returns:
            内容类型得分 0-1
        """
        scores = {
            ContentType.ANNOUNCEMENT: 1.0,    # 公告最可信
            ContentType.REPORT: 0.9,          # 研报
            ContentType.NEWS: 0.7,            # 新闻
            ContentType.OTHER: 0.5,           # 其他
            ContentType.COMMENT: 0.4,         # 评论主观性强
        }
        return scores.get(content_type, 0.5)

    async def _llm_evaluation(self, result: SearchResult) -> float:
        """
        使用LLM进行深度可信度评估

        Args:
            result: 搜索结果

        Returns:
            LLM评估的可信度得分 0-1
        """
        if not self.llm_service:
            return 0.5

        try:
            prompt = f"""请评估以下信息的可信度（0-1之间的分数）：

标题：{result.title}
内容：{result.content[:200]}
来源：{result.source}
发布时间：{result.publish_date}

评估要点：
1. 内容是否专业、客观
2. 是否包含具体数据和事实
3. 语言风格是否正式
4. 是否有明显的夸大或偏见

请只返回一个0-1之间的数字（保留2位小数），不要其他内容。
示例：0.85
"""

            messages = [
                {"role": "system", "content": "你是一位专业的信息可信度评估专家。"},
                {"role": "user", "content": prompt}
            ]

            response = await self.llm_service._call_llm(messages)

            # 解析响应
            try:
                import re
                score_match = re.search(r'0\.\d+|1\.0|0\.\d', response)
                if score_match:
                    score = float(score_match.group())
                    return max(0.0, min(score, 1.0))
            except ValueError:
                pass

            return 0.5

        except Exception as e:
            logger.warning(f"LLM评估失败: {e}")
            return 0.5
