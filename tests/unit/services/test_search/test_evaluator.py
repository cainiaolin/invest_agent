"""可信度评估器测试"""

import pytest
from datetime import datetime, timedelta
from app.services.search.evaluator import ReliabilityEvaluator
from app.models.search import SearchResult, ReliabilityScore, SourceType, ContentType


@pytest.fixture
def evaluator():
    """创建评估器实例"""
    return ReliabilityEvaluator(use_llm_evaluation=False)


@pytest.fixture
def sample_results():
    """创建示例搜索结果"""
    now = datetime.now()
    return [
        # 高可信度：官方公告，新鲜
        SearchResult(
            title="重大资产重组公告",
            content="公司拟收购XXX公司100%股权",
            url="http://www.cninfo.com.cn/xxx",
            source="巨潮资讯网",
            source_type=SourceType.OFFICIAL,
            content_type=ContentType.ANNOUNCEMENT,
            publish_date=now - timedelta(days=1),
            stock_code="600519",
            relevance_score=0.95
        ),
        # 中可信度：主流媒体，较新鲜
        SearchResult(
            title="茅台股价创新高",
            content="贵州茅台股价今日上涨5%",
            url="http://finance.sina.com.cn/xxx",
            source="新浪财经",
            source_type=SourceType.MAINSTREAM,
            content_type=ContentType.NEWS,
            publish_date=now - timedelta(days=2),
            stock_code="600519",
            relevance_score=0.8
        ),
        # 低可信度：自媒体，较旧
        SearchResult(
            title="茅台要跌了",
            content="我觉得茅台要跌，大家快跑",
            url="http://jueduiuidui.com/xxx",
            source="今日头条",
            source_type=SourceType.OTHER,
            content_type=ContentType.COMMENT,
            publish_date=now - timedelta(days=30),
            stock_code="600519",
            relevance_score=0.6
        )
    ]


class TestReliabilityEvaluator:
    """可信度评估器测试"""

    def test_evaluate_high_reliability(self, evaluator, sample_results):
        """测试高可信度评估"""
        result = sample_results[0]
        score = evaluator._rule_based_evaluation(result)

        assert score.score >= 0.8
        assert score.source_authority == 1.0  # 巨潮资讯网
        assert score.timeliness >= 0.9  # 1天内
        assert score.is_official is True

    def test_evaluate_medium_reliability(self, evaluator, sample_results):
        """测试中可信度评估"""
        result = sample_results[1]
        score = evaluator._rule_based_evaluation(result)

        assert 0.6 <= score.score < 0.8
        assert score.source_authority == 0.8  # 新浪财经
        assert score.timeliness >= 0.8  # 2天内
        assert score.is_official is False

    def test_evaluate_low_reliability(self, evaluator, sample_results):
        """测试低可信度评估"""
        result = sample_results[2]
        score = evaluator._rule_based_evaluation(result)

        assert score.score < 0.6
        assert score.source_authority == 0.4  # 今日头条
        assert score.timeliness < 0.6  # 30天前
        assert score.is_official is False

    def test_source_authority_evaluation(self, evaluator):
        """测试来源权威性评估"""
        # 官方渠道
        assert evaluator._evaluate_source_authority("巨潮资讯网") == 1.0
        assert evaluator._evaluate_source_authority("上海证券交易所") == 1.0

        # 主流媒体
        assert evaluator._evaluate_source_authority("新浪财经") == 0.8
        assert evaluator._evaluate_source_authority("证券时报") == 0.85

        # 其他
        assert evaluator._evaluate_source_authority("雪球") == 0.5

        # 未识别
        assert evaluator._evaluate_source_authority("未知来源") == 0.5

    def test_timeliness_evaluation(self, evaluator):
        """测试时效性评估"""
        now = datetime.now()

        # 1天内
        assert evaluator._evaluate_timeliness(now - timedelta(hours=12)) == 1.0

        # 1周内
        assert evaluator._evaluate_timeliness(now - timedelta(days=3)) == 0.9

        # 1月内
        assert evaluator._evaluate_timeliness(now - timedelta(days=15)) == 0.7

        # 3月内
        assert evaluator._evaluate_timeliness(now - timedelta(days=60)) == 0.5

        # 更早
        assert evaluator._evaluate_timeliness(now - timedelta(days=120)) == 0.3

        # 无时间信息
        assert evaluator._evaluate_timeliness(None) == 0.3

    def test_content_type_evaluation(self, evaluator):
        """测试内容类型评估"""
        assert evaluator._evaluate_content_type(ContentType.ANNOUNCEMENT) == 1.0
        assert evaluator._evaluate_content_type(ContentType.REPORT) == 0.9
        assert evaluator._evaluate_content_type(ContentType.NEWS) == 0.7
        assert evaluator._evaluate_content_type(ContentType.OTHER) == 0.5
        assert evaluator._evaluate_content_type(ContentType.COMMENT) == 0.4

    def test_to_prompt_format(self):
        """测试Prompt格式化"""
        high_score = ReliabilityScore(score=0.9, source_authority=1.0, timeliness=1.0, is_official=True)
        assert "高" in high_score.to_prompt_format()
        assert "官方公告" in high_score.to_prompt_format()

        medium_score = ReliabilityScore(score=0.7, source_authority=0.8, timeliness=0.8, is_official=False)
        assert "中" in medium_score.to_prompt_format()

        low_score = ReliabilityScore(score=0.3, source_authority=0.5, timeliness=0.5, is_official=False)
        assert "低" in low_score.to_prompt_format()
