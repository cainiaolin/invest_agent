"""输出节点：格式化最终输出"""
from typing import Dict, Any
from app.core.state import AnalysisState


async def output_node(state: AnalysisState) -> AnalysisState:
    """
    输出节点：格式化并返回最终结果

    格式化内容包括：
    1. 股票基本信息
    2. 各Agent的分析摘要
    3. 协作过程（投票/辩论）
    4. 最终决策和建议

    Args:
        state: 当前状态

    Returns:
        更新后的状态（包含格式化输出）
    """
    stock_code = state.get("stock_code", "")
    mode = state.get("mode", "parallel")
    agent_analyses = state.get("agent_analyses", [])
    final_decision = state.get("final_decision")
    debate_history = state.get("debate_history", [])

    # 构造格式化输出
    formatted_output = _format_output(
        stock_code=stock_code,
        mode=mode,
        agent_analyses=agent_analyses,
        final_decision=final_decision,
        debate_history=debate_history,
        error=state.get("error"),
    )

    state["formatted_output"] = formatted_output

    return state


def _format_output(
    stock_code: str,
    mode: str,
    agent_analyses: list,
    final_decision: dict,
    debate_history: list,
    error: str = None,
) -> str:
    """格式化输出内容"""
    output_parts = []

    # 标题
    output_parts.append("=" * 80)
    output_parts.append(f"投资分析报告 - {stock_code}")
    output_parts.append(f"协作模式: {mode}")
    output_parts.append("=" * 80)
    output_parts.append("")

    # Agent分析摘要
    output_parts.append("【Agent分析摘要】")
    if agent_analyses:
        for i, analysis in enumerate(agent_analyses, 1):
            agent_name = analysis.get("agent_name", "Unknown")
            action = analysis.get("action", "hold")
            confidence = analysis.get("confidence", 0.0)
            reasoning = analysis.get("reasoning", "")

            output_parts.append(f"{i}. {agent_name}")
            output_parts.append(f"   建议: {action} (置信度: {confidence:.1%})")
            output_parts.append(f"   理由: {reasoning[:100]}...")

            # 关键因素
            key_metrics = analysis.get("key_metrics", {})
            if key_metrics:
                scores = key_metrics.get("scores", {})
                if scores:
                    top_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
                    factors_str = ", ".join([f"{k}={v:.0f}" for k, v in top_factors])
                    output_parts.append(f"   关键因素: {factors_str}")

            output_parts.append("")
    else:
        output_parts.append("无Agent分析结果")

    output_parts.append("")

    # 协作过程
    if mode == "vote" and final_decision:
        output_parts.append("【投票协作】")
        output_parts.append(final_decision.get("summary", ""))
        output_parts.append("")

    elif mode == "debate" and debate_history:
        output_parts.append("【辩论协作】")
        output_parts.append(f"辩论轮次: {len(set(msg['round'] for msg in debate_history))}")
        output_parts.append("")

        # 显示最后一轮辩论
        last_round = max(msg["round"] for msg in debate_history)
        output_parts.append(f"第{last_round}轮观点:")
        for msg in debate_history:
            if msg["round"] == last_round:
                output_parts.append(f"  {msg['agent_name']}: {msg['content'][:150]}...")
        output_parts.append("")

    # 最终决策
    if final_decision:
        output_parts.append("=" * 80)
        output_parts.append("【最终决策】")

        action = final_decision.get("action", "hold")
        consensus = final_decision.get("consensus", 0.0)
        summary = final_decision.get("summary", "")

        action_names = {"buy": "买入", "sell": "卖出", "hold": "持有"}
        output_parts.append(f"投资建议: {action_names.get(action, action)}")
        output_parts.append(f"共识度: {consensus:.1%}")

        if summary:
            output_parts.append(f"决策摘要: {summary}")

        output_parts.append("=" * 80)

    # 错误信息
    if error:
        output_parts.append("")
        output_parts.append(f"【错误信息】")
        output_parts.append(error)

    return "\n".join(output_parts)
