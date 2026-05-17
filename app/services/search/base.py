"""网络搜索服务基类"""

import logging
from typing import List
from abc import ABC, abstractmethod
from app.models.search import SearchResult, SearchSummary, CrawlerConfig
from app.services.search.cache import SearchCacheManager
from app.services.search.evaluator import ReliabilityEvaluator
from app.services.search.enricher import SearchDataEnricher


logger = logging.getLogger(__name__)


class WebSearchService:
    """
    网络搜索服务

    统一的搜索接口，整合多个爬虫源
    """

    def __init__(
        self,
        cache_ttl: int = 900,
        search_days: int = 7,
        max_results: int = 10,
        use_llm_fallback: bool = True
    ):
        """
        初始化搜索服务

        Args:
            cache_ttl: 缓存时间（秒）
            search_days: 搜索最近N天的信息
            max_results: 每个源的最大结果数
            use_llm_fallback: 是否启用LLM备用搜索
        """
        self.cache_ttl = cache_ttl
        self.search_days = search_days
        self.max_results = max_results
        self.use_llm_fallback = use_llm_fallback

        self.cache = SearchCacheManager(default_ttl=cache_ttl)
        self.evaluator = ReliabilityEvaluator()
        self.enricher = SearchDataEnricher()

        # 爬虫列表（在子类或初始化时填充）
        self._crawlers: List["CrawlerBase"] = []

    def register_crawler(self, crawler: "CrawlerBase"):
        """注册爬虫"""
        self._crawlers.append(crawler)
        logger.info(f"注册爬虫: {crawler.__class__.__name__}")

    async def search_stock_info(
        self,
        stock_code: str,
        stock_name: str,
        force_refresh: bool = False
    ) -> SearchSummary:
        """
        搜索股票相关信息

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            force_refresh: 是否强制刷新（忽略缓存）

        Returns:
            搜索结果汇总
        """
        # 检查缓存
        if not force_refresh:
            cached = self.cache.get(stock_code)
            if cached:
                return cached

        logger.info(f"开始搜索: {stock_name}({stock_code})")
        all_results = []

        # 使用所有爬虫搜索
        for crawler in self._crawlers:
            try:
                results = await crawler.search(stock_code, stock_name, self.search_days)
                all_results.extend(results)
                logger.debug(f"{crawler.__class__.__name__}: 找到{len(results)}条结果")
            except Exception as e:
                logger.warning(f"{crawler.__class__.__name__} 搜索失败: {e}")

        # 如果没有结果且启用了LLM备用搜索
        if not all_results and self.use_llm_fallback:
            logger.info("爬虫无结果，尝试LLM备用搜索")
            # TODO: 实现LLM备用搜索

        # 评估可信度
        evaluated_results = await self.evaluator.evaluate_batch(all_results)

        # 构建汇总
        summary = SearchSummary(
            stock_code=stock_code,
            stock_name=stock_name,
            total_results=len(evaluated_results),
            high_reliability_count=sum(1 for r in evaluated_results if r.reliability_score.score >= 0.8),
            medium_reliability_count=sum(1 for r in evaluated_results if 0.5 <= r.reliability_score.score < 0.8),
            low_reliability_count=sum(1 for r in evaluated_results if r.reliability_score.score < 0.5),
            latest_news_date=max(
                (r.publish_date for r in evaluated_results if r.publish_date),
                default=None
            ),
            results=evaluated_results,
        )

        # 缓存结果
        self.cache.set(stock_code, summary, self.cache_ttl)

        logger.info(
            f"搜索完成: {stock_name}({stock_code}), "
            f"总计{len(evaluated_results)}条, "
            f"高可信度{summary.high_reliability_count}条"
        )

        return summary
