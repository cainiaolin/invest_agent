"""投资大师知识管理服务"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import frontmatter


class KnowledgeService:
    """
    投资大师知识管理服务

    功能：
    - 加载md知识文件
    - 解析frontmatter元数据
    - 提取特定章节内容
    - 内存缓存
    """

    def __init__(self, knowledge_base_path: str = "knowledge"):
        """
        初始化知识服务

        Args:
            knowledge_base_path: 知识库根路径
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def load_knowledge(self, master_name: str) -> Dict[str, Any]:
        """
        加载大师知识

        Args:
            master_name: 大师名称 (如 "graham")

        Returns:
            知识字典，包含：
            - metadata: 元数据
            - content: 完整内容
            - core_philosophy: 核心哲学
            - evaluation_dimensions: 评估维度
            - decision_rules: 决策规则
            - cases: 经典案例
            - checklist: 检查清单

        Raises:
            FileNotFoundError: 知识文件不存在
        """
        # 检查缓存
        if master_name in self._cache:
            return self._cache[master_name]

        # 构建文件路径
        summary_file = self.knowledge_base_path / master_name / f"{master_name.upper()}_AGENT_SUMMARY.md"

        if not summary_file.exists():
            raise FileNotFoundError(f"知识文件不存在: {summary_file}")

        # 读取并解析文件
        with open(summary_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        knowledge = {
            "metadata": dict(post.metadata),
            "content": post.content,
            "core_philosophy": self._extract_section(post.content, "核心投资哲学"),
            "evaluation_dimensions": self._extract_section(post.content, "核心评估维度"),
            "decision_rules": self._extract_section(post.content, "决策规则"),
            "cases": self._extract_section(post.content, "经典案例"),
            "checklist": self._extract_section(post.content, "分析检查清单"),
        }

        # 缓存
        self._cache[master_name] = knowledge

        return knowledge

    def _extract_section(self, content: str, section_title: str) -> str:
        """
        提取markdown中的特定章节

        Args:
            content: markdown内容
            section_title: 章节标题

        Returns:
            章节内容
        """
        lines = content.split('\n')
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if line.strip().startswith(f"## {section_title}"):
                start_idx = i + 1
            elif start_idx and line.strip().startswith("## ") and i > start_idx:
                end_idx = i
                break

        if start_idx is None:
            return ""

        section_lines = lines[start_idx:end_idx]
        return '\n'.join(section_lines).strip()

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
