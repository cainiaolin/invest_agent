"""爬虫基类"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
from app.models.search import SearchResult, CrawlerConfig, SourceType, ContentType


logger = logging.getLogger(__name__)


class CrawlerBase(ABC):
    """
    爬虫基类

    所有爬虫的抽象基类，定义统一接口
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        初始化爬虫

        Args:
            config: 爬虫配置
        """
        self.config = config or CrawlerConfig(base_url=self.base_url)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    @abstractmethod
    def base_url(self) -> str:
        """爬虫的基础URL（子类实现）"""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """来源名称（子类实现）"""
        pass

    @property
    def source_type(self) -> SourceType:
        """来源类型（子类可覆盖）"""
        return SourceType.OTHER

    @property
    def client(self) -> httpx.AsyncClient:
        """获取或创建HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers={"User-Agent": self.config.user_agent}
            )
        return self._client

    async def close(self):
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def search(
        self,
        stock_code: str,
        stock_name: str,
        days: int = 7
    ) -> List[SearchResult]:
        """
        搜索股票信息（子类实现）

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 搜索最近N天的信息

        Returns:
            搜索结果列表
        """
        pass

    async def _fetch_with_retry(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Optional[httpx.Response]:
        """
        带重试的HTTP请求

        Args:
            url: 请求URL
            method: 请求方法
            **kwargs: 其他请求参数

        Returns:
            响应对象，失败返回None
        """
        for attempt in range(self.config.retry_times):
            try:
                # 请求延迟
                if attempt > 0:
                    await asyncio.sleep(self.config.delay * (attempt + 1))

                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP错误: {url} - {e}")
                if attempt == self.config.retry_times - 1:
                    return None
            except httpx.RequestError as e:
                logger.warning(f"请求错误: {url} - {e}")
                if attempt == self.config.retry_times - 1:
                    return None
            except Exception as e:
                logger.error(f"未知错误: {url} - {e}")
                return None

        return None

    def _calculate_relevance(
        self,
        title: str,
        stock_code: str,
        stock_name: str
    ) -> float:
        """
        计算相关性得分

        Args:
            title: 标题
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            相关性得分 0-1
        """
        score = 0.0
        title_upper = title.upper()

        # 股票代码匹配（权重0.4）
        if stock_code in title_upper:
            score += 0.4

        # 股票名称匹配（权重0.6）
        if stock_name in title:
            score += 0.6

        return min(score, 1.0)

    def _filter_by_date(
        self,
        results: List[SearchResult],
        days: int
    ) -> List[SearchResult]:
        """
        按日期过滤结果

        Args:
            results: 搜索结果列表
            days: 最近N天

        Returns:
            过滤后的结果列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            r for r in results
            if r.publish_date and r.publish_date >= cutoff_date
        ]

    def _limit_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        限制结果数量

        Args:
            results: 搜索结果列表

        Returns:
            限制后的结果列表
        """
        # 按相关性和发布时间排序
        sorted_results = sorted(
            results,
            key=lambda r: (r.relevance_score, r.publish_date or datetime.min),
            reverse=True
        )
        return sorted_results[:self.config.max_results]
