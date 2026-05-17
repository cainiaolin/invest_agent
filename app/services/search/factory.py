"""搜索服务工厂"""

import logging
from app.services.search.base import WebSearchService
from app.services.search.crawlers import (
    JiuchaoCrawler,
    SSECrawler,
    SZSECrawler,
    LLMFallbackSearcher
)
from app.core.config import settings


logger = logging.getLogger(__name__)


def create_search_service(llm_service=None) -> WebSearchService:
    """
    创建搜索服务实例

    Args:
        llm_service: LLM服务实例（用于LLM备用搜索）

    Returns:
        配置好的搜索服务实例
    """
    if not settings.search_enabled:
        logger.info("搜索增强功能未启用")
        return None

    # 创建搜索服务
    search_service = WebSearchService(
        cache_ttl=settings.search_cache_ttl,
        search_days=settings.search_days,
        max_results=settings.search_max_results,
        use_llm_fallback=settings.search_fallback_llm
    )

    # 创建爬虫配置
    from app.models.search import CrawlerConfig
    crawler_config = CrawlerConfig(
        user_agent=settings.crawler_user_agent,
        timeout=settings.crawler_timeout,
        retry_times=settings.crawler_retry,
        delay=settings.crawler_delay,
        max_results=settings.search_max_results
    )

    # 注册爬虫
    crawlers = [
        JiuchaoCrawler(crawler_config),
        SSECrawler(crawler_config),
        SZSECrawler(crawler_config)
    ]

    for crawler in crawlers:
        search_service.register_crawler(crawler)

    # 如果启用LLM备用搜索，注册LLM搜索器
    if settings.search_fallback_llm and llm_service:
        llm_searcher = LLMFallbackSearcher(crawler_config, llm_service)
        search_service.register_crawler(llm_searcher)

    logger.info("搜索服务初始化完成，已注册%d个爬虫", len(crawlers))

    return search_service
