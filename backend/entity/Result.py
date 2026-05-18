from typing import TypeVar, Optional, Generic

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self,code:int = 0,msg:str="",data:Optional[T] = None):
        self.code = code
        self.msg = msg
        self.data = data

    @classmethod
    def success(cls,data:Optional[T] = None)->'Result[T]':
        """
        创建成功实例
        """
        return cls(code=200,msg="success",data=data)

    @classmethod
    def error(cls,msg: str ,code: int ,data:Optional[T] = None)->'Result[T]':
        """
        创建失败实例
        """
        return cls(code=code,msg=msg,data=data)

    @classmethod
    def custom(cls,code: int ,msg: str ,data:Optional[T] = None)->'Result[T]':
        """
        创建自定义实例
        """
        return cls(code=code,msg=msg,data=data)

    def is_error(self) -> bool:
        """判断是否错误，通常认为code不为200时为错误"""
        return self.code != 200

    def __str__(self) -> str:
        return f"Result(code={self.code}, msg='{self.msg}', data={self.data})"

    def __repr__(self) -> str:
        return f"Result(code={self.code}, msg='{self.msg}', data={self.data})"
