"""搜索相关数据模型"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """单个搜索结果"""

    title: str = Field(description="搜索结果标题")
    url: str = Field(description="搜索结果URL")
    content: str = Field(description="搜索结果内容")
    source: str = Field(description="数据源，如 'news', 'report', 'web'")
    reliability: float = Field(description="可信度评分 0.0-1.0")
    relevance: float = Field(description="相关度评分 0.0-1.0")
    timestamp: str = Field(description="发布时间")
    author: Optional[str] = Field(default=None, description="作者")

    # 用于评分的元数据
    high_quality_score: float = Field(default=0.0, description="高质量内容得分")
    medium_quality_score: float = Field(default=0.0, description="中等质量内容得分")
    low_quality_score: float = Field(default=0.0, description="低质量内容得分")

    @property
    def is_high_quality(self) -> bool:
        """判断是否为高质量结果"""
        return self.reliability >= 0.7 or self.high_quality_score >= 0.7

    @property
    def quality_category(self) -> str:
        """获取质量类别"""
        if self.is_high_quality:
            return "high"
        elif self.reliability >= 0.4 or self.medium_quality_score >= 0.4:
            return "medium"
        else:
            return "low"


class SearchSummary(BaseModel):
    """搜索结果摘要"""

    stock_code: str = Field(description="股票代码")
    total_results: int = Field(description="总搜索结果数")
    high_quality_count: int = Field(description="高质量结果数")
    medium_quality_count: int = Field(description="中等质量结果数")
    low_quality_count: int = Field(description="低质量结果数")
    high_ratio: float = Field(description="高质量结果占比")

    # 按来源分类的结果
    results_by_source: Dict[str, List[SearchResult]] = Field(default_factory=dict)

    # 搜索时间戳
    search_timestamp: str = Field(description="搜索完成时间")

    # 搜索关键词
    search_keywords: List[str] = Field(default_factory=list)

    # 错误信息（可选）
    error: Optional[str] = Field(default=None, description="搜索错误信息")

    @property
    def has_valid_results(self) -> bool:
        """判断是否有有效搜索结果"""
        return self.total_results > 0 and not self.error

    @property
    def quality_assessment(self) -> str:
        """质量评估：high | medium | low | none"""
        if self.total_results == 0 or self.error:
            return "none"

        if self.high_ratio >= 0.7:
            return "high"
        elif self.high_ratio >= 0.4:
            return "medium"
        else:
            return "low"

    def get_results_by_quality(self, quality: str) -> List[SearchResult]:
        """按质量获取结果"""
        if quality == "high":
            return [r for r in self.get_all_results() if r.is_high_quality]
        elif quality == "medium":
            return [r for r in self.get_all_results() if r.quality_category == "medium"]
        elif quality == "low":
            return [r for r in self.get_all_results() if r.quality_category == "low"]
        else:
            return self.get_all_results()

    def get_all_results(self) -> List[SearchResult]:
        """获取所有搜索结果"""
        all_results = []
        for source_results in self.results_by_source.values():
            all_results.extend(source_results)
        return all_results

    def get_top_n_results(self, n: int = 5) -> List[SearchResult]:
        """获取排名前N的结果（按质量和相关度排序）"""
        all_results = self.get_all_results()
        # 按质量和相关度排序：先按质量（high>medium>low），再按相关度
        sorted_results = sorted(
            all_results,
            key=lambda r: (r.is_high_quality, r.relevance),
            reverse=True
        )
        return sorted_results[:n]