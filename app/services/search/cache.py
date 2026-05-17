"""搜索缓存管理"""

import time
import logging
from typing import Optional, List
from app.models.search import SearchSummary


logger = logging.getLogger(__name__)


class SearchCacheManager:
    """搜索缓存管理器"""

    def __init__(self, default_ttl: int = 900):
        """
        初始化缓存管理器

        Args:
            default_ttl: 默认缓存时间（秒），默认15分钟
        """
        self._cache: dict[str, dict] = {}
        self.default_ttl = default_ttl

    def get(self, stock_code: str) -> Optional[SearchSummary]:
        """
        从缓存获取搜索结果

        Args:
            stock_code: 股票代码

        Returns:
            缓存的搜索结果，如果不存在或已过期则返回None
        """
        cached = self._cache.get(stock_code)
        if not cached:
            return None

        # 检查是否过期
        if time.time() - cached["timestamp"] > cached["ttl"]:
            logger.debug(f"缓存已过期: {stock_code}")
            del self._cache[stock_code]
            return None

        logger.debug(f"从缓存获取搜索结果: {stock_code}")
        return cached["data"]

    def set(self, stock_code: str, data: SearchSummary, ttl: Optional[int] = None):
        """
        设置缓存

        Args:
            stock_code: 股票代码
            data: 搜索结果
            ttl: 缓存时间（秒），默认使用default_ttl
        """
        ttl = ttl or self.default_ttl
        self._cache[stock_code] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl
        }
        logger.debug(f"缓存搜索结果: {stock_code}, TTL={ttl}秒")

    def clear(self, stock_code: Optional[str] = None):
        """
        清除缓存

        Args:
            stock_code: 股票代码，如果为None则清除所有缓存
        """
        if stock_code:
            self._cache.pop(stock_code, None)
            logger.debug(f"清除缓存: {stock_code}")
        else:
            self._cache.clear()
            logger.debug("清除所有缓存")

    def cleanup_expired(self):
        """清理所有过期的缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if current_time - value["timestamp"] > value["ttl"]
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"清理过期缓存: {len(expired_keys)}个")
