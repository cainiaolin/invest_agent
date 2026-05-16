"""搜索策略数据模型测试"""
import pytest
from unittest.mock import patch
from app.models.search_strategy import SearchStrategy, AgentSearchConfig


class TestSearchStrategy:
    """测试SearchStrategy类"""

    def test_search_strategy_creation(self):
        """测试创建SearchStrategy实例"""
        strategy = SearchStrategy(
            search_basic_info=True,
            search_market_sentiment=True,
            search_industry=True,
            search_competitors=True,
            time_horizon=30,
            min_reliability=0.7,
            max_results_per_source=20
        )

        assert strategy.search_basic_info is True
        assert strategy.search_market_sentiment is True
        assert strategy.search_industry is True
        assert strategy.search_competitors is True
        assert strategy.time_horizon == 30
        assert strategy.min_reliability == 0.7
        assert strategy.max_results_per_source == 20

    def test_search_strategy_defaults(self):
        """测试SearchStrategy默认值"""
        strategy = SearchStrategy()

        assert strategy.search_basic_info is True
        assert strategy.search_market_sentiment is True
        assert strategy.search_industry is True
        assert strategy.search_competitors is True
        assert strategy.time_horizon == 7
        assert strategy.min_reliability == 0.6
        assert strategy.max_results_per_source == 10

    def test_search_strategy_validation(self):
        """测试SearchStrategy参数验证"""
        # 测试时间范围验证
        with pytest.raises(ValueError):
            SearchStrategy(time_horizon=0)  # 小于最小值

        with pytest.raises(ValueError):
            SearchStrategy(time_horizon=366)  # 大于最大值

        # 测试可信度验证
        with pytest.raises(ValueError):
            SearchStrategy(min_reliability=-0.1)  # 小于最小值

        with pytest.raises(ValueError):
            SearchStrategy(min_reliability=1.1)  # 大于最大值

        # 测试最大结果数验证
        with pytest.raises(ValueError):
            SearchStrategy(max_results_per_source=0)  # 小于最小值

        with pytest.raises(ValueError):
            SearchStrategy(max_results_per_source=101)  # 大于最大值


class TestAgentSearchConfig:
    """测试AgentSearchConfig类"""

    def test_agent_search_config_creation(self):
        """测试创建AgentSearchConfig实例"""
        strategy = SearchStrategy(
            search_basic_info=True,
            time_horizon=30
        )

        config = AgentSearchConfig(
            agent_name="buffet",
            strategy=strategy,
            llm_model="gpt-4o"
        )

        assert config.agent_name == "buffet"
        assert config.strategy is strategy
        assert config.llm_model == "gpt-4o"

    def test_agent_search_config_defaults(self):
        """测试AgentSearchConfig默认值"""
        strategy = SearchStrategy()
        config = AgentSearchConfig(
            agent_name="buffet",
            strategy=strategy
        )

        assert config.agent_name == "buffet"
        assert config.strategy is strategy
        assert config.llm_model == "gpt-4o"

    @patch.dict('os.environ', {
        'SEARCH_LLM_MODEL': 'claude-3-sonnet',
        'SEARCH_MIN_RELIABILITY': '0.8'
    })
    def test_agent_search_config_from_env(self):
        """测试从环境变量加载配置"""
        strategy = SearchStrategy()
        config = AgentSearchConfig.from_env("buffet", strategy)

        assert config.agent_name == "buffet"
        assert config.strategy is strategy
        assert config.llm_model == 'claude-3-sonnet'  # 从环境变量获取

    @patch.dict('os.environ', {})
    def test_agent_search_config_fallback(self):
        """测试配置降级"""
        strategy = SearchStrategy()
        config = AgentSearchConfig.from_env("buffet", strategy)

        assert config.agent_name == "buffet"
        assert config.strategy is strategy
        assert config.llm_model == "gpt-4o"  # 默认值

    def test_get_default_strategy_for_agent(self):
        """测试获取Agent的默认搜索策略"""
        # 测试Buffet策略
        buffet_strategy = AgentSearchConfig._get_default_strategy_for_agent("buffet")
        assert buffet_strategy.search_basic_info is True
        assert buffet_strategy.search_market_sentiment is False
        assert buffet_strategy.search_industry is True
        assert buffet_strategy.search_competitors is True
        assert buffet_strategy.time_horizon == 30
        assert buffet_strategy.min_reliability == 0.7

        # 测试Graham策略
        graham_strategy = AgentSearchConfig._get_default_strategy_for_agent("graham")
        assert graham_strategy.search_basic_info is True
        assert graham_strategy.search_market_sentiment is False
        assert graham_strategy.search_industry is False
        assert graham_strategy.search_competitors is False
        assert graham_strategy.time_horizon == 90
        assert graham_strategy.min_reliability == 0.8

        # 测试Fisher策略
        fisher_strategy = AgentSearchConfig._get_default_strategy_for_agent("fisher")
        assert fisher_strategy.search_basic_info is True
        assert fisher_strategy.search_market_sentiment is True
        assert fisher_strategy.search_industry is True
        assert fisher_strategy.search_competitors is True
        assert fisher_strategy.time_horizon == 60
        assert fisher_strategy.min_reliability == 0.6

        # 测试Lynch策略
        lynch_strategy = AgentSearchConfig._get_default_strategy_for_agent("lynch")
        assert lynch_strategy.search_basic_info is True
        assert lynch_strategy.search_market_sentiment is True
        assert lynch_strategy.search_industry is True
        assert lynch_strategy.search_competitors is False
        assert lynch_strategy.time_horizon == 14
        assert lynch_strategy.min_reliability == 0.6

        # 测试Soros策略
        soros_strategy = AgentSearchConfig._get_default_strategy_for_agent("soros")
        assert soros_strategy.search_basic_info is False
        assert soros_strategy.search_market_sentiment is True
        assert soros_strategy.search_industry is True
        assert soros_strategy.search_competitors is False
        assert soros_strategy.time_horizon == 7
        assert soros_strategy.min_reliability == 0.5

        # 测试Dalio策略
        dalio_strategy = AgentSearchConfig._get_default_strategy_for_agent("dalio")
        assert dalio_strategy.search_basic_info is True
        assert dalio_strategy.search_market_sentiment is True
        assert dalio_strategy.search_industry is True
        assert dalio_strategy.search_competitors is True
        assert dalio_strategy.time_horizon == 30
        assert dalio_strategy.min_reliability == 0.6

        # 测试未知的Agent策略（应该返回默认策略）
        unknown_strategy = AgentSearchConfig._get_default_strategy_for_agent("unknown")
        assert unknown_strategy.search_basic_info is True
        assert unknown_strategy.search_market_sentiment is True
        assert unknown_strategy.search_industry is True
        assert unknown_strategy.search_competitors is True
        assert unknown_strategy.time_horizon == 7
        assert unknown_strategy.min_reliability == 0.6