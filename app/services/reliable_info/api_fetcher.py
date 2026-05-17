"""金融API数据获取器

使用稳定的金融API接口获取实时信息，避免爬虫的不稳定性。
所有API均为官方或主流财经媒体提供的公开接口。
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
from app.models.search import SearchResult, SourceType, ContentType


logger = logging.getLogger(__name__)


class FinancialAPIFetcher:
    """
    金融API数据获取器

    使用多个稳定的金融API作为数据源：
    1. 东方财富API - 数据全面，更新及时
    2. 新浪财经API - 稳定可靠
    3. 腾讯财经API - 备用数据源
    """

    def __init__(self, timeout: int = 10):
        """
        初始化API获取器

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def fetch_stock_news(
        self,
        stock_code: str,
        stock_name: str,
        days: int = 7,
        max_results: int = 10
    ) -> List[SearchResult]:
        """
        获取股票新闻

        按优先级尝试多个API，直到获取到数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 查询最近N天
            max_results: 最大结果数

        Returns:
            新闻列表
        """
        # API列表按优先级排序
        apis = [
            self._fetch_from_eastmoney,
            self._fetch_from_sina,
            self._fetch_from_tencent,
        ]

        for api_func in apis:
            try:
                logger.info(f"尝试使用 {api_func.__name__} 获取新闻")
                results = await api_func(stock_code, stock_name, days, max_results)
                if results:
                    logger.info(f"{api_func.__name__} 成功获取 {len(results)} 条新闻")
                    return results
            except Exception as e:
                logger.warning(f"{api_func.__name__} 失败: {e}")
                continue

        logger.warning("所有API均失败")
        return []

    async def _fetch_from_eastmoney(
        self,
        stock_code: str,
        stock_name: str,
        days: int,
        max_results: int
    ) -> List[SearchResult]:
        """
        从东方财富API获取新闻

        API说明：东方财富提供了稳定的新闻API接口
        """
        try:
            # 东方财富新闻API
            # 格式: http://np-anotice-stock.eastmoney.com/api/security/ann
            url = "http://np-anotice-stock.eastmoney.com/api/security/ann"

            # 构建查询参数
            params = {
                "sr": "-1",  # 排序方式
                "page_size": max_results,
                "page_index": 1,
                "ann_type": "PA",  # 公告类型
                "client_source": "web",
                "f_node": "0",
                "s_node": "0"
            }

            # 添加股票代码过滤
            stock_list = []
            if stock_code.startswith("6"):
                # 沪市
                stock_list.append(f"1.{stock_code}")
            elif stock_code.startswith(("0", "3")):
                # 深市
                stock_list.append(f"0.{stock_code}")

            if stock_list:
                params["stock_list"] = ",".join(stock_list)

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # 解析结果
            results = []
            if data.get("code") == 0 and "data" in data:
                items = data["data"].get("list", [])

                for item in items[:max_results]:
                    try:
                        # 解析时间
                        publish_date = None
                        if item.get("show_date"):
                            try:
                                publish_date = datetime.strptime(
                                    item["show_date"],
                                    "%Y-%m-%d"
                                )
                            except ValueError:
                                pass

                        # 只保留最近N天的新闻
                        if publish_date and publish_date < datetime.now() - timedelta(days=days):
                            continue

                        result = SearchResult(
                            title=item.get("title", ""),
                            content=item.get("abstract", "")[:200],
                            url=item.get("art_code", ""),
                            source="东方财富",
                            source_type=SourceType.MAINSTREAM,
                            content_type=ContentType.ANNOUNCEMENT,
                            publish_date=publish_date,
                            stock_code=stock_code,
                            relevance_score=self._calculate_relevance(
                                item.get("title", ""),
                                stock_code,
                                stock_name
                            )
                        )
                        results.append(result)

                    except Exception as e:
                        logger.warning(f"解析单条新闻失败: {e}")

            return results

        except Exception as e:
            logger.error(f"东方财富API调用失败: {e}")
            raise

    async def _fetch_from_sina(
        self,
        stock_code: str,
        stock_name: str,
        days: int,
        max_results: int
    ) -> List[SearchResult]:
        """
        从新浪财经API获取新闻

        API说明：新浪财经提供公开的新闻API
        """
        try:
            # 新浪财经新闻API
            url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_AllNewsStock"

            # 构建查询参数
            params = {
                "symbol": f"sh{stock_code}" if stock_code.startswith("6") else f"sz{stock_code}",
                "page": 1
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            # 新浪返回的是HTML，需要解析
            # 这里使用简单的文本匹配提取信息
            from html.parser import HTMLParser

            class SinaNewsParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.results = []
                    self.in_link = False
                    self.current_url = ""
                    self.current_title = ""

                def handle_starttag(self, tag, attrs):
                    if tag == "a":
                        for attr, value in attrs:
                            if attr == "href":
                                self.current_url = value
                                self.in_link = True

                def handle_data(self, data):
                    if self.in_link:
                        self.current_title = data.strip()

                def handle_endtag(self, tag):
                    if tag == "a" and self.in_link:
                        if self.current_title and self.current_url:
                            self.results.append({
                                "title": self.current_title,
                                "url": self.current_url
                            })
                        self.in_link = False
                        self.current_url = ""
                        self.current_title = ""

            parser = SinaNewsParser()
            parser.feed(response.text)

            results = []
            for item in parser.results[:max_results]:
                try:
                    result = SearchResult(
                        title=item["title"],
                        content="",  # 新浪API不提供内容摘要
                        url=item["url"],
                        source="新浪财经",
                        source_type=SourceType.MAINSTREAM,
                        content_type=ContentType.NEWS,
                        publish_date=None,  # 新浪API不提供精确日期
                        stock_code=stock_code,
                        relevance_score=self._calculate_relevance(
                            item["title"],
                            stock_code,
                            stock_name
                        )
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"解析单条新闻失败: {e}")

            return results

        except Exception as e:
            logger.error(f"新浪财经API调用失败: {e}")
            raise

    async def _fetch_from_tencent(
        self,
        stock_code: str,
        stock_name: str,
        days: int,
        max_results: int
    ) -> List[SearchResult]:
        """
        从腾讯财经API获取新闻

        API说明：腾讯财经提供JSON格式的新闻API
        """
        try:
            # 腾讯财经新闻API
            url = "https://qt.gtimg.cn/qyn"

            # 构建查询参数
            params = {
                "s": f"sh{stock_code}" if stock_code.startswith("6") else f"sz{stock_code}",
                "n": max_results
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            # 腾讯返回的是分号分隔的JSON数据
            # 格式: v_news_sh600519="标题|url|时间|来源..."
            data = response.text

            results = []
            if data.startswith("v_news_"):
                # 提取JSON部分
                json_str = data[data.index('"') + 1:data.rindex('"')]

                # 解析数据（分号分隔）
                items = json_str.split(";")

                for item in items[:max_results]:
                    try:
                        parts = item.split("|")
                        if len(parts) >= 3:
                            title = parts[0]
                            url = parts[1]
                            time_str = parts[2]

                            # 解析时间
                            publish_date = None
                            try:
                                # 腾讯时间格式可能是: 05-09 14:30
                                if len(time_str) > 0:
                                    publish_date = datetime.strptime(
                                        f"2025-{time_str}",
                                        "%Y-%m-%d %H:%M"
                                    )
                            except ValueError:
                                pass

                            # 只保留最近N天的新闻
                            if publish_date and publish_date < datetime.now() - timedelta(days=days):
                                continue

                            result = SearchResult(
                                title=title,
                                content="",  # 腾讯API不提供内容摘要
                                url=url,
                                source="腾讯财经",
                                source_type=SourceType.MAINSTREAM,
                                content_type=ContentType.NEWS,
                                publish_date=publish_date,
                                stock_code=stock_code,
                                relevance_score=self._calculate_relevance(
                                    title,
                                    stock_code,
                                    stock_name
                                )
                            )
                            results.append(result)

                    except Exception as e:
                        logger.warning(f"解析单条新闻失败: {e}")

            return results

        except Exception as e:
            logger.error(f"腾讯财经API调用失败: {e}")
            raise

    def _calculate_relevance(
        self,
        title: str,
        stock_code: str,
        stock_name: str
    ) -> float:
        """计算新闻相关性"""
        score = 0.0
        title_upper = title.upper()

        # 股票代码匹配
        if stock_code in title_upper:
            score += 0.4

        # 股票名称匹配
        if stock_name in title:
            score += 0.6

        return min(score, 1.0)

    async def fetch_company_announcement(
        self,
        stock_code: str,
        stock_name: str,
        days: int = 7
    ) -> List[SearchResult]:
        """
        获取公司公告

        优先使用官方渠道

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 查询最近N天

        Returns:
            公告列表
        """
        # 使用东方财富的公告API
        return await self._fetch_from_eastmoney(
            stock_code,
            stock_name,
            days,
            max_results=20
        )
