"""搜索数据增强器 - 增强搜索结果并格式化为LLM友好的格式"""
import json
from typing import List, Dict, Any, Optional
from app.models.search import SearchResult, SearchSummary


class SearchDataEnricher:
    """搜索数据增强器"""

    def __init__(self):
        """初始化搜索数据增强器"""
        pass

    def format_for_llm(self, search_summary: SearchSummary) -> str:
        """
        将搜索结果格式化为LLM友好的格式

        Args:
            search_summary: 搜索结果摘要

        Returns:
            格式化的LLM友好内容
        """
        if not search_summary.has_valid_results:
            return f"""
搜索结果质量：{search_summary.quality_assessment}
搜索结果总数：{search_summary.total_results}

注意：当前搜索结果质量较低，建议：
1. 检查搜索关键词是否准确
2. 尝试不同的搜索策略
3. 扩大搜索时间范围
"""

        # 按质量分类结果
        high_quality_results = search_summary.get_results_by_quality("high")
        medium_quality_results = search_summary.get_results_by_quality("medium")
        low_quality_results = search_summary.get_results_by_quality("low")

        # 构建格式化内容
        formatted_content = f"""
=== 搜索结果摘要 ===
股票代码：{search_summary.stock_code}
搜索结果总数：{search_summary.total_results}
高质量结果数：{len(high_quality_results)}
中等质量结果数：{len(medium_quality_results)}
低质量结果数：{len(low_quality_results)}
搜索质量评估：{search_summary.quality_assessment}
搜索时间：{search_summary.search_timestamp}

"""

        # 添加高质量结果
        if high_quality_results:
            formatted_content += "=== 高质量信息源 ===\n"
            for i, result in enumerate(high_quality_results[:5], 1):
                formatted_content += f"""
[{i}] {result.title}
     来源：{result.source} | 可信度：{result.reliability:.2f} | 相关度：{result.relevance:.2f}
     发布时间：{result.timestamp}
     摘要：{result.content[:300]}...
"""
            formatted_content += "\n"

        # 添加中等质量结果
        if medium_quality_results:
            formatted_content += "=== 中等质量信息源 ===\n"
            for i, result in enumerate(medium_quality_results[:3], 1):
                formatted_content += f"""
[{i}] {result.title}
     来源：{result.source} | 可信度：{result.reliability:.2f} | 相关度：{result.relevance:.2f}
     摘要：{result.content[:200]}...
"""
            formatted_content += "\n"

        # 添加使用建议
        formatted_content += """
=== 使用建议 ===
"""

        if search_summary.quality_assessment == "high":
            formatted_content += "- 当前搜索结果质量高，可直接用于分析\n"
        elif search_summary.quality_assessment == "medium":
            formatted_content += "- 当前搜索结果质量中等，建议重点关注高质量信息\n"
        else:
            formatted_content += "- 当前搜索结果质量较低，建议结合其他数据源进行分析\n"

        if len(search_summary.search_keywords) > 0:
            formatted_content += f"- 搜索关键词：{', '.join(search_summary.search_keywords)}\n"

        return formatted_content

    def enrich_results(self, raw_results: List[Dict[str, Any]]) -> List[SearchResult]:
        """
        增强原始搜索结果

        Args:
            raw_results: 原始搜索结果列表

        Returns:
            增强后的搜索结果列表
        """
        enriched_results = []

        for raw_result in raw_results:
            # 计算质量评分
            high_quality_score = self._calculate_high_quality_score(raw_result)
            medium_quality_score = self._calculate_medium_quality_score(raw_result)
            low_quality_score = self._calculate_low_quality_score(raw_result)

            # 计算可信度
            reliability = self._calculate_reliability(raw_result, high_quality_score)

            # 创建搜索结果对象
            search_result = SearchResult(
                title=raw_result.get("title", ""),
                url=raw_result.get("url", ""),
                content=raw_result.get("content", ""),
                source=raw_result.get("source", "unknown"),
                reliability=reliability,
                relevance=raw_result.get("relevance", 0.0),
                timestamp=raw_result.get("timestamp", ""),
                author=raw_result.get("author"),
                high_quality_score=high_quality_score,
                medium_quality_score=medium_quality_score,
                low_quality_score=low_quality_score
            )

            enriched_results.append(search_result)

        return enriched_results

    def _calculate_high_quality_score(self, raw_result: Dict[str, Any]) -> float:
        """计算高质量得分"""
        score = 0.0

        # 权威机构发布
        if raw_result.get("source_type") in ["official", "regulatory", "exchange"]:
            score += 0.4

        # 专业评级报告
        if "rating" in raw_result.get("content", "").lower():
            score += 0.3

        # 有明确的财务数据
        if any(keyword in raw_result.get("content", "").lower()
               for keyword in ["revenue", "profit", "eps", "roe", "roa"]):
            score += 0.2

        # 有明确的时间戳
        if raw_result.get("timestamp"):
            score += 0.1

        return min(score, 1.0)

    def _calculate_medium_quality_score(self, raw_result: Dict[str, Any]) -> float:
        """计算中等质量得分"""
        score = 0.0

        # 一般财经媒体
        if raw_result.get("source_type") in ["news", "financial"]:
            score += 0.3

        # 有分析师观点
        if "analyst" in raw_result.get("content", "").lower():
            score += 0.3

        # 有行业对比
        if "industry" in raw_result.get("content", "").lower():
            score += 0.2

        # 有作者署名
        if raw_result.get("author"):
            score += 0.2

        return min(score, 1.0)

    def _calculate_low_quality_score(self, raw_result: Dict[str, Any]) -> float:
        """计算低质量得分"""
        score = 0.0

        # 社交媒体或论坛
        if raw_result.get("source_type") in ["social", "forum"]:
            score += 0.3

        # 缺少具体信息
        if len(raw_result.get("content", "")) < 100:
            score += 0.4

        # 情绪化语言多
        emotional_words = ["暴涨", "暴跌", "翻倍", "归零", "暴富", "血亏"]
        if any(word in raw_result.get("content", "") for word in emotional_words):
            score += 0.3

        return min(score, 1.0)

    def _calculate_reliability(self, raw_result: Dict[str, Any],
                              high_quality_score: float) -> float:
        """计算结果可信度"""
        base_reliability = 0.5

        # 来源权重
        source_weights = {
            "official": 0.3,
            "regulatory": 0.25,
            "exchange": 0.2,
            "news": 0.1,
            "financial": 0.08,
            "social": -0.1,
            "forum": -0.15
        }

        source_type = raw_result.get("source_type", "unknown")
        source_weight = source_weights.get(source_type, 0.0)

        # 质量得分权重
        quality_weight = high_quality_score * 0.3

        # 时间权重（最新的更可靠）
        if raw_result.get("timestamp"):
            # 简单的时间权重计算
            time_weight = 0.1
        else:
            time_weight = -0.1

        total_reliability = base_reliability + source_weight + quality_weight + time_weight
        return max(0.0, min(1.0, total_reliability))