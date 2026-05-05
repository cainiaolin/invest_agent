"""数据质量检查工具"""

from typing import Dict, Any, List, Optional
import logging
from app.services.exceptions import InvalidDataError, MissingCriticalDataError

logger = logging.getLogger(__name__)


class DataValidator:
    """
    数据质量验证器

    功能：
    - 验证必需字段是否存在
    - 检查数据值的合理性
    - 标记缺失或无效的数据
    """

    # Agent关键数据要求
    AGENT_DATA_REQUIREMENTS = {
        "buffet": {
            "required": ["roe", "debt_ratio", "current_ratio", "profit_margin"],
            "optional": ["pe_ratio", "pb_ratio", "revenue_growth"],
            "reason": "巴菲特投资需要评估企业质量和护城河"
        },
        "graham": {
            "required": ["eps", "bvps", "pe_ratio", "debt_ratio", "current_ratio"],
            "optional": ["pb_ratio", "net_margin", "revenue_growth"],
            "reason": "格雷厄姆需要计算内在价值和安全边际"
        },
        "fisher": {
            "required": ["revenue_growth", "profit_growth", "gross_margin", "operating_margin"],
            "optional": ["rd_ratio", "roe", "debt_ratio"],
            "reason": "费雪关注成长质量和研发投入"
        },
        "lynch": {
            "required": ["pe_ratio", "revenue_growth", "profit_growth"],
            "optional": ["pb_ratio", "roe", "debt_ratio"],
            "reason": "林奇PEG比率需要PE和增长率"
        },
        "dalio": {
            "required": ["debt_ratio", "current_ratio"],
            "optional": ["roe", "profit_margin", "revenue_growth"],
            "reason": "达利欧关注债务周期"
        },
        "soros": {
            "required": ["revenue_growth", "profit_growth"],
            "optional": ["pe_ratio", "pb_ratio", "debt_ratio"],
            "reason": "索罗斯关注反身性和趋势"
        }
    }

    @staticmethod
    def validate_stock_data(
        stock_data: Dict[str, Any],
        agent_name: str,
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """
        验证股票数据质量

        Args:
            stock_data: 股票数据字典
            agent_name: Agent名称
            strict_mode: 严格模式（缺少必需字段时抛出异常）

        Returns:
            验证结果字典，包含is_valid、missing_fields、invalid_fields等

        Raises:
            MissingCriticalDataError: 缺少关键数据
            InvalidDataError: 数据无效
        """
        metrics = stock_data.get("metrics", {})

        # 获取Agent的数据要求
        agent_key = agent_name.lower().replace(" ", "").replace("(ai)", "").replace("(", "").replace(")", "")
        requirements = DataValidator.AGENT_DATA_REQUIREMENTS.get(
            agent_key,
            {"required": [], "optional": [], "reason": "通用投资分析"}
        )

        required_fields = requirements["required"]
        optional_fields = requirements["optional"]

        # 检查必需字段
        missing_fields = []
        for field in required_fields:
            value = metrics.get(field)
            if value is None or value == 0:
                missing_fields.append(field)

        # 检查可选字段（记录但不阻止）
        missing_optional = []
        for field in optional_fields:
            value = metrics.get(field)
            if value is None or value == 0:
                missing_optional.append(field)

        # 严格模式：缺少必需字段时抛出异常
        if strict_mode and missing_fields:
            raise MissingCriticalDataError(
                missing_fields=missing_fields,
                stock_code=stock_data.get("symbol", ""),
                agent_name=agent_name
            )

        # 验证数据值的合理性
        invalid_fields = []
        warnings = []

        for field, value in metrics.items():
            if value is None:
                continue

            # 检查数值类型的合理性
            if isinstance(value, (int, float)):
                # PE比率：通常在0-1000之间
                if field == "pe_ratio" and (value < 0 or value > 1000):
                    invalid_fields.append(f"{field}={value} (PE比率异常)")
                    warnings.append(f"PE比率{value:.2f}超出正常范围")

                # PB比率：通常在0-100之间
                if field == "pb_ratio" and (value < 0 or value > 100):
                    invalid_fields.append(f"{field}={value} (PB比率异常)")
                    warnings.append(f"PB比率{value:.2f}超出正常范围")

                # ROE：通常在-100%到100%之间
                if field == "roe" and (value < -100 or value > 100):
                    invalid_fields.append(f"{field}={value} (ROE异常)")
                    warnings.append(f"ROE{value:.2f}%超出正常范围")

                # 负债率：通常在0%到100%之间
                if field == "debt_ratio" and (value < 0 or value > 100):
                    invalid_fields.append(f"{field}={value} (负债率异常)")
                    warnings.append(f"负债率{value:.2f}%超出正常范围")

                # 流动比率：通常大于0
                if field == "current_ratio" and value < 0:
                    invalid_fields.append(f"{field}={value} (流动比率不能为负)")

                # 增长率：通常在-100%到1000%之间
                if "growth" in field and (value < -100 or value > 1000):
                    warnings.append(f"{field}{value:.2f}%增长率异常")

        # 构建验证结果
        validation_result = {
            "is_valid": len(missing_fields) == 0 and len(invalid_fields) == 0,
            "missing_required": missing_fields,
            "missing_optional": missing_optional,
            "invalid_fields": invalid_fields,
            "warnings": warnings,
            "data_quality_score": DataValidator._calculate_quality_score(
                len(required_fields),
                len(missing_fields),
                len(optional_fields),
                len(missing_optional),
                len(invalid_fields)
            )
        }

        # 记录验证日志
        if not validation_result["is_valid"]:
            logger.warning(
                f"数据验证失败 - Agent: {agent_name}, "
                f"缺失必需: {missing_fields}, "
                f"无效字段: {invalid_fields}"
            )

        return validation_result

    @staticmethod
    def _calculate_quality_score(
        total_required: int,
        missing_required: int,
        total_optional: int,
        missing_optional: int,
        invalid_count: int
    ) -> float:
        """
        计算数据质量评分（0-100）

        Args:
            total_required: 必需字段总数
            missing_required: 缺失的必需字段数
            total_optional: 可选字段总数
            missing_optional: 缺失的可选字段数
            invalid_count: 无效字段数

        Returns:
            质量评分
        """
        if total_required == 0:
            return 100.0

        # 必需字段权重：70%
        required_score = (total_required - missing_required) / total_required * 70

        # 可选字段权重：20%
        optional_score = 0
        if total_optional > 0:
            optional_score = (total_optional - missing_optional) / total_optional * 20

        # 有效性权重：10%
        validity_score = max(0, 10 - invalid_count * 2)

        total_score = required_score + optional_score + validity_score
        return round(total_score, 2)

    @staticmethod
    def get_data_summary(stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取数据摘要信息

        Args:
            stock_data: 股票数据字典

        Returns:
            数据摘要
        """
        metrics = stock_data.get("metrics", {})

        # 统计非零字段
        non_zero_fields = {k: v for k, v in metrics.items() if v not in [None, 0]}

        return {
            "symbol": stock_data.get("symbol", ""),
            "name": stock_data.get("name", ""),
            "total_fields": len(metrics),
            "non_zero_fields": len(non_zero_fields),
            "zero_fields": len(metrics) - len(non_zero_fields),
            "data_completeness": len(non_zero_fields) / len(metrics) * 100 if metrics else 0,
            "available_metrics": list(non_zero_fields.keys())
        }
