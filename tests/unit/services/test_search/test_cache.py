"""搜索缓存管理器测试"""

import pytest
import time
from app.services.search.cache import SearchCacheManager
from app.models.search import SearchSummary, SearchResult


@pytest.fixture
def cache_manager():
    """创建缓存管理器实例"""
    return SearchCacheManager(default_ttl=1)


@pytest.fixture
def sample_summary():
    """创建示例搜索结果"""
    return SearchSummary(
        stock_code="600519",
        stock_name="贵州茅台",
        total_results=2,
        high_reliability_count=1,
        medium_reliability_count=1,
        low_reliability_count=0,
        results=[
            SearchResult(
                title="公告标题",
                content="公告内容",
                url="http://example.com",
                source="巨潮资讯网",
                stock_code="600519",
                relevance_score=0.9
            )
        ]
    )


class TestSearchCacheManager:
    """搜索缓存管理器测试"""

    def test_set_and_get(self, cache_manager, sample_summary):
        """测试设置和获取缓存"""
        stock_code = "600519"

        # 设置缓存
        cache_manager.set(stock_code, sample_summary)

        # 获取缓存
        cached = cache_manager.get(stock_code)

        assert cached is not None
        assert cached.stock_code == stock_code
        assert cached.stock_name == "贵州茅台"
        assert cached.total_results == 2

    def test_cache_expiration(self, cache_manager, sample_summary):
        """测试缓存过期"""
        stock_code = "600519"

        # 设置缓存（TTL为1秒）
        cache_manager.set(stock_code, sample_summary, ttl=1)

        # 立即获取应该成功
        cached = cache_manager.get(stock_code)
        assert cached is not None

        # 等待2秒后获取应该失败
        time.sleep(2)
        cached = cache_manager.get(stock_code)
        assert cached is None

    def test_cache_clear_specific(self, cache_manager, sample_summary):
        """测试清除特定缓存"""
        stock_code = "600519"

        # 设置缓存
        cache_manager.set(stock_code, sample_summary)

        # 清除特定缓存
        cache_manager.clear(stock_code)

        # 获取应该失败
        cached = cache_manager.get(stock_code)
        assert cached is None

    def test_cache_clear_all(self, cache_manager, sample_summary):
        """测试清除所有缓存"""
        # 设置多个缓存
        cache_manager.set("600519", sample_summary)
        cache_manager.set("000858", sample_summary)

        # 清除所有缓存
        cache_manager.clear()

        # 获取应该失败
        assert cache_manager.get("600519") is None
        assert cache_manager.get("000858") is None

    def test_cleanup_expired(self, cache_manager, sample_summary):
        """测试清理过期缓存"""
        # 设置多个缓存，TTL不同
        cache_manager.set("600519", sample_summary, ttl=1)
        cache_manager.set("000858", sample_summary, ttl=10)

        # 等待第一个缓存过期
        time.sleep(2)

        # 清理过期缓存
        cache_manager.cleanup_expired()

        # 第一个应该被清除，第二个应该还在
        assert cache_manager.get("600519") is None
        assert cache_manager.get("000858") is not None
