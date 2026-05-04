"""Graph模块初始化"""
# 延迟导入以避免在没有langgraph时导入失败

def create_investment_workflow():
    """创建投资分析工作流"""
    from app.graph.workflow import create_investment_workflow as _create_workflow
    return _create_workflow()

__all__ = ["create_investment_workflow"]
