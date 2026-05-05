import pytest
from app.services.knowledge_service import KnowledgeService


@pytest.mark.asyncio
async def test_load_nonexistent_knowledge():
    """测试加载不存在的知识文件"""
    service = KnowledgeService("knowledge")

    with pytest.raises(FileNotFoundError):
        await service.load_knowledge("nonexistent")


def test_extract_section():
    """测试章节提取"""
    service = KnowledgeService()
    content = """
## 核心投资哲学

这是核心哲学内容。

## 其他章节

其他内容。
"""
    result = service._extract_section(content, "核心投资哲学")
    assert "这是核心哲学内容" in result
    assert "其他章节" not in result
