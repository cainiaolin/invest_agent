"""验证工作流代码结构"""
import sys
import os
from pathlib import Path

# 设置UTF-8编码
if os.name == 'nt':  # Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_file_structure():
    """检查文件结构"""
    print("检查文件结构...")

    required_files = [
        "app/graph/__init__.py",
        "app/graph/workflow.py",
        "app/graph/nodes/__init__.py",
        "app/graph/nodes/router.py",
        "app/graph/nodes/agents.py",
        "app/graph/nodes/collaboration.py",
        "app/graph/nodes/output.py",
        "app/graph/edges/__init__.py",
        "app/graph/edges/conditions.py",
        "tests/unit/graph/test_workflow.py",
        "tests/integration/test_collaboration.py",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  [OK] {file_path}")

    if missing_files:
        print(f"\n缺少文件: {missing_files}")
        return False

    print("\n所有必需文件都已创建!")
    return True


def check_imports():
    """检查导入"""
    print("\n检查导入...")

    try:
        # 检查基础导入
        from app.core.state import AnalysisState, AgentAnalysis, Decision, DebateMessage
        print("  [OK] 状态定义导入成功")

        from app.agents.base import BaseAgent
        from app.agents.value.buffet_agent import BuffetAgent
        from app.agents.value.graham_agent import GrahamAgent
        from app.agents.growth.fisher_agent import FisherAgent
        from app.agents.growth.lynch_agent import LynchAgent
        from app.agents.macro.soros_agent import SorosAgent
        from app.agents.macro.dalio_agent import DalioAgent
        print("  [OK] 所有Agent导入成功")

        from app.graph.nodes.router import router_node
        from app.graph.nodes.agents import (
            parallel_agents_node,
            value_agent_node,
            growth_agent_node,
            macro_agent_node,
        )
        from app.graph.nodes.collaboration import vote_collaboration_node, debate_collaboration_node
        from app.graph.nodes.output import output_node
        print("  [OK] 所有节点导入成功")

        from app.graph.edges.conditions import route_to_agents, route_after_agents
        print("  [OK] 条件边函数导入成功")

        print("\n所有导入成功!")
        return True

    except Exception as e:
        print(f"\n导入失败: {e}")
        return False


def check_workflow_structure():
    """检查工作流结构"""
    print("\n检查工作流结构...")

    try:
        from app.graph.workflow import create_investment_workflow

        # 创建工作流（不执行）
        print("  [OK] 工作流创建函数存在")

        # 检查工作流组件
        from app.graph.nodes import (
            router_node,
            parallel_agents_node,
            value_agent_node,
            growth_agent_node,
            macro_agent_node,
            vote_collaboration_node,
            debate_collaboration_node,
            output_node,
        )
        print("  [OK] 所有节点函数已定义")

        from app.graph.edges import route_to_agents, route_after_agents
        print("  [OK] 所有路由函数已定义")

        print("\n工作流结构验证完成!")
        return True

    except Exception as e:
        print(f"\n工作流结构检查失败: {e}")
        return False


def check_agent_functionality():
    """检查Agent功能"""
    print("\n检查Agent功能...")

    try:
        from app.agents.value.buffet_agent import BuffetAgent
        from app.agents.growth.fisher_agent import FisherAgent
        from app.agents.macro.soros_agent import SorosAgent

        # 创建Agent实例
        buffet = BuffetAgent()
        fisher = FisherAgent()
        soros = SorosAgent()

        # 检查Agent属性
        assert hasattr(buffet, 'name')
        assert hasattr(buffet, 'style')
        assert hasattr(buffet, 'analyze')
        assert hasattr(buffet, 'vote')
        assert hasattr(buffet, 'debate')
        print("  [OK] Buffett Agent功能完整")

        assert hasattr(fisher, 'name')
        assert hasattr(fisher, 'style')
        assert hasattr(fisher, 'analyze')
        assert hasattr(fisher, 'vote')
        assert hasattr(fisher, 'debate')
        print("  [OK] Fisher Agent功能完整")

        assert hasattr(soros, 'name')
        assert hasattr(soros, 'style')
        assert hasattr(soros, 'analyze')
        assert hasattr(soros, 'vote')
        assert hasattr(soros, 'debate')
        print("  [OK] Soros Agent功能完整")

        print("\nAgent功能验证完成!")
        return True

    except Exception as e:
        print(f"\nAgent功能检查失败: {e}")
        return False


def check_collaboration_modes():
    """检查协作模式"""
    print("\n检查协作模式...")

    try:
        from app.graph.nodes.collaboration import (
            vote_collaboration_node,
            debate_collaboration_node,
            _generate_vote_summary,
            _generate_debate_summary,
        )

        # 检查协作节点
        assert callable(vote_collaboration_node)
        assert callable(debate_collaboration_node)
        print("  [OK] 投票协作节点存在")
        print("  [OK] 辩论协作节点存在")

        # 检查辅助函数
        assert callable(_generate_vote_summary)
        assert callable(_generate_debate_summary)
        print("  [OK] 协作辅助函数存在")

        print("\n协作模式验证完成!")
        return True

    except Exception as e:
        print(f"\n协作模式检查失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("LangGraph工作流代码验证")
    print("=" * 80)

    checks = [
        ("文件结构", check_file_structure),
        ("导入检查", check_imports),
        ("工作流结构", check_workflow_structure),
        ("Agent功能", check_agent_functionality),
        ("协作模式", check_collaboration_modes),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n{name}检查异常: {e}")
            results[name] = False

    # 总结
    print("\n" + "=" * 80)
    print("验证结果汇总")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n[SUCCESS] 所有验证通过!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 项验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
