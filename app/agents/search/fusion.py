"""信息融合器 - 负责将搜索结果与股票数据融合"""
from typing import Dict, Any, Union
from app.models.search import SearchSummary
from app.services.search.enricher import SearchDataEnricher


class InformationFusion:
    """信息融合器类 - 负责将搜索结果与股票数据融合，生成LLM友好的分析上下文"""

    def __init__(self):
        """
        初始化信息融合器
        创建SearchDataEnricher实例用于格式化搜索结果
        """
        self.enricher = SearchDataEnricher()

    def merge(self, search_summary: SearchSummary, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        融合搜索结果和股票数据

        Args:
            search_summary: 搜索结果摘要
            stock_data: 股票基础数据

        Returns:
            融合后的数据字典，包含：
            - search_summary: 搜索结果摘要
            - stock_data: 股票数据
            - has_search_data: 是否有搜索数据
            - search_quality: 搜索质量评级
        """
        # 使用SearchSummary内置的质量评估
        search_quality = search_summary.quality_assessment

        # 构建返回结果
        result = {
            "search_summary": search_summary,
            "stock_data": stock_data,
            "has_search_data": search_summary.total_results > 0,
            "search_quality": search_quality
        }

        return result

    def format_for_llm(self, search_summary: SearchSummary, stock_data: Dict[str, Any]) -> str:
        """
        格式化为LLM友好的分析上下文

        Args:
            search_summary: 搜索结果摘要
            stock_data: 股票基础数据

        Returns:
            格式化的LLM友好上下文文本
        """
        # 生成股票基本信息
        stock_basic_info = self._format_stock_basic_info(stock_data)

        # 生成搜索结果信息（通过SearchDataEnricher）
        search_info = self.enricher.format_for_llm(search_summary)

        # 生成数据融合说明
        fusion_note = self._format_fusion_note(search_summary, stock_data)

        # 用分隔符连接各部分
        formatted_context = f"{stock_basic_info}\n\n---\n\n{search_info}\n\n---\n\n{fusion_note}"

        return formatted_context

    def _format_stock_basic_info(self, stock_data: Dict[str, Any]) -> str:
        """
        格式化股票基本信息

        Args:
            stock_data: 股票数据字典

        Returns:
            格式化的股票基本信息
        """
        info_lines = [
            "=== 股票基本信息 ===",
            f"股票名称：{stock_data.get('stock_name', '未知')}",
            f"股票代码：{stock_data.get('stock_code', '未知')}",
            f"所属行业：{stock_data.get('industry', '未知')}"
        ]

        # 添加财务指标（如果存在）
        if stock_data.get('roe') is not None:
            info_lines.append(f"ROE：{stock_data['roe']:.1%}")
        if stock_data.get('pe_ratio') is not None:
            info_lines.append(f"市盈率：{stock_data['pe_ratio']:.1f}")
        if stock_data.get('market_cap') is not None:
            info_lines.append(f"市值：{stock_data['market_cap']}")

        # 添加价格信息（如果存在）
        if stock_data.get('current_price') is not None:
            info_lines.append(f"当前股价：{stock_data['current_price']:.2f}")
        if stock_data.get('change_percent') is not None:
            change_str = f"{stock_data['change_percent']:+.1f}%"
            info_lines.append(f"涨跌幅：{change_str}")

        return "\n".join(info_lines)

    def _format_fusion_note(self, search_summary: SearchSummary, stock_data: Dict[str, Any]) -> str:
        """
        格式化数据融合说明

        Args:
            search_summary: 搜索结果摘要
            stock_data: 股票数据

        Returns:
            格式化的数据融合说明
        """
        info_lines = [
            "=== 数据融合说明 ===",
            f"股票代码：{search_summary.stock_code}",
            f"总搜索结果：{search_summary.total_results}条"
        ]

        # 添加质量分布
        info_lines.extend([
            f"高质量：{search_summary.high_quality_count}条 ({search_summary.high_ratio:.1%})",
            f"中等质量：{search_summary.medium_quality_count}条",
            f"低质量：{search_summary.low_quality_count}条"
        ])

        # 添加搜索质量评估
        info_lines.append(f"搜索质量评估：{search_summary.quality_assessment}")

        # 添加使用建议
        info_lines.append("\n建议：")
        if search_summary.quality_assessment == "high":
            info_lines.append("- 当前搜索结果质量高，可直接用于分析")
        elif search_summary.quality_assessment == "medium":
            info_lines.append("- 当前搜索结果质量中等，建议重点关注高质量信息")
        else:
            info_lines.append("- 当前搜索结果质量较低，建议结合其他数据源进行分析")

        # 添加搜索关键词（如果存在）
        if search_summary.search_keywords:
            info_lines.append(f"- 搜索关键词：{', '.join(search_summary.search_keywords)}")

        return "\n".join(info_lines)


