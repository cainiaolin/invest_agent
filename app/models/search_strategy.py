"""搜索策略数据模型"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class SearchStrategy(BaseModel):
    """搜索策略数据模型"""

    search_basic_info: bool = Field(default=True, description="是否搜索基本面信息")
    search_market_sentiment: bool = Field(default=True, description="是否搜索市场情绪")
    search_industry: bool = Field(default=True, description="是否搜索行业信息")
    search_competitors: bool = Field(default=True, description="是否搜索竞争对手信息")
    time_horizon: int = Field(default=7, ge=1, le=365, description="搜索时间范围（天）")
    min_reliability: float = Field(default=0.6, ge=0.0, le=1.0, description="最低可信度阈值")
    max_results_per_source: int = Field(default=10, ge=1, le=100, description="每个源的最大结果数")

    

class AgentSearchConfig(BaseModel):
    """Agent搜索配置数据模型"""

    agent_name: str = Field(description="Agent名称")
    strategy: SearchStrategy = Field(description="搜索策略")
    llm_model: str = Field(default="gpt-4o", description="LLM模型")

    @classmethod
    def from_env(cls, agent_name: str, strategy: Optional[SearchStrategy] = None) -> 'AgentSearchConfig':
        """从环境变量加载配置"""
        # 从环境变量获取LLM模型配置
        llm_model = os.getenv('SEARCH_LLM_MODEL', 'gpt-4o')

        # 如果策略没有提供，使用默认策略
        if strategy is None:
            strategy = cls._get_default_strategy_for_agent(agent_name)

        return cls(
            agent_name=agent_name,
            strategy=strategy,
            llm_model=llm_model
        )

    @classmethod
    def _get_default_strategy_for_agent(cls, agent_name: str) -> SearchStrategy:
        """获取Agent的默认搜索策略"""

        agent_strategies = {
            "buffet": {
                "search_basic_info": True,
                "search_market_sentiment": False,
                "search_industry": True,
                "search_competitors": True,
                "time_horizon": 30,
                "min_reliability": 0.7,
                "max_results_per_source": 10
            },
            "graham": {
                "search_basic_info": True,
                "search_market_sentiment": False,
                "search_industry": False,
                "search_competitors": False,
                "time_horizon": 90,
                "min_reliability": 0.8,
                "max_results_per_source": 10
            },
            "fisher": {
                "search_basic_info": True,
                "search_market_sentiment": True,
                "search_industry": True,
                "search_competitors": True,
                "time_horizon": 60,
                "min_reliability": 0.6,
                "max_results_per_source": 10
            },
            "lynch": {
                "search_basic_info": True,
                "search_market_sentiment": True,
                "search_industry": True,
                "search_competitors": False,
                "time_horizon": 14,
                "min_reliability": 0.6,
                "max_results_per_source": 10
            },
            "soros": {
                "search_basic_info": False,
                "search_market_sentiment": True,
                "search_industry": True,
                "search_competitors": False,
                "time_horizon": 7,
                "min_reliability": 0.5,
                "max_results_per_source": 10
            },
            "dalio": {
                "search_basic_info": True,
                "search_market_sentiment": True,
                "search_industry": True,
                "search_competitors": True,
                "time_horizon": 30,
                "min_reliability": 0.6,
                "max_results_per_source": 10
            }
        }

        # 获取指定Agent的策略，如果没有则返回默认策略
        strategy_config = agent_strategies.get(agent_name, {
            "search_basic_info": True,
            "search_market_sentiment": True,
            "search_industry": True,
            "search_competitors": True,
            "time_horizon": 7,
            "min_reliability": 0.6,
            "max_results_per_source": 10
        })

        return SearchStrategy(**strategy_config)