"""搜索相关数据模型"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class SourceType(str, Enum):
    """数据源类型"""
    MAINSTREAM = "mainstream"  # 主流媒体
    OFFICIAL = "official"  # 官方公告
    SOCIAL = "social"  # 社交媒体
    OTHER = "other"  # 其他


class ContentType(str, Enum):
    """内容类型"""
    NEWS = "news"  # 新闻
    ANNOUNCEMENT = "announcement"  # 公告
    REPORT = "report"  # 研报
    OTHER = "other"  # 其他


class CrawlerConfig(BaseModel):
    """爬虫配置"""
    base_url: str = Field(description="基础URL")
    timeout: int = Field(default=10, description="请求超时时间（秒）")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User-Agent"
    )
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: float = Field(default=1.0, description="重试延迟（秒）")


class ReliabilityScore(BaseModel):
    """可信度评分"""
    score: float = Field(description="综合可信度得分 0.0-1.0")
    source_authority: float = Field(description="来源权威性得分 0.0-1.0")
    timeliness: float = Field(description="时效性得分 0.0-1.0")
    is_official: bool = Field(default=False, description="是否官方来源")
    reasons: List[str] = Field(default_factory=list, description="评分理由")


class SearchResult(BaseModel):
    """单个搜索结果"""

    title: str = Field(description="搜索结果标题")
    url: str = Field(description="搜索结果URL")
    content: str = Field(description="搜索结果内容")
    source: str = Field(description="数据源名称")
    source_type: SourceType = Field(default=SourceType.OTHER, description="数据源类型")
    content_type: ContentType = Field(default=ContentType.OTHER, description="内容类型")
    reliability: float = Field(description="可信度评分 0.0-1.0")
    relevance: float = Field(description="相关度评分 0.0-1.0")
    publish_date: datetime = Field(default_factory=datetime.now, description="发布时间")
    stock_code: str = Field(description="股票代码")

    # 兼容旧字段
    timestamp: Optional[str] = Field(default=None, description="发布时间（字符串格式）")
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
    stock_name: str = Field(default="", description="股票名称")
    total_results: int = Field(description="总搜索结果数")
    high_reliability_count: int = Field(default=0, description="高可信度结果数")
    medium_reliability_count: int = Field(default=0, description="中等可信度结果数")
    low_reliability_count: int = Field(default=0, description="低可信度结果数")
    latest_news_date: Optional[datetime] = Field(default=None, description="最新新闻日期")

    # 兼容旧字段
    high_quality_count: int = Field(default=0, description="高质量结果数")
    medium_quality_count: int = Field(default=0, description="中等质量结果数")
    low_quality_count: int = Field(default=0, description="低质量结果数")
    high_ratio: float = Field(default=0.0, description="高质量结果占比")

    # 按来源分类的结果
    results_by_source: Dict[str, List[SearchResult]] = Field(default_factory=dict)

    # 搜索时间戳
    search_timestamp: str = Field(default="", description="搜索完成时间")

    # 搜索关键词
    search_keywords: List[str] = Field(default_factory=list)

    # 错误信息（可选）
    error: Optional[str] = Field(default=None, description="搜索错误信息")

    # 新增字段
    results: List[SearchResult] = Field(default_factory=list, description="所有搜索结果")

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