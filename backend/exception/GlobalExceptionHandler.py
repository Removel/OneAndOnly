from fastapi import Request
from fastapi.responses import JSONResponse
from .Exceptions import BaseBusinessException
from backend.entity.Result import Result
import logging

logger = logging.getLogger(__name__)


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
        logger.error(f"业务异常 - 路径: {request.url.path}, 方法: {request.method}, 错误: {exc.msg}, 错误码: {exc.code}")
        result = Result.error(msg=exc.msg, code=exc.code)
        return JSONResponse(content=result.model_dump(), status_code=exc.code)

    @app.exception_handler(Exception)
    async def default_exception_handler(request: Request, exc: Exception):
        """
        默认异常处理器
        从异常中提取消息和错误码，返回标准化的失败结果
        """
        logger.error(f"系统异常 - 路径: {request.url.path}, 方法: {request.method}, 错误: {str(exc)}", exc_info=True)
        result = Result.error(msg=str(exc), code=500)
        return JSONResponse(content=result.model_dump(), status_code=500)

    return app