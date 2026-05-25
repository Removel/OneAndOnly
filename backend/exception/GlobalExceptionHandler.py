from fastapi import Request
from fastapi.responses import JSONResponse
from .Exceptions import BaseBusinessException
from backend.entity.Result import Result


def register_exception_handlers(app):
    """
    注册全局异常处理器
    :param app: FastAPI 应用实例
    """
    
    @app.exception_handler(BaseBusinessException)
    async def base_business_exception_handler(request: Request, exc: BaseBusinessException):
        """
        基础业务异常处理器
        从异常中提取消息和错误码，返回标准化的失败结果
        """
        return Result.error(msg=exc.msg, code=exc.code)
    
    return app