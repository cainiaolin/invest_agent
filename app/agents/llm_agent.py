"""LLM Agent抽象基类"""

import logging
from abc import abstractmethod
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.core.state import AnalysisState
from app.services.exceptions import (
    TushareAPIError,
    TushareDataNotFoundError,
    MissingCriticalDataError,
    TusharePermissionError
)
from app.services.data_validator import DataValidator


logger = logging.getLogger(__name__)


class LLMAgent(BaseAgent):
    """
    基于LLM的智能投资Agent基类

    特点：
    - 使用思维链(Chain-of-Thought)推理
    - 结合知识图谱和实时数据
    - 支持多LLM模型配置
    - 自动降级到规则引擎
    """

    def __init__(
        self,
        tushare_service,
        llm_service: LLMService,
        knowledge_service: KnowledgeService,
        master_name: str
    ):
        """
        初始化LLM Agent

        Args:
            tushare_service: Tushare数据服务
            llm_service: LLM服务
            knowledge_service: 知识服务
            master_name: 大师名称
        """
        super().__init__(tushare_service)
        self.llm = llm_service
        self.knowledge = knowledge_service
        self._master_name = master_name

    @property
    def master_name(self) -> str:
        """大师名称"""
        return self._master_name

    async def analyze(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行投资分析

        Args:
            state: 分析状态

        Returns:
            分析结果字典
        """
        stock_code = state.get("stock_code", "")

        try:
            logger.info(f"尝试使用LLM分析: {self.name}, LLM配置: provider={self.llm.config.get('provider')}, model={self.llm.config.get('model')}")
            return await self._analyze_with_llm(state)
        except (TusharePermissionError, TushareDataNotFoundError, MissingCriticalDataError) as e:
            logger.warning(f"数据获取失败: {type(e).__name__}: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"数据获取失败：{str(e)}",
                "error_type": type(e).__name__,
                "agent_name": self.name,
                "analysis_mode": "data_error",
                "llm_model": None
            }
        except TushareAPIError as e:
            logger.error(f"Tushare API错误: {e}")
            return {
                "action": "hold",
                "confidence": 0.0,
                "reasoning": f"数据获取失败：{e.message}",
                "error_type": "api_error",
                "agent_name": self.name,
                "analysis_mode": "data_error",
                "llm_model": None
            }
        except Exception as e:
            logger.warning(f"LLM分析失败: {type(e).__name__}: {e}，降级到规则引擎", exc_info=True)
            result = await self._fallback_to_rule_engine(state)
            # 确保降级结果也包含必要字段
            result.setdefault("analysis_mode", "rule_fallback")
            result.setdefault("llm_model", None)
            result.setdefault("thought_process", None)
            return result

    async def _analyze_with_llm(self, state: AnalysisState) -> Dict[str, Any]:
        """
        使用LLM进行分析（子类实现具体逻辑）

        Args:
            state: 分析状态

        Returns:
            分析结果

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
            MissingCriticalDataError: 关键数据缺失
        """
        stock_code = state.get("stock_code", "")
        stock_data = await self._get_enriched_stock_data(stock_code)
        knowledge = await self.knowledge.load_knowledge(self.master_name)

        cot_prompt = self._build_cot_prompt(stock_data, knowledge)
        llm_result = await self.llm.reason_with_cot(cot_prompt)

        result = self._parse_llm_response(llm_result, stock_data)
        result.update({
            "agent_name": self.name,
            "analysis_mode": "ai_llm",
            "llm_model": self.llm.config.get("model")
        })

        return result

    @abstractmethod
    def _build_cot_prompt(self, stock_data: Dict, knowledge: Dict) -> str:
        """
        构建思维链Prompt（子类实现）

        Args:
            stock_data: 股票数据
            knowledge: 大师知识

        Returns:
            Prompt字符串
        """
        pass

    def _parse_llm_response(self, llm_result: Dict, stock_data: Dict) -> Dict[str, Any]:
        """
        解析LLM响应

        Args:
            llm_result: LLM返回结果
            stock_data: 股票数据

        Returns:
            标准化的分析结果
        """
        return {
            "action": llm_result.get("action", "hold"),
            "confidence": llm_result.get("confidence", 0.5),
            "reasoning": llm_result.get("reasoning", ""),
            "key_metrics": llm_result.get("key_metrics", {}),
            "thought_process": llm_result.get("thought_process", {}),
            "key_factors": llm_result.get("key_factors", [])
        }

    async def _get_enriched_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取增强的股票数据

        Args:
            stock_code: 股票代码

        Returns:
            包含股票数据的字典

        Raises:
            TushareAPIError: API调用失败
            TushareDataNotFoundError: 数据不存在
            MissingCriticalDataError: 关键数据缺失
        """
        # 复用现有Agent的数据获取方法（使用新的验证版本）
        from app.agents.value.graham_agent import GrahamAgent
        temp_agent = GrahamAgent(self.tushare)
        return await temp_agent._get_validated_stock_data(stock_code)

    async def _fallback_to_rule_engine(self, state: AnalysisState) -> Dict[str, Any]:
        """
        降级到规则引擎

        Args:
            state: 分析状态

        Returns:
            规则引擎分析结果
        """
        from app.agents import RULE_AGENTS

        rule_agent_class = RULE_AGENTS.get(self.master_name)
        if not rule_agent_class:
            raise ValueError(f"没有找到对应的规则Agent: {self.master_name}")

        rule_agent = rule_agent_class(self.tushare)
        result = await rule_agent.analyze(state)

        # 确保返回结果包含AI模式的标识字段
        result.setdefault("agent_name", f"{self.name} (规则引擎降级)")
        result.setdefault("analysis_mode", "rule_fallback")
        result.setdefault("fallback_reason", "LLM服务不可用")
        result.setdefault("llm_model", None)
        result.setdefault("thought_process", None)

        return result
