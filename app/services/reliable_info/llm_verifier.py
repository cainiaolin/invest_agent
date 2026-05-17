"""LLM信息验证器

使用支持联网的LLM模型验证和补充信息
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.search import SearchResult, SearchSummary, ReliabilityScore, SourceType, ContentType


logger = logging.getLogger(__name__)


class LLMInfoVerifier:
    """
    LLM信息验证器

    使用支持联网的LLM模型进行：
    1. 信息验证 - 验证已获取信息的准确性
    2. 信息补充 - 补充缺失的关键信息
    3. 交叉验证 - 与多个来源进行对比
    """

    # 支持联网的LLM模型列表
    SUPPORTED_LLMS = [
        "claude-3-5-sonnet-20241022",  # Claude with computer use
        "claude-3-7-sonnet-20250219",   # Claude 3.7 Sonnet
        "gpt-4-turbo-browsing",         # GPT-4 with browsing
        "gpt-4o",                       # GPT-4o (部分支持联网)
    ]

    def __init__(self, llm_service):
        """
        初始化验证器

        Args:
            llm_service: LLM服务实例
        """
        self.llm_service = llm_service
        self.model = llm_service.config.get("model", "")

    def is_network_enabled(self) -> bool:
        """检查当前LLM是否支持联网"""
        # 检查模型是否在支持列表中
        return any(model in self.model.lower() for model in self.SUPPORTED_LLMS)

    async def verify_and_enhance(
        self,
        stock_code: str,
        stock_name: str,
        existing_results: List[SearchResult],
        days: int = 7
    ) -> List[SearchResult]:
        """
        验证和增强已获取的信息

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            existing_results: 已获取的搜索结果
            days: 查询最近N天

        Returns:
            验证和增强后的结果列表
        """
        if not self.is_network_enabled():
            logger.info(f"当前LLM模型 {self.model} 不支持联网，跳过LLM验证")
            return existing_results

        logger.info(f"使用LLM {self.model} 验证和增强信息")

        try:
            # 构建验证Prompt
            verify_prompt = self._build_verify_prompt(
                stock_code,
                stock_name,
                existing_results,
                days
            )

            # 调用LLM进行验证和补充
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的金融信息验证专家，擅长识别虚假信息和补充关键信息。"
                },
                {"role": "user", "content": verify_prompt}
            ]

            response = await self.llm_service._call_llm(messages)

            # 解析LLM响应
            enhanced_results = self._parse_llm_response(
                response,
                stock_code,
                existing_results
            )

            logger.info(f"LLM验证完成，返回 {len(enhanced_results)} 条结果")
            return enhanced_results

        except Exception as e:
            logger.warning(f"LLM验证失败: {e}")
            return existing_results

    def _build_verify_prompt(
        self,
        stock_code: str,
        stock_name: str,
        existing_results: List[SearchResult],
        days: int
    ) -> str:
        """构建验证Prompt"""
        # 格式化已有信息
        existing_info = ""
        if existing_results:
            existing_info = "\n".join([
                f"- {r.title} (来源: {r.source}, 日期: {r.publish_date})"
                for r in existing_results[:5]
            ])
        else:
            existing_info = "暂无信息"

        return f"""请使用联网搜索功能，验证和补充关于"{stock_name}({stock_code})"在最近{days}天的重要信息。

## 已有信息
{existing_info}

## 任务
1. **验证已有信息的准确性**：检查上述信息是否真实可靠
2. **补充关键信息**：搜索并补充以下类型的重要信息：
   - 公司公告（财报、重组、分红等）
   - 重大新闻（并购、合作、诉讼等）
   - 行业动态（政策变化、行业趋势等）
   - 市场事件（停牌、复牌、异常波动等）

## 要求
1. 只使用可靠来源（官方公告、主流财经媒体）
2. 标注每条信息的发布时间和来源
3. 对已有信息进行准确性验证（准确/存疑/错误）
4. 返回JSON格式，包含验证结果和补充信息

## 返回格式
```json
{{
  "verification": {{
    "existing_accurate": ["已有的准确信息标题列表"],
    "existing_questionable": ["存疑的信息标题列表"],
    "existing_false": ["错误的信息标题列表"]
  }},
  "supplemented": [
    {{
      "title": "补充信息标题",
      "content": "内容摘要（100字以内）",
      "url": "来源链接",
      "source": "来源网站",
      "publish_date": "YYYY-MM-DD",
      "type": "announcement/news/industry",
      "importance": "high/medium/low"
    }}
  ]
}}
```

请开始验证和补充。
"""

    def _parse_llm_response(
        self,
        response: str,
        stock_code: str,
        existing_results: List[SearchResult]
    ) -> List[SearchResult]:
        """解析LLM响应"""
        import json

        try:
            data = json.loads(response)

            # 保留准确的信息
            accurate_titles = set(
                data.get("verification", {}).get("existing_accurate", [])
            )
            results = [
                r for r in existing_results
                if r.title in accurate_titles
            ]

            # 添加补充的信息
            for item in data.get("supplemented", []):
                try:
                    # 解析发布日期
                    publish_date = None
                    date_str = item.get("publish_date", "")
                    if date_str:
                        try:
                            publish_date = datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            pass

                    # 解析内容类型
                    type_str = item.get("type", "news")
                    if type_str == "announcement":
                        content_type = ContentType.ANNOUNCEMENT
                    elif type_str == "news":
                        content_type = ContentType.NEWS
                    else:
                        content_type = ContentType.OTHER

                    result = SearchResult(
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        url=item.get("url", ""),
                        source=item.get("source", "LLM验证"),
                        source_type=SourceType.MAINSTREAM,
                        content_type=content_type,
                        publish_date=publish_date,
                        stock_code=stock_code,
                        relevance_score=0.8  # LLM补充的信息相关性较高
                    )
                    results.append(result)

                except Exception as e:
                    logger.warning(f"解析单条补充信息失败: {e}")

            return results

        except json.JSONDecodeError as e:
            logger.error(f"解析LLM响应失败: {e}")
            return existing_results
