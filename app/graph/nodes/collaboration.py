"""协作节点：实现投票和辩论协作模式"""
from typing import Dict, List
from datetime import datetime
from app.core.state import AnalysisState, Decision, DebateMessage
from app.agents.base import BaseAgent
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.value.graham_agent import GrahamAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.macro.dalio_agent import DalioAgent


async def vote_collaboration_node(state: AnalysisState) -> AnalysisState:
    """
    投票协作模式：多数投票决策

    流程：
    1. 收集所有Agent的投票
    2. 统计buy/sell/hold的票数
    3. 多数决策
    4. 计算共识度

    Args:
        state: 当前状态

    Returns:
        更新后的状态（包含最终决策）
    """
    agent_analyses = state.get("agent_analyses", [])

    if not agent_analyses:
        state["error"] = "没有Agent分析结果可用于投票"
        return state

    # 收集投票
    votes = {"buy": 0, "sell": 0, "hold": 0}
    agent_votes = {}  # 记录每个Agent的投票

    for analysis in agent_analyses:
        action = analysis["action"]
        votes[action] += 1
        agent_votes[analysis["agent_name"]] = action

    # 多数决策
    total_votes = sum(votes.values())
    max_votes = max(votes.values())

    # 找出得票最多的行动
    winning_actions = [action for action, count in votes.items() if count == max_votes]

    if len(winning_actions) == 1:
        final_action = winning_actions[0]
    else:
        # 平票时优先级: hold > buy > sell
        if "hold" in winning_actions:
            final_action = "hold"
        elif "buy" in winning_actions:
            final_action = "buy"
        else:
            final_action = "sell"

    # 计算共识度 (多数票占比)
    consensus = max_votes / total_votes if total_votes > 0 else 0.0

    # 生成决策摘要
    summary = _generate_vote_summary(agent_votes, final_action, consensus)

    # 构造最终决策
    decision = Decision(
        action=final_action,
        consensus=consensus,
        participating_agents=list(agent_votes.keys()),
        summary=summary,
    )

    state["final_decision"] = decision

    return state


async def debate_collaboration_node(state: AnalysisState) -> AnalysisState:
    """
    辩论协作模式：3轮辩论后决策

    流程：
    1. 初始化辩论环境
    2. 进行3轮辩论
    3. 每轮Agent根据上下文发表观点
    4. 3轮后基于辩论质量做出决策

    Args:
        state: 当前状态

    Returns:
        更新后的状态（包含最终决策和辩论历史）
    """
    agent_analyses = state.get("agent_analyses", [])
    stock_data = state.get("stock_data", {})

    if not agent_analyses:
        state["error"] = "没有Agent分析结果可用于辩论"
        return state

    # 初始化辩论
    debate_history: List[DebateMessage] = []
    debate_round = state.get("debate_round", 0)

    # 创建Agent实例
    agents_map = {
        "Warren Buffett": BuffetAgent(),
        "Benjamin Graham": GrahamAgent(),
        "Philip Fisher": FisherAgent(),
        "Peter Lynch": LynchAgent(),
        "George Soros": SorosAgent(),
        "Ray Dalio": DalioAgent(),
    }

    # 进行3轮辩论
    for round_num in range(1, 4):  # 3轮
        debate_round = round_num

        # 构造辩论上下文
        debate_context = {
            "stock": stock_data,
            "round": round_num,
            "previous_messages": debate_history,
            "market_sentiment": _infer_market_sentiment(agent_analyses),
        }

        # 每个Agent参与辩论
        for analysis in agent_analyses:
            agent_name = analysis["agent_name"]
            agent = agents_map.get(agent_name)

            if not agent:
                continue

            try:
                # Agent发表观点
                opinion = agent.debate(debate_context)

                # 记录辩论消息
                message = DebateMessage(
                    agent_name=agent_name,
                    content=opinion,
                    round=round_num,
                    timestamp=datetime.now().isoformat(),
                )

                debate_history.append(message)

            except Exception as e:
                print(f"Agent {agent_name} 辩论失败: {str(e)}")
                continue

    # 基于辩论结果做出决策
    final_action = _make_decision_from_debate(agent_analyses, debate_history)

    # 计算共识度（基于辩论的一致性）
    consensus = _calculate_debate_consensus(debate_history)

    # 生成决策摘要
    summary = _generate_debate_summary(debate_history, final_action)

    # 构造最终决策
    decision = Decision(
        action=final_action,
        consensus=consensus,
        participating_agents=[a["agent_name"] for a in agent_analyses],
        summary=summary,
    )

    state["final_decision"] = decision
    state["debate_history"] = debate_history
    state["debate_round"] = debate_round

    return state


def _generate_vote_summary(agent_votes: Dict[str, str], final_action: str, consensus: float) -> str:
    """生成投票摘要"""
    summary_parts = []

    # 统计票数
    vote_counts = {"buy": 0, "sell": 0, "hold": 0}
    for vote in agent_votes.values():
        vote_counts[vote] += 1

    summary_parts.append(f"投票结果: buy({vote_counts['buy']}) sell({vote_counts['sell']}) hold({vote_counts['hold']})")

    # 最终决策
    action_names = {"buy": "买入", "sell": "卖出", "hold": "持有"}
    summary_parts.append(f"最终决策: {action_names[final_action]}")

    # 共识度
    summary_parts.append(f"共识度: {consensus:.1%}")

    # 投票详情
    summary_parts.append("投票详情:")
    for agent, vote in agent_votes.items():
        summary_parts.append(f"  - {agent}: {vote}")

    return "\n".join(summary_parts)


def _infer_market_sentiment(agent_analyses: List[Dict]) -> str:
    """推断市场情绪"""
    buy_count = sum(1 for a in agent_analyses if a["action"] == "buy")
    sell_count = sum(1 for a in agent_analyses if a["action"] == "sell")

    if buy_count > sell_count * 1.5:
        return "bullish"
    elif sell_count > buy_count * 1.5:
        return "bearish"
    else:
        return "neutral"


def _make_decision_from_debate(agent_analyses: List[Dict], debate_history: List[DebateMessage]) -> str:
    """基于辩论结果做出决策"""
    # 简化版：基于原始分析的加权投票
    # 在实际实现中，可以基于辩论内容进行更复杂的分析

    votes = {"buy": 0, "sell": 0, "hold": 0}

    for analysis in agent_analyses:
        action = analysis["action"]
        confidence = analysis.get("confidence", 0.5)

        # 置信度加权
        votes[action] += confidence

    # 找出最高分
    max_score = max(votes.values())
    for action, score in votes.items():
        if score == max_score:
            return action

    return "hold"


def _calculate_debate_consensus(debate_history: List[DebateMessage]) -> float:
    """计算辩论共识度"""
    # 简化版：基于辩论轮次的完整性
    # 实际实现可以分析观点的一致性

    if not debate_history:
        return 0.0

    # 如果进行了完整的3轮辩论，基础共识度为0.6
    # 每轮增加0.1
    max_round = max(msg["round"] for msg in debate_history)
    base_consensus = 0.6 + (max_round - 1) * 0.1

    return min(base_consensus, 1.0)


def _generate_debate_summary(debate_history: List[DebateMessage], final_action: str) -> str:
    """生成辩论摘要"""
    summary_parts = []

    summary_parts.append(f"辩论共进行{len(debate_history)}轮，{len(debate_history)}位Agent参与讨论。")

    # 按轮次总结
    current_round = 0
    for msg in debate_history:
        if msg["round"] != current_round:
            current_round = msg["round"]
            summary_parts.append(f"\n第{current_round}轮辩论:")

        summary_parts.append(f"  {msg['agent_name']}: {msg['content'][:100]}...")

    # 最终决策
    action_names = {"buy": "买入", "sell": "卖出", "hold": "持有"}
    summary_parts.append(f"\n经过辩论，最终决策: {action_names[final_action]}")

    return "\n".join(summary_parts)
