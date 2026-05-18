import logging
from fastapi import APIRouter

from backend.entity.request.SessionRequest import SessionRequest
from backend.entity.response.SessionResponse import SessionResponse
from backend.entity.Result import Result
from backend.service.SessionService import SessionService

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用APIRouter而不是FastAPI主应用，更适合模块化路由管理
session_router = APIRouter(prefix="/api/session", tags=["session"])

@session_router.get("/{session_id}", response_model=Result[SessionResponse])
async def get_session(session_id: int) -> Result[SessionResponse]:
    """
    通过sessionId获取对话历史
    :param session_id: 会话ID
    :return: 会话信息包装在Result中
    """
    try:
        # 参数验证
        if session_id <= 0:
            return Result.error(msg="会话ID必须为正整数", code=400)
        
        logger.info(f"获取会话请求，会话ID: {session_id}")
        
        # 调用服务获取会话信息
        session_response = SessionService.get_session_by_id(session_id)
        
        if session_response is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            return Result.error(msg=f"会话ID {session_id} 不存在", code=404)
        
        logger.info(f"获取会话成功，会话ID: {session_id}")
        return Result.success(data=session_response)
    
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"获取会话失败: {str(e)}")
        return Result.error(msg=f"获取会话失败: {str(e)}", code=500)

@session_router.post("/", response_model=Result[SessionResponse])
async def create_session(session_request: SessionRequest) -> Result[SessionResponse]:
    """
    新建对话会话，派发sessionId返回
    :param session_request: 会话创建请求
    :return: 创建的会话信息包装在Result中
    """
    try:
        # 参数验证
        user_id = session_request.get_user_id()
        if user_id <= 0:
            return Result.error(msg="用户ID必须为正整数", code=400)
        
        logger.info(f"创建会话请求，用户ID: {user_id}, 会话名称: {session_request.get_session_name()}")
        
        # 调用服务创建会话
        session_response = SessionService.create_session(session_request)
        
        if session_response is None:
            logger.error(f"创建会话失败，用户ID: {user_id}")
            return Result.error(msg="创建会话失败", code=500)
        
        logger.info(f"创建会话成功，会话ID: {session_response.get_session_id()}")
        return Result.success(data=session_response)
    
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        return Result.error(msg=f"创建会话失败: {str(e)}", code=500)

@session_router.delete("/{session_id}", response_model=Result[bool])
async def delete_session(session_id: int) -> Result[bool]:
    """
    通过sessionId删除对话历史
    :param session_id: 要删除的会话ID
    :return: 删除结果包装在Result中
    """
    try:
        # 参数验证
        if session_id <= 0:
            return Result.error(msg="会话ID必须为正整数", code=400)
        
        logger.info(f"删除会话请求，会话ID: {session_id}")
        
        # 调用服务删除会话
        success = SessionService.delete_session(session_id)
        
        if not success:
            logger.warning(f"删除会话失败或会话不存在，会话ID: {session_id}")
            return Result.error(msg=f"删除会话失败，会话ID {session_id} 可能不存在", code=404)
        
        logger.info(f"删除会话成功，会话ID: {session_id}")
        return Result.success(data=True)
    
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"删除会话失败: {str(e)}")
        return Result.error(msg=f"删除会话失败: {str(e)}", code=500)