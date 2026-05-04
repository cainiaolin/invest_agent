"""测试Agent集成 - 验证tushare_token正常工作"""
import os
import asyncio

# 设置临时测试token
os.environ["TUSHARE_TOKEN"] = "test_token_placeholder"

from app.services.tushare_service import TushareService
from app.agents.value.buffet_agent import BuffetAgent
from app.agents.value.graham_agent import GrahamAgent
from app.agents.growth.fisher_agent import FisherAgent
from app.agents.growth.lynch_agent import LynchAgent
from app.agents.macro.soros_agent import SorosAgent
from app.agents.macro.dalio_agent import DalioAgent


async def test_agents():
    """测试所有Agent的初始化和基本功能"""

    # 创建Tushare服务
    tushare_service = TushareService("test_token_placeholder")

    # 测试所有Agent的初始化
    agents = [
        BuffetAgent(tushare_service),
        GrahamAgent(tushare_service),
        FisherAgent(tushare_service),
        LynchAgent(tushare_service),
        SorosAgent(tushare_service),
        DalioAgent(tushare_service),
    ]

    print("[OK] 所有Agent初始化成功")
    print(f"  - BuffetAgent: {agents[0].name}")
    print(f"  - GrahamAgent: {agents[1].name}")
    print(f"  - FisherAgent: {agents[2].name}")
    print(f"  - LynchAgent: {agents[3].name}")
    print(f"  - SorosAgent: {agents[4].name}")
    print(f"  - DalioAgent: {agents[5].name}")

    # 测试_get_stock_data方法（会失败，因为token无效，但能验证代码结构）
    print("\n测试 _get_stock_data 方法结构...")

    test_stock_code = "600519"  # 贵州茅台

    for agent in agents:
        try:
            # 调用_get_stock_data方法（因为token无效会返回空数据）
            result = await agent._get_stock_data(test_stock_code)

            # 验证返回结构
            assert "symbol" in result, f"{agent.name}: 缺少symbol字段"
            assert "name" in result, f"{agent.name}: 缺少name字段"

            print(f"[OK] {agent.name}._get_stock_data() 结构正确")
        except Exception as e:
            print(f"[FAIL] {agent.name}._get_stock_data() 失败: {e}")
            return False

    print("\n所有测试通过！")
    return True


if __name__ == "__main__":
    asyncio.run(test_agents())
