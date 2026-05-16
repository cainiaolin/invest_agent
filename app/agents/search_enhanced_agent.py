"""搜索增强Agent基类"""
import logging
from abc import abstractmethod
from typing import Dict, Any, Optional
from app.agents.llm_agent import LLMAgent
from app.models.search_strategy import SearchStrategy
from app.agents.search.fusion import InformationFusion


logger = logging.getLogger(__name__)


class SearchEnhancedAgent(LLMAgent):
    """
    搜索增强Agent基类

    继承LLMAgent，集成搜索服务和信息融合能力，提供基于搜索结果的投资分析。
    """

    @abstractmethod
    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict, search_context: str = "") -> str:
        """
        构建思维链Prompt（子类实现）

        Args:
            stock_data: 股票数据
            knowledge: 大师知识
            search_context: 搜索上下文（可选）

        Returns:
            Prompt字符串
        """
        pass
    """
    搜索增强Agent基类

    继承LLMAgent，集成搜索服务和信息融合能力，提供基于搜索结果的投资分析。
    """

    def __init__(
        self,
        tushare_service,
        search_service,
        llm_service,
        knowledge_service,
        master_name: str,
        search_strategy: Optional[SearchStrategy] = None
    ):
        """
        初始化搜索增强Agent

        Args:
            tushare_service: Tushare数据服务
            search_service: 搜索服务
            llm_service: LLM服务
            knowledge_service: 知识服务
            master_name: 大师名称
            search_strategy: 搜索策略，如果未提供则使用默认策略
        """
        # 调用父类初始化
        super().__init__(
            tushare_service=tushare_service,
            llm_service=llm_service,
            knowledge_service=knowledge_service,
            master_name=master_name
        )

        # 保存搜索服务
        self.search_service = search_service

        # 设置搜索策略（使用默认策略或提供的策略）
        self.search_strategy = search_strategy if search_strategy is not None else self._default_strategy()

        # 创建信息融合器
        self.fusion = InformationFusion()

    def get_search_strategy(self) -> SearchStrategy:
        """
        获取当前搜索策略

        Returns:
            SearchStrategy: 当前搜索策略
        """
        return self.search_strategy

    def _default_strategy(self) -> SearchStrategy:
        """
        默认搜索策略

        Returns:
            SearchStrategy: 默认搜索策略
        """
        return SearchStrategy()

    def _get_search_context(self, stock_code: str, stock_data: Dict[str, Any]) -> str:
        """
        获取搜索上下文

        Args:
            stock_code: 股票代码
            stock_data: 股票数据

        Returns:
            str: 搜索上下文字符串，如果搜索服务不可用则返回空字符串
        """
        # 如果没有搜索服务，返回空字符串
        if not self.search_service:
            logger.warning("搜索服务不可用，跳过搜索上下文获取")
            return ""

        try:
            # 调用搜索服务获取搜索结果
            search_summary = self.search_service.search_stock_info(stock_code, stock_data)

            # 使用信息融合器生成LLM友好的上下文
            return self.fusion.format_for_llm(search_summary, stock_data)

        except Exception as e:
            logger.warning(f"获取搜索上下文失败: {type(e).__name__}: {e}")
            return ""

    def _analyze_with_search_enhancement(self, state: Dict[str, Any], stock_data: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用搜索增强进行分析

        Args:
            state: 分析状态
            stock_data: 股票数据
            knowledge: 知识数据

        Returns:
            Dict: 分析结果，包含搜索增强信息
        """
        # 获取搜索上下文
        search_context = self._get_search_context(state.get("stock_code", ""), stock_data)

        # 构建增强Prompt（添加搜索上下文）
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, search_context)

        # 进行LLM分析
        llm_result = self.llm.reason_with_cot(cot_prompt)

        # 解析LLM响应
        result = self._parse_llm_response(llm_result)

        # 更新结果，添加搜索增强信息
        result.update({
            "search_enhanced": True,
            "search_strategy": self.search_strategy
        })

        return result

    @abstractmethod
    def analyze_with_enhanced_context(self, state: Dict[str, Any], analysis_context: Dict[str, Any], search_summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        使用增强上下文进行抽象分析（子类必须实现）

        Args:
            state: 分析状态
            analysis_context: 分析上下文
            search_summary: 搜索摘要（可选）

        Returns:
            Dict: 分析结果
        """
        pass

    # 重写父类的analyze方法，添加搜索增强能力
    async def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM和搜索增强进行投资分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        stock_code = state.get("stock_code", "")

        try:
            logger.info(f"尝试使用LLM和搜索增强分析: {self.name}")

            # 获取股票数据
            stock_data = await self._get_enriched_stock_data(stock_code)

            # 获取知识数据
            knowledge = await self.knowledge.load_knowledge(self.master_name)

            # 使用搜索增强进行分析
            return await self._analyze_with_llm_and_search_enhancement(state, stock_data, knowledge)

        except Exception as e:
            logger.warning(f"LLM搜索增强分析失败: {type(e).__name__}: {e}，降级到规则引擎")
            return await self._fallback_to_rule_engine(state)

    def _analyze_with_llm_and_search_enhancement(self, state: Dict[str, Any], stock_data: Dict[str, Any], knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM和搜索增强进行分析

        Args:
            state: 分析状态
            stock_data: 股票数据
            knowledge: 知识数据

        Returns:
            分析结果
        """
        # 获取搜索上下文
        search_context = self._get_search_context(state.get("stock_code", ""), stock_data)

        # 构建增强Prompt
        cot_prompt = self._build_cot_prompt(stock_data, knowledge, search_context)

        # 进行LLM分析
        llm_result = self.llm.reason_with_cot(cot_prompt)

        # 解析LLM响应
        result = self._parse_llm_response(llm_result)

        # 更新结果，添加搜索增强信息
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm_search_enhanced",
            "llm_model": self.llm.config.get("model"),
            "search_enhanced": True,
            "search_strategy": self.search_strategy
        })

        return result