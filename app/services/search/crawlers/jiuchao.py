"""巨潮资讯网爬虫"""

import logging
from typing import List
from datetime import datetime, timedelta
from urllib.parse import urljoin
from app.models.search import (
    SearchResult, CrawlerConfig, SourceType, ContentType
)
from .base import CrawlerBase


logger = logging.getLogger(__name__)


class JiuchaoCrawler(CrawlerBase):
    """
    巨潮资讯网爬虫

    巨潮资讯网是中国证监会指定的上市公司信息披露网站
    """

    @property
    def base_url(self) -> str:
        return "http://www.cninfo.com.cn"

    @property
    def source_name(self) -> str:
        return "巨潮资讯网"

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
        搜索巨潮资讯网公告

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 搜索最近N天

        Returns:
            搜索结果列表
        """
        logger.debug(f"巨潮资讯网搜索: {stock_name}({stock_code})")

        results = []

        try:
            # 构建搜索API URL
            # 注意：巨潮资讯网的API可能会变化，这里提供一个基础框架
            search_url = f"{self.base_url}/new/hisAnnouncement/query"

            # 构建查询参数
            params = {
                "stock": f"{stock_code},",  # 股票代码
                "searchkey": stock_name,    # 搜索关键词
                "plate": "",                # 板块
                "category": "",             # 分类
                "trade": "",                # 行业
                "column": "szse_main",      # 栏目
                "columnTitle": "历史公告查询",
                "pageNum": 1,
                "pageSize": self.config.max_results,
                "tabName": "fulltext",
                "sortName": "",
                "sortType": "",
                "limit": "",
                "showType": "",
                "seDate": self._get_date_range(days),
            }

            # 发送请求
            response = await self._fetch_with_retry(
                search_url,
                method="POST",
                data=params
            )

            if response:
                # 解析响应
                data = response.json()
                if data.get("hasmore") is not False:
                    announcements = data.get("announcements", [])

                    for ann in announcements:
                        result = self._parse_announcement(ann, stock_code)
                        if result:
                            results.append(result)

        except Exception as e:
            logger.error(f"巨潮资讯网搜索失败: {e}")

        # 过滤和限制结果
        results = self._filter_by_date(results, days)
        results = self._limit_results(results)

        logger.debug(f"巨潮资讯网: 找到{len(results)}条结果")
        return results

    def _parse_announcement(
        self,
        ann: dict,
        stock_code: str
    ) -> SearchResult:
        """解析公告数据"""
        try:
            # 提取公告标题
            title = ann.get("announcementTitle", "")

            # 提取附件URL列表
            adjunct_urls = ann.get("adjunctUrl", [])
            if not isinstance(adjunct_urls, list) or not adjunct_urls:
                adjunct_urls = ann.get("adjunctSize", [])

            url = ""
            if adjunct_urls:
                url = urljoin(
                    self.base_url,
                    adjunct_urls[0] if isinstance(adjunct_urls[0], str) else ""
                )

            # 发布时间
            publish_date_str = ann.get("announcementTime", "")
            publish_date = None
            if publish_date_str:
                try:
                    publish_date = datetime.strptime(
                        publish_date_str,
                        "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    pass

            # 相关性
            stock_name = ann.get("secName", stock_code)
            relevance = self._calculate_relevance(title, stock_code, stock_name)

            return SearchResult(
                title=title,
                content=ann.get("announcementContent", "")[:200],  # 前200字作为摘要
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

    def _get_date_range(self, days: int) -> str:
        """
        获取日期范围字符串

        Args:
            days: 最近N天

        Returns:
            日期范围字符串，格式: "YYYY-MM-DD~YYYY-MM-DD"
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"
