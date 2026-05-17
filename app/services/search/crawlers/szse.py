"""深交所爬虫"""

import logging
from typing import List
from datetime import datetime, timedelta
from urllib.parse import urljoin
from app.models.search import (
    SearchResult, CrawlerConfig, SourceType, ContentType
)
from .base import CrawlerBase


logger = logging.getLogger(__name__)


class SZSECrawler(CrawlerBase):
    """
    深圳证券交易所爬虫

    爬取深交所公告信息
    """

    @property
    def base_url(self) -> str:
        return "http://www.szse.cn"

    @property
    def source_name(self) -> str:
        return "深圳证券交易所"

    @property
    def source_type(self) -> SourceType:
        return SourceType.OFFICIAL

    async def search(
        self,
        stock_code: str,
        stock_name: str,
        days: int = 7
    ) -> List[SearchResult]:
        """
        搜索深交所公告

        Args:
            stock_code: 股票代码（0或3开头）
            stock_name: 股票名称
            days: 搜索最近N天

        Returns:
            搜索结果列表
        """
        logger.debug(f"深交所搜索: {stock_name}({stock_code})")

        results = []

        # 只处理0或3开头的股票代码（深市）
        if not (stock_code.startswith("0") or stock_code.startswith("3")):
            logger.debug(f"非深市股票代码，跳过深交所搜索: {stock_code}")
            return results

        try:
            # 深交所公告查询API
            search_url = f"{self.base_url}/api/disclosure/announ"

            params = {
                "stockCode": stock_code,
                "stockName": stock_name,
                "startTime": self._get_start_date(days),
                "endTime": self._get_end_date(),
                "pageSize": self.config.max_results,
            }

            response = await self._fetch_with_retry(
                search_url,
                method="GET",
                params=params
            )

            if response:
                data = response.json()
                announcements = data.get("data", [])

                for ann in announcements:
                    result = self._parse_announcement(ann, stock_code)
                    if result:
                        results.append(result)

        except Exception as e:
            logger.error(f"深交所搜索失败: {e}")

        # 过滤和限制结果
        results = self._filter_by_date(results, days)
        results = self._limit_results(results)

        logger.debug(f"深交所: 找到{len(results)}条结果")
        return results

    def _parse_announcement(
        self,
        ann: dict,
        stock_code: str
    ) -> SearchResult:
        """解析公告数据"""
        try:
            title = ann.get("title", "")
            url = urljoin(self.base_url, ann.get("url", ""))

            publish_date_str = ann.get("publishTime", "")
            publish_date = None
            if publish_date_str:
                try:
                    publish_date = datetime.strptime(publish_date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass

            stock_name = ann.get("stockName", stock_code)
            relevance = self._calculate_relevance(title, stock_code, stock_name)

            return SearchResult(
                title=title,
                content=ann.get("summary", "")[:200],
                url=url,
                source=self.source_name,
                source_type=self.source_type,
                content_type=ContentType.ANNOUNCEMENT,
                publish_date=publish_date,
                stock_code=stock_code,
                relevance_score=relevance
            )

        except Exception as e:
            logger.warning(f"解析公告失败: {e}")
            return None

    def _get_start_date(self, days: int) -> str:
        """获取开始日期"""
        start_date = datetime.now() - timedelta(days=days)
        return start_date.strftime("%Y-%m-%d")

    def _get_end_date(self) -> str:
        """获取结束日期"""
        return datetime.now().strftime("%Y-%m-%d")
