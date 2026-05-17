"""可靠的搜索服务

结合稳定的API和LLM验证，确保信息可靠性
"""

import logging
from typing import Optional
from app.services.reliable_info.api_fetcher import FinancialAPIFetcher
from app.services.reliable_info.llm_verifier import LLMInfoVerifier
from app.services.search.cache import SearchCacheManager
from app.models.search import SearchSummary, SearchResult


logger = logging.getLogger(__name__)


class ReliableSearchService:
    """
    可靠的搜索服务

    采用多层级策略确保信息可靠：
    1. 优先使用稳定的金融API
    2. 使用LLM进行验证和补充
    3. 严格的来源验证
    4. 完整的缓存管理
    """

    def __init__(
        self,
        llm_service=None,
        cache_ttl: int = 900,
        search_days: int = 7,
        max_results: int = 10,
        enable_llm_verify: bool = True
    ):
        """
        初始化可靠的搜索服务

        Args:
            llm_service: LLM服务（用于验证和补充）
            cache_ttl: 缓存时间（秒）
            search_days: 搜索最近N天
            max_results: 最大结果数
            enable_llm_verify: 是否启用LLM验证
        """
        self.llm_service = llm_service
        self.cache_ttl = cache_ttl
        self.search_days = search_days
        self.max_results = max_results
        self.enable_llm_verify = enable_llm_verify

        self.api_fetcher = FinancialAPIFetcher()
        self.cache = SearchCacheManager(default_ttl=cache_ttl)

        if llm_service and enable_llm_verify:
            self.llm_verifier = LLMInfoVerifier(llm_service)
        else:
            self.llm_verifier = None

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
                logger.info(f"使用缓存数据: {stock_code}")
                return cached

        logger.info(f"开始搜索: {stock_name}({stock_code})")

        try:
            # 第一层：使用稳定的金融API获取信息
            api_results = await self.api_fetcher.fetch_stock_news(
                stock_code=stock_code,
                stock_name=stock_name,
                days=self.search_days,
                max_results=self.max_results
            )

            logger.info(f"API获取到 {len(api_results)} 条信息")

            # 第二层：使用LLM验证和补充（如果启用）
            if self.llm_verifier and self.llm_verifier.is_network_enabled():
                logger.info("使用LLM验证和补充信息")
                final_results = await self.llm_verifier.verify_and_enhance(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    existing_results=api_results,
                    days=self.search_days
                )
            else:
                final_results = api_results

            # 可信度评估
            from app.services.search.evaluator import ReliabilityEvaluator
            evaluator = ReliabilityEvaluator(use_llm_evaluation=False)
            final_results = await evaluator.evaluate_batch(final_results)

            # 构建汇总
            summary = SearchSummary(
                stock_code=stock_code,
                stock_name=stock_name,
                total_results=len(final_results),
                high_reliability_count=sum(
                    1 for r in final_results
                    if r.reliability_score.score >= 0.8
                ),
                medium_reliability_count=sum(
                    1 for r in final_results
                    if 0.5 <= r.reliability_score.score < 0.8
                ),
                low_reliability_count=sum(
                    1 for r in final_results
                    if r.reliability_score.score < 0.5
                ),
                latest_news_date=max(
                    (r.publish_date for r in final_results if r.publish_date),
                    default=None
                ),
                results=final_results,
            )

            # 缓存结果
            self.cache.set(stock_code, summary, self.cache_ttl)

            logger.info(
                f"搜索完成: {stock_name}({stock_code}), "
                f"总计{len(final_results)}条, "
                f"高可信度{summary.high_reliability_count}条"
            )

            return summary

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            # 返回空结果
            return SearchSummary(
                stock_code=stock_code,
                stock_name=stock_name,
                total_results=0,
                high_reliability_count=0,
                medium_reliability_count=0,
                low_reliability_count=0,
                results=[]
            )

    async def close(self):
        """关闭服务"""
        await self.api_fetcher.close()
