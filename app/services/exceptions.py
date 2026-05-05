"""数据服务异常定义"""

from typing import Optional, Dict, Any


class DataServiceError(Exception):
    """数据服务基础异常类"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化异常

        Args:
            message: 错误消息
            details: 错误详情（包含接口名、股票代码等）
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class TushareAPIError(DataServiceError):
    """Tushare API调用失败异常"""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        stock_code: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        初始化API异常

        Args:
            message: 错误消息
            api_name: 调用的API接口名
            stock_code: 股票代码
            original_error: 原始异常
        """
        details = {}
        if api_name:
            details["api"] = api_name
        if stock_code:
            details["stock_code"] = stock_code
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message, details)
        self.api_name = api_name
        self.stock_code = stock_code
        self.original_error = original_error


class TusharePermissionError(TushareAPIError):
    """Tushare权限不足异常（积分不够）"""

    def __init__(
        self,
        api_name: str,
        required_points: int,
        current_points: int,
        stock_code: Optional[str] = None
    ):
        """
        初始化权限异常

        Args:
            api_name: 需要的API接口名
            required_points: 需要的积分
            current_points: 当前积分
            stock_code: 股票代码
        """
        message = f"权限不足：{api_name}需要{required_points}积分，当前{current_points}积分"
        super().__init__(message, api_name, stock_code)
        self.required_points = required_points
        self.current_points = current_points


class TushareDataNotFoundError(TushareAPIError):
    """Tushare数据不存在异常"""

    def __init__(
        self,
        api_name: str,
        stock_code: str,
        reason: Optional[str] = None
    ):
        """
        初始化数据不存在异常

        Args:
            api_name: API接口名
            stock_code: 股票代码
            reason: 数据不存在的原因（如：股票代码错误、未上市等）
        """
        message = f"数据不存在：{api_name}未找到股票{stock_code}的数据"
        if reason:
            message += f"（{reason}）"
        super().__init__(message, api_name, stock_code)
        self.reason = reason


class MissingCriticalDataError(DataServiceError):
    """缺少关键数据异常"""

    def __init__(
        self,
        missing_fields: list,
        stock_code: Optional[str] = None,
        agent_name: Optional[str] = None
    ):
        """
        初始化关键数据缺失异常

        Args:
            missing_fields: 缺失的关键字段列表
            stock_code: 股票代码
            agent_name: Agent名称
        """
        message = f"缺少关键数据：{', '.join(missing_fields)}"
        details = {}
        if stock_code:
            details["stock_code"] = stock_code
        if agent_name:
            details["agent"] = agent_name
        details["missing_fields"] = missing_fields

        super().__init__(message, details)
        self.missing_fields = missing_fields
        self.stock_code = stock_code
        self.agent_name = agent_name


class InvalidDataError(DataServiceError):
    """数据无效异常"""

    def __init__(
        self,
        field_name: str,
        value: Any,
        reason: str,
        stock_code: Optional[str] = None
    ):
        """
        初始化数据无效异常

        Args:
            field_name: 字段名
            value: 无效的值
            reason: 无效的原因
            stock_code: 股票代码
        """
        message = f"数据无效：{field_name}={value} ({reason})"
        details = {"field": field_name, "value": str(value), "reason": reason}
        if stock_code:
            details["stock_code"] = stock_code

        super().__init__(message, details)
        self.field_name = field_name
        self.value = value
        self.reason = reason
