from typing import Optional


class BaseBusinessException(Exception):
    """基础业务异常类"""
    def __init__(self, msg: str, code: int, cause: Optional[Exception] = None):
        self.msg = msg
        self.code = code
        self.cause = cause
        super().__init__(self.msg)


class DatabaseException(BaseBusinessException):
    """数据库操作异常"""
    def __init__(self, msg: str = "数据库操作失败", cause: Optional[Exception] = None):
        super().__init__(msg=msg, code=500, cause=cause)


class SessionException(BaseBusinessException):
    """会话相关异常"""
    def __init__(self, msg: str = "会话操作失败", code: int = 500, cause: Optional[Exception] = None):
        super().__init__(msg=msg, code=code, cause=cause)


class ChatException(BaseBusinessException):
    """聊天相关异常"""
    def __init__(self, msg: str = "聊天操作失败", code: int = 500, cause: Optional[Exception] = None):
        super().__init__(msg=msg, code=code, cause=cause)


class ResourceException(BaseBusinessException):
    """资源相关异常"""
    def __init__(self, resource: str, identifier: str = None, msg: str = None):
        if msg is None:
            if identifier:
                msg = f"{resource} with id '{identifier}' not found"
            else:
                msg = f"{resource} not found"
        super().__init__(msg=msg, code=404)


class ParamValidationException(BaseBusinessException):
    """参数验证异常"""
    def __init__(self, msg: str = "参数验证失败", code: int = 400):
        super().__init__(msg=msg, code=code)