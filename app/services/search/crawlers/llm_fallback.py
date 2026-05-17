"""LLM备用搜索器"""

import logging
from typing import List, Optional
from datetime import datetime
from app.models.search import (
    SearchResult, CrawlerConfig, SourceType, ContentType
)
from .base import CrawlerBase


logger = logging.getLogger(__name__)


class LLMFallbackSearcher(CrawlerBase):
    """
    LLM备用搜索器

    当传统爬虫失败时，使用支持联网的LLM模型进行搜索
    """

    def __init__(self, config: Optional[CrawlerConfig] = None, llm_service=None):
        """
        初始化LLM备用搜索器

        Args:
            config: 爬虫配置
            llm_service: LLM服务实例
        """
        super().__init__(config)
        self.llm_service = llm_service

    @property
    def base_url(self) -> str:
        return "llm://search"

    @property
    def source_name(self) -> str:
        return "LLM联网搜索"

    @property
    def source_type(self) -> SourceType:
        return SourceType.OTHER

    async def search(
        self,
        stock_code: str,
        stock_name: str,
        days: int = 7
    ) -> List[SearchResult]:
        """
        使用LLM联网能力搜索

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 搜索最近N天

        Returns:
            搜索结果列表
        """
        if not self.llm_service:
            logger.warning("LLM服务未配置，无法使用LLM备用搜索")
            return []

        logger.debug(f"LLM联网搜索: {stock_name}({stock_code})")

        try:
            # 构建搜索Prompt
            search_prompt = self._build_search_prompt(
                stock_code, stock_name, days
            )

            # 调用LLM进行搜索
            # 注意：这需要LLM模型支持联网功能
            # 例如Claude with computer use, GPT-4 with browsing等
            response = await self._call_llm_with_search(search_prompt)

            # 解析LLM响应
            results = self._parse_llm_response(response, stock_code)

            logger.debug(f"LLM联网搜索: 找到{len(results)}条结果")
            return results

        except Exception as e:
            logger.error(f"LLM联网搜索失败: {e}")
            return []

    def _build_search_prompt(
        self,
        stock_code: str,
        stock_name: str,
        days: int
    ) -> str:
        """构建搜索Prompt"""
        return f"""请使用联网搜索功能，查找"{stock_name}({stock_code})"在最近{days}天的重要信息。

搜索重点：
1. 官方公告（巨潮资讯网、交易所公告）
2. 重大新闻（主流财经媒体）
3. 财务报告
4. 重大事件（并购、重组、分红等）

请以JSON格式返回搜索结果，包含以下字段：
- title: 标题
- content: 内容摘要
- url: 来源链接
- source: 来源网站
- publish_date: 发布时间（YYYY-MM-DD格式）
- relevance: 相关性得分（0-1）

返回格式示例：
```json
{{
  "results": [
    {{
      "title": "公司公告标题",
      "content": "内容摘要",
      "url": "https://...",
      "source": "巨潮资讯网",
      "publish_date": "2025-05-08",
      "relevance": 0.95
    }}
  ]
}}
```
"""

    async def _call_llm_with_search(self, prompt: str) -> str:
        """调用支持联网的LLM"""
        # 这里需要根据具体的LLM服务实现
        # 如果使用Claude with computer use或GPT-4 with browsing
        # 需要在llm_service中添加相应的方法

        # 临时实现：直接调用LLM（不联网）
        # 实际使用时需要配置支持联网的模型
        if self.llm_service:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的金融信息搜索助手，擅长查找和整理股票相关信息。"
                },
                {"role": "user", "content": prompt}
            ]
            # 注意：这需要LLM服务支持JSON响应
            # response = await self.llm_service._call_llm(messages)
            # return response

        # 如果没有配置联网功能，返回空结果
        logger.warning("LLM服务未配置联网功能")
        return '{"results": []}'

    def _parse_llm_response(
        self,
        response: str,
        stock_code: str
    ) -> List[SearchResult]:
        """解析LLM响应"""
        import json

        try:
            data = json.loads(response)
            results_list = data.get("results", [])

            results = []
            for item in results_list:
                try:
                    # 解析发布日期
                    publish_date = None
                    date_str = item.get("publish_date", "")
                    if date_str:
                        try:
                            publish_date = datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            pass

                    result = SearchResult(
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        url=item.get("url", ""),
                        source=item.get("source", "LLM搜索"),
                        source_type=SourceType.OTHER,
                        content_type=ContentType.NEWS,
                        publish_date=publish_date,
                        stock_code=stock_code,
                        relevance_score=item.get("relevance", 0.5)
                    )
                    results.append(result)

                except Exception as e:
                    logger.warning(f"解析单个结果失败: {e}")

            return results

        except json.JSONDecodeError as e:
            logger.error(f"解析LLM响应失败: {e}")
            return []
