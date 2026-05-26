from typing import TypeVar, Optional, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    code: int = Field(default=0, description="响应状态码")
    msg: str = Field(default="", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, data: Optional[T] = None) -> 'Result[T]':
        """
        创建成功实例
        """
        return cls(code=200, msg="success", data=data)

    @classmethod
    def error(cls, msg: str, code: int, data: Optional[T] = None) -> 'Result[T]':
        """
        创建失败实例
        """
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def custom(cls, code: int, msg: str, data: Optional[T] = None) -> 'Result[T]':
        """
        创建自定义实例
        """
        return cls(code=code, msg=msg, data=data)

    def is_error(self) -> bool:
        """判断是否错误，通常认为code不为200时为错误"""
        return self.code != 200

    class Config:
        arbitrary_types_allowed = True