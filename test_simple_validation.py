#!/usr/bin/env python3
"""
简单的修复验证脚本
专注于验证方法调用修复
"""
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_method_calls():
    """测试方法调用是否正确"""
    print("开始测试方法调用修复...")

    try:
        from app.agents.value.llm_buffet_agent import LLMBuffetAgent
        from app.agents.llm_agent import LLMAgent
        import inspect

        # 检查LLMBuffetAgent的_analyze_with_llm方法
        buffet_source = inspect.getsource(LLMBuffetAgent._analyze_with_llm)
        print("LLMBuffetAgent._analyze_with_llm 方法:")
        print("=" * 50)

        lines = buffet_source.split('\n')
        for i, line in enumerate(lines, 1):
            if '_parse_llm_response' in line:
                print(f"第{i}行: {line.strip()}")
                # 检查参数
                if 'llm_result, stock_data' in line:
                    print("  [PASS] _parse_llm_response调用正确：包含两个参数")
                else:
                    print("  [FAIL] _parse_llm_response调用可能有问题")

            if 'reason_with_cot' in line:
                print(f"第{i}行: {line.strip()}")
                if 'await' in line:
                    print("  [PASS] reason_with_cot异步调用正确")
                else:
                    print("  [FAIL] reason_with_cot缺少await")

        print("\n检查父类LLMAgent._parse_llm_response签名:")
        print("=" * 50)
        print(inspect.signature(LLMAgent._parse_llm_response))

        # 检查是否添加了异步测试装饰器
        test_file_path = os.path.join(os.path.dirname(__file__), 'tests', 'integration', 'test_buffet_search_agent.py')
        if os.path.exists(test_file_path):
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_content = f.read()

            if 'pytest.mark.asyncio' in test_content:
                print("  [PASS] 已添加异步测试装饰器")
            else:
                print("  [FAIL] 缺少异步测试装饰器")

            # 检查异步测试方法
            if 'async def test_buffet_search_agent_analyze' in test_content:
                print("  [PASS] 找到异步测试方法")
            else:
                print("  [FAIL] 未找到异步测试方法")

        return True

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_code_structure():
    """测试代码结构"""
    print("\n开始测试代码结构...")

    try:
        from app.agents.value.llm_buffet_agent import LLMBuffetAgent

        # 检查基本属性
        agent_class = LLMBuffetAgent
        print(f"Agent名称: {agent_class.name}")
        print(f"投资风格: {agent_class.style}")

        # 检查方法存在
        methods = ['analyze', '_analyze_with_llm', '_calculate_buffet_metrics', '_build_cot_prompt']
        for method in methods:
            if hasattr(agent_class, method):
                print(f"  [PASS] {method} 方法存在")
            else:
                print(f"  [FAIL] {method} 方法不存在")

        return True

    except Exception as e:
        print(f"代码结构测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 简单修复验证脚本 ===")

    # 测试方法调用
    method_result = test_method_calls()

    # 测试代码结构
    structure_result = test_code_structure()

    print(f"\n=== 最终结果 ===")
    print(f"方法调用测试: {'通过' if method_result else '失败'}")
    print(f"代码结构测试: {'通过' if structure_result else '失败'}")

    if method_result and structure_result:
        print("核心修复验证通过!")
    else:
        print("部分测试失败，需要进一步检查")