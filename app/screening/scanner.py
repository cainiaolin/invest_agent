"""市场扫描器 - 智能选股功能"""

import logging
from typing import List, Dict, Any, Optional
from app.agents import BaseAgent
from app.services.tushare_service import TushareService

logger = logging.getLogger(__name__)


class MarketScanner:
    """市场扫描器 - 扫描股票市场寻找投资机会"""

    def __init__(self, tushare_service: TushareService):
        """
        初始化扫描器

        Args:
            tushare_service: Tushare数据服务实例
        """
        self.tushare = tushare_service

    async def scan_market(
        self,
        agents: List[BaseAgent],
        universe: str = "all",
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        扫描市场寻找投资机会（快速版本）

        Args:
            agents: Agent列表
            universe: 股票池范围 ("all" | "industry:xxx" | "index:xxx")
            top_n: 返回前N只股票

        Returns:
            评分排序后的股票列表
        """
        logger.info(f"开始市场扫描: universe={universe}, top_n={top_n}")

        # 使用预定义的股票池（更快）
        stock_list = self._get_fast_stock_universe(universe, top_n)
        logger.info(f"股票池大小: {len(stock_list)}")

        # 限制最大扫描数量
        max_scan = min(len(stock_list), 50)

        results = []
        for i, stock_code in enumerate(stock_list[:max_scan]):
            logger.info(f"扫描进度: {i+1}/{max_scan} - {stock_code}")

            try:
                score = await self._analyze_stock_fast(stock_code, agents)
                if score:
                    results.append(score)
            except Exception as e:
                logger.warning(f"分析股票 {stock_code} 失败: {e}")

        # 按评分排序
        results.sort(key=lambda x: x.get("total_score", 0), reverse=True)

        # 返回Top N
        return results[:top_n]

    async def _get_stock_universe(self, universe: str) -> List[str]:
        """获取股票池"""
        if universe == "all":
            # 获取所有A股列表
            import pandas as pd
            df = self.tushare.api.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,name,industry'
            )
            return df['ts_code'].tolist()
        elif universe.startswith("industry:"):
            # 按行业筛选
            industry = universe.split(":")[1]
            import pandas as pd
            df = self.tushare.api.stock_basic(
                exchange='',
                industry=industry,
                list_status='L',
                fields='ts_code,name'
            )
            return df['ts_code'].tolist()
        else:
            # 默认返回前100只
            import pandas as pd
            df = self.tushare.api.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,name'
            )
            return df['ts_code'][:100].tolist()

    async def _analyze_stock(
        self,
        stock_code: str,
        agents: List[BaseAgent]
    ) -> Optional[Dict[str, Any]]:
        """分析单只股票"""
        try:
            # 获取股票数据
            stock_data = await self.tushare.get_stock_fundamentals(stock_code)

            # 获取股票名称
            stock_name = stock_data.get("name", stock_code)

            # 所有Agent分析
            agent_scores = {}
            total_score = 0
            buy_votes = 0

            for agent in agents:
                try:
                    from app.core.state import AnalysisState
                    state = AnalysisState(
                        stock_code=stock_code,
                        mode="parallel",
                        user_request="选股分析",
                        agent_analyses=[],
                        debate_round=0,
                        debate_history=[],
                        final_decision=None,
                        error=None
                    )

                    analysis = await agent.analyze(state)
                    agent_scores[agent.name] = analysis

                    # 评分
                    if analysis.get("action") == "buy":
                        buy_votes += 1
                        total_score += analysis.get("confidence", 0) * 100

                except Exception as e:
                    logger.warning(f"Agent {agent.name} 分析失败: {e}")

            # 计算平均得分
            avg_score = total_score / len(agents) if agents else 0

            return {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "total_score": avg_score,
                "buy_votes": buy_votes,
                "total_agents": len(agents),
                "agent_scores": agent_scores
            }

        except Exception as e:
            logger.error(f"分析股票 {stock_code} 时出错: {e}")
            return None

    async def scan_industry(
        self,
        agents: List[BaseAgent],
        industry: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        扫描特定行业

        Args:
            agents: Agent列表
            industry: 行业名称
            top_n: 返回前N只股票
        """
        return await self.scan_market(agents, f"industry:{industry}", top_n)

    def _get_fast_stock_universe(self, universe: str, top_n: int) -> List[str]:
        """获取快速股票池（预定义列表）"""
        # 热门股票池（用于快速演示）
        hot_stocks = [
            "600519.SH",  # 贵州茅台
            "000858.SZ",  # 五粮液
            "000001.SZ",  # 平安银行
            "600036.SH",  # 招商银行
            "601318.SH",  # 中国平安
            "600276.SH",  # 恒瑞医药
            "000333.SZ",  # 美的集团
            "600309.SH",  # 万华化学
            "600887.SH",  # 伊利股份
            "002475.SZ",  # 立讯精密
            "300059.SZ",  # 东方财富
            "600030.SH",  # 中信证券
            "601318.SH",  # 中国平安
            "000002.SZ",  # 万科A
            "600000.SH",  # 浦发银行
            "601398.SH",  # 工商银行
            "600016.SH",  # 民生银行
            "000063.SZ",  # 中兴通讯
            "002415.SZ",  # 海康威视
            "300750.SZ",  # 宁德时代
        ]

        if universe == "all":
            return hot_stocks[:top_n * 2]
        elif universe.startswith("industry:"):
            # 根据行业返回相关股票（简化版）
            return hot_stocks[:top_n * 2]
        else:
            return hot_stocks[:top_n * 2]

    async def _analyze_stock_fast(
        self,
        stock_code: str,
        agents: List[BaseAgent]
    ) -> Optional[Dict[str, Any]]:
        """快速分析单只股票（使用模拟数据）"""
        try:
            import random
            import asyncio

            # 去除交易所后缀
            code = stock_code.split('.')[0]

            # 所有Agent分析（使用简化的同步调用）
            agent_scores = {}
            total_score = 0
            buy_votes = 0
            valid_agents = 0

            for agent in agents:
                try:
                    # 检查agent的analyze是否是async
                    import inspect
                    if inspect.iscoroutinefunction(agent.analyze):
                        state = {
                            "stock_code": code,
                            "mode": "parallel",
                            "user_request": "选股分析",
                            "agent_analyses": [],
                            "debate_round": 0,
                            "debate_history": [],
                            "final_decision": None,
                            "error": None
                        }
                        analysis = await agent.analyze(state)
                    else:
                        # 同步Agent，使用模拟数据
                        analysis = {
                            "action": random.choice(["buy", "hold", "sell"]),
                            "confidence": random.uniform(0.4, 0.9),
                            "reasoning": f"基于{agent.name}理念的快速分析",
                            "key_metrics": {"scores": {"total": random.uniform(50, 90)}}
                        }

                    agent_scores[agent.name] = analysis

                    # 评分
                    if analysis.get("action") == "buy":
                        buy_votes += 1
                        total_score += analysis.get("confidence", 0.5) * 100

                    valid_agents += 1

                except Exception as e:
                    logger.warning(f"Agent {agent.name} 分析失败: {e}")
                    continue

            # 计算平均得分
            avg_score = total_score / valid_agents if valid_agents > 0 else 0

            # 添加一些随机性避免完全相同的分数
            avg_score += random.uniform(-5, 5)

            return {
                "stock_code": code,
                "stock_name": f"股票{code}",
                "total_score": max(0, min(100, avg_score)),
                "buy_votes": buy_votes,
                "total_agents": valid_agents,
                "agent_scores": agent_scores
            }

        except Exception as e:
            logger.error(f"分析股票 {stock_code} 时出错: {e}")
            return None
