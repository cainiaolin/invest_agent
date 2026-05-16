"""信息融合器测试"""
import pytest
from datetime import datetime
from app.models.search import SearchSummary, SearchResult
from app.services.search.enricher import SearchDataEnricher
from app.agents.search.fusion import InformationFusion


class TestInformationFusion:
    """信息融合器测试类"""

    @pytest.fixture
    def sample_stock_data(self):
        """示例股票数据"""
        return {
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "industry": "白酒",
            "roe": 0.25,
            "pe_ratio": 30.5,
            "market_cap": "2.1万亿",
            "current_price": 1680.0,
            "change_percent": 2.3
        }

    @pytest.fixture
    def sample_search_summary_good(self):
        """高质量的搜索结果摘要"""
        # 创建高质量结果
        high_quality_results = []
        for i in range(7):
            result = SearchResult(
                title=f"高质量研究报告{i+1}",
                url=f"http://example.com/report{i+1}",
                content=f"这是第{i+1}份高质量的茅台财务分析报告，包含详细的ROE、营收、利润等数据。当前ROE为25%，营收增长率稳定。",
                source="report",
                reliability=0.8 + i * 0.02,  # 0.8-0.92
                relevance=0.9,
                timestamp="2024-01-15",
                author=f"分析师{i+1}",
                high_quality_score=0.8,
                medium_quality_score=0.1,
                low_quality_score=0.1
            )
            high_quality_results.append(result)

        # 创建中等质量结果
        medium_quality_results = []
        for i in range(3):
            result = SearchResult(
                title=f"中等质量新闻{i+1}",
                url=f"http://example.com/news{i+1}",
                content=f"这是第{i+1}篇关于茅台的新闻报道，提到了最近的股价变化。",
                source="news",
                reliability=0.5,
                relevance=0.7,
                timestamp="2024-01-14",
                high_quality_score=0.2,
                medium_quality_score=0.6,
                low_quality_score=0.2
            )
            medium_quality_results.append(result)

        search_summary = SearchSummary(
            stock_code="600519",
            total_results=10,
            high_quality_count=7,
            medium_quality_count=3,
            low_quality_count=0,
            high_ratio=0.7,
            results_by_source={"report": high_quality_results, "news": medium_quality_results},
            search_timestamp="2024-01-15 10:00:00",
            search_keywords=["茅台", "白酒", "投资分析"]
        )

        return search_summary

    @pytest.fixture
    def sample_search_summary_medium(self):
        """中等质量的搜索结果摘要"""
        # 创建中等质量结果
        medium_quality_results = []
        for i in range(5):
            result = SearchResult(
                title=f"中等质量报告{i+1}",
                url=f"http://example.com/report{i+1}",
                content=f"这是第{i+1}份中等质量的报告，包含一些基本信息。",
                source="report",
                reliability=0.5,
                relevance=0.6,
                timestamp="2024-01-14",
                high_quality_score=0.3,
                medium_quality_score=0.5,
                low_quality_score=0.2
            )
            medium_quality_results.append(result)

        # 创建低质量结果
        low_quality_results = []
        for i in range(5):
            result = SearchResult(
                title=f"低质量内容{i+1}",
                url=f"http://example.com/low{i+1}",
                content=f"这是第{i+1}篇低质量的内容，信息较少。",
                source="forum",
                reliability=0.3,
                relevance=0.4,
                timestamp="2024-01-13",
                high_quality_score=0.1,
                medium_quality_score=0.2,
                low_quality_score=0.7
            )
            low_quality_results.append(result)

        search_summary = SearchSummary(
            stock_code="600519",
            total_results=10,
            high_quality_count=0,
            medium_quality_count=5,
            low_quality_count=5,
            high_ratio=0.0,
            results_by_source={"report": medium_quality_results, "forum": low_quality_results},
            search_timestamp="2024-01-15 10:00:00",
            search_keywords=["茅台", "分析"]
        )

        return search_summary

    @pytest.fixture
    def sample_search_summary_none(self):
        """无搜索结果的摘要"""
        search_summary = SearchSummary(
            stock_code="600519",
            total_results=0,
            high_quality_count=0,
            medium_quality_count=0,
            low_quality_count=0,
            high_ratio=0.0,
            results_by_source={},
            search_timestamp="2024-01-15 10:00:00",
            search_keywords=["茅台", "分析"],
            error="搜索失败"
        )

        return search_summary

    def test_information_fusion_init(self):
        """测试信息融合器初始化"""
        fusion = InformationFusion()
        assert fusion.enricher is not None
        assert isinstance(fusion.enricher, SearchDataEnricher)

    def test_information_fusion_merge_good_quality(self, sample_search_summary_good, sample_stock_data):
        """测试高质量信息的融合"""
        fusion = InformationFusion()
        result = fusion.merge(sample_search_summary_good, sample_stock_data)

        # 验证返回结构
        assert "search_summary" in result
        assert "stock_data" in result
        assert "has_search_data" in result
        assert "search_quality" in result

        # 验证内容
        assert result["search_summary"] == sample_search_summary_good
        assert result["stock_data"] == sample_stock_data
        assert result["has_search_data"] is True
        assert result["search_quality"] == "high"

    def test_information_fusion_merge_medium_quality(self, sample_search_summary_medium, sample_stock_data):
        """测试中等质量信息的融合"""
        fusion = InformationFusion()
        result = fusion.merge(sample_search_summary_medium, sample_stock_data)

        # 验证内容
        assert result["search_summary"] == sample_search_summary_medium
        assert result["stock_data"] == sample_stock_data
        assert result["has_search_data"] is True
        # 对于medium质量测试，根据实际逻辑应该是"low"，因为high_ratio=0.0
        assert result["search_quality"] == "low"

    def test_information_fusion_merge_none_quality(self, sample_search_summary_none, sample_stock_data):
        """测试无搜索结果的融合"""
        fusion = InformationFusion()
        result = fusion.merge(sample_search_summary_none, sample_stock_data)

        # 验证内容
        assert result["search_summary"] == sample_search_summary_none
        assert result["stock_data"] == sample_stock_data
        assert result["has_search_data"] is False
        assert result["search_quality"] == "none"

    def test_information_fusion_format_for_llm_good_quality(self, sample_search_summary_good, sample_stock_data):
        """测试高质量信息的LLM格式化"""
        fusion = InformationFusion()
        result = fusion.format_for_llm(sample_search_summary_good, sample_stock_data)

        # 验证格式化内容包含必要部分
        assert "=== 股票基本信息 ===" in result
        assert "=== 搜索结果摘要 ===" in result
        assert "=== 高质量信息源 ===" in result
        assert "=== 使用建议 ===" in result

        # 验证股票基本信息格式化正确
        assert "贵州茅台" in result
        assert "600519" in result
        assert "白酒" in result
        assert "ROE：25.0%" in result

    def test_information_fusion_format_for_llm_medium_quality(self, sample_search_summary_medium, sample_stock_data):
        """测试中等质量信息的LLM格式化"""
        fusion = InformationFusion()
        result = fusion.format_for_llm(sample_search_summary_medium, sample_stock_data)

        # 验证格式化内容包含必要部分
        assert "=== 股票基本信息 ===" in result
        assert "=== 搜索结果摘要 ===" in result
        assert "=== 使用建议 ===" in result

        # 验证不包含高质量信息源（因为没有高质量结果）
        assert "=== 高质量信息源 ===" not in result

    def test_information_fusion_format_for_llm_none_quality(self, sample_search_summary_none, sample_stock_data):
        """测试无搜索结果的LLM格式化"""
        fusion = InformationFusion()
        result = fusion.format_for_llm(sample_search_summary_none, sample_stock_data)

        # 验证格式化内容包含股票基本信息
        assert "=== 股票基本信息 ===" in result
        assert "贵州茅台" in result

        # 验证搜索结果部分显示无搜索数据
        assert "搜索结果质量：none" in result
        assert "当前搜索结果质量较低" in result


    def test_format_stock_basic_info(self, sample_stock_data):
        """测试股票基本信息格式化"""
        fusion = InformationFusion()
        result = fusion._format_stock_basic_info(sample_stock_data)

        # 验证包含必要信息
        assert "股票名称：贵州茅台" in result
        assert "股票代码：600519" in result
        assert "所属行业：白酒" in result
        assert "ROE：25.0%" in result
        assert "市盈率：30.5" in result
        assert "市值：2.1万亿" in result

    def test_format_fusion_note_good(self, sample_search_summary_good, sample_stock_data):
        """测试高质量数据融合说明"""
        fusion = InformationFusion()
        result = fusion._format_fusion_note(sample_search_summary_good, sample_stock_data)

        # 验证包含必要信息
        assert "=== 数据融合说明 ===" in result
        assert "总搜索结果：10条" in result
        assert "高质量：7条 (70.0%)" in result
        assert "中等质量：3条" in result
        assert "- 当前搜索结果质量高，可直接用于分析" in result

    def test_format_fusion_note_medium(self, sample_search_summary_medium, sample_stock_data):
        """测试中等质量数据融合说明"""
        fusion = InformationFusion()
        result = fusion._format_fusion_note(sample_search_summary_medium, sample_stock_data)

        # 验证包含必要信息
        assert "=== 数据融合说明 ===" in result
        assert "总搜索结果：10条" in result
        assert "高质量：0条 (0.0%)" in result
        assert "中等质量：5条" in result
        assert "- 当前搜索结果质量较低，建议结合其他数据源进行分析" in result

    def test_format_fusion_note_none(self, sample_search_summary_none, sample_stock_data):
        """测试无搜索结果融合说明"""
        fusion = InformationFusion()
        result = fusion._format_fusion_note(sample_search_summary_none, sample_stock_data)

        # 验证包含必要信息
        assert "=== 数据融合说明 ===" in result
        assert "总搜索结果：0条" in result
        assert "- 当前搜索结果质量较低，建议结合其他数据源进行分析" in result