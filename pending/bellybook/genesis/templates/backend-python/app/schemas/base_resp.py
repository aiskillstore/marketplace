"""
[INPUT]: 依赖 pydantic 的 BaseModel，依赖 app/utils/log 的 logger
[OUTPUT]: 对外提供 BaseResp 统一响应模型
[POS]: 响应模型基类，所有 API 响应的标准格式
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar

from app.utils.log import logger


T = TypeVar('T')


# ============================================================================
#  BaseResp - 统一响应模型
# ============================================================================

class BaseResp(BaseModel, Generic[T]):
    """统一响应模型

    所有 API 响应的基础模型，提供统一的响应格式。
    支持泛型，可指定 data 字段的具体类型。
    """
    code: int = Field(200, description="状态码，200表示成功，其他值表示错误")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    extra: Optional[dict[str, Any]] = Field(None, description="额外数据")

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = "success",
        extra: Optional[dict[str, Any]] = None
    ) -> "BaseResp":
        """成功响应

        Args:
            data: 响应数据
            message: 响应消息
            extra: 额外数据

        Returns:
            BaseResp: 成功响应对象
        """
        return cls(message=message, data=data, extra=extra)

    @classmethod
    def error(
        cls,
        code: int = 400,
        message: str = "error",
        extra: Optional[dict[str, Any]] = None
    ) -> "BaseResp":
        """错误响应

        Args:
            code: 错误状态码
            message: 错误消息
            extra: 额外数据

        Returns:
            BaseResp: 错误响应对象
        """
        logger.error(f"错误响应: {message}")
        return cls(code=code, message=message, data=None, extra=extra)
