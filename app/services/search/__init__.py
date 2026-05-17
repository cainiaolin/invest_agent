"""搜索服务模块"""

from app.services.search.factory import create_search_service
from app.services.search.base import WebSearchService
from app.services.search.enricher import SearchDataEnricher

# 向后兼容别名
SearchService = WebSearchService

__all__ = ["create_search_service", "WebSearchService", "SearchService", "SearchDataEnricher"]