"""测试 BaseAgent 抽象类"""
import pytest
from abc import ABC

from app.agents.base import BaseAgent


class TestBaseAgent:
    """测试BaseAgent抽象类"""

    def test_base_agent_is_abstract(self):
        """测试BaseAgent无法直接实例化"""
        with pytest.raises(TypeError):
            BaseAgent()

    def test_base_agent_requires_abstract_methods(self):
        """测试子类必须实现抽象方法"""
        # 缺少analyze方法
        with pytest.raises(TypeError):

            class IncompleteAgent(BaseAgent):
                @property
                def name(self) -> str:
                    return "Incomplete"

                @property
                def style(self) -> str:
                    return "incomplete"

            IncompleteAgent()

        # 缺少vote方法
        with pytest.raises(TypeError):

            class IncompleteAgent2(BaseAgent):
                @property
                def name(self) -> str:
                    return "Incomplete"

                @property
                def style(self) -> str:
                    return "incomplete"

                def analyze(self, stock_data: dict) -> dict:
                    return {}

            IncompleteAgent2()

    def test_concrete_agent_implementation(self):
        """测试具体实现可以正常工作"""

        class ConcreteAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "Concrete Agent"

            @property
            def style(self) -> str:
                return "concrete"

            def analyze(self, stock_data: dict) -> dict:
                return {"decision": "hold", "confidence": 0.5}

            def vote(self, analysis: dict) -> str:
                return "hold"

            def debate(self, context: dict) -> str:
                return "I think we should hold"

        agent = ConcreteAgent()

        # 测试属性
        assert agent.name == "Concrete Agent"
        assert agent.style == "concrete"

        # 测试方法
        stock_data = {"symbol": "600000", "price": 10.0}
        analysis = agent.analyze(stock_data)
        assert analysis["decision"] == "hold"
        assert analysis["confidence"] == 0.5

        vote = agent.vote(analysis)
        assert vote == "hold"

        debate = agent.debate({"context": "test"})
        assert debate == "I think we should hold"

    def test_base_agent_is_abc(self):
        """测试BaseAgent继承自ABC"""
        assert issubclass(BaseAgent, ABC)
