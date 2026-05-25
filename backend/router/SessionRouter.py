import logging
from typing import List

from fastapi import APIRouter, Depends

from backend.entity.request.SessionRequest import SessionRequest
from backend.entity.response.SessionResponse import SessionResponse
from backend.entity.Result import Result
from backend.service.SessionService import SessionService

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用APIRouter而不是FastAPI主应用，更适合模块化路由管理
session_router = APIRouter(prefix="/api/session", tags=["session"])

def get_session_service():
    return SessionService()

@session_router.get("/{session_id}", response_model=Result[SessionResponse])
async def get_session(session_id: int, service: SessionService = Depends(get_session_service)) -> Result[SessionResponse]:
    """
    通过sessionId获取对话历史
    :param session_id: 会话ID
    :param service: 会话服务实例
    :return: 会话信息包装在Result中
    """
    try:
        # 参数验证
        if session_id <= 0:
            return Result.error(msg="会话ID必须为正整数", code=400)
        
        logger.info(f"获取会话请求，会话ID: {session_id}")
        
        # 调用服务获取会话信息
        query_session = service.get_session_by_session_id(session_id)

        if query_session is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            return Result.error(msg=f"会话ID {session_id} 不存在", code=404)
        
        logger.info(f"获取会话成功，会话ID: {session_id}")
        return Result.success(data=query_session)
    
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"获取会话失败: {str(e)}")
        return Result.error(msg=f"获取会话失败: {str(e)}", code=500)

@session_router.get("/", response_model=Result[List[SessionResponse]])
async def get_active_sessions(service: SessionService = Depends(get_session_service)) -> Result[List[SessionResponse]]:
    """
    获取所有会话信息
    :param service: 会话服务实例
    :return: 所有会话信息包装在Result中
    """
    logger.info(f"获取所有会话请求")
    result = service.get_active_sessions()
    if not result:
        response = [SessionResponse(session=session) for session in result]
    elif result is not None:
        response = []
        logger.warning(f"活跃会话为空")
    else:
        logger.error(f"获取活跃会话失败")
        return Result.error(msg="获取活跃会话失败", code=500)
    return Result.success(data=response)



@session_router.post("/", response_model=Result[int])
async def create_session(service: SessionService = Depends(get_session_service)) -> Result[int]:
    """
    新建对话会话，派发sessionId返回
    :param service: 会话服务实例
    :return: 创建的会话ID包装在Result中
    """
    try:
        # 调用服务创建会话
        session_id = service.create_session()

        if session_id is None:
            logger.error(f"创建会话失败")
            return Result.error(msg="创建会话失败", code=500)
        
        logger.info(f"创建会话成功，会话ID: {session_id}")
        return Result.success(data=session_id)
    
    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}")
        return Result.error(msg=f"创建会话失败: {str(e)}", code=500)

@session_router.delete("/{session_id}", response_model=Result[bool])
async def delete_session(session_request: SessionRequest, service: SessionService = Depends(get_session_service)) -> Result[bool]:
    """
    通过sessionId删除对话历史
    :param session_request: 会话请求包含会话ID
    :param service: 会话服务实例
    :return: 删除结果包装在Result中
    """
    session_id = session_request.session_id
    try:
        # 参数验证
        if session_id <= 0:
            return Result.error(msg="会话ID必须为正整数", code=400)
        
        logger.info(f"删除会话请求，会话ID: {session_id}")
        
        # 调用服务删除会话
        success = service.delete_session(session_id)
        
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

@session_router.put("/{session_id}", response_model=Result[bool])
async def update_session(session_request: SessionRequest, service: SessionService = Depends(get_session_service)) -> Result[bool]:
    """
    更新通过sessionId的会话状态
    :param session_request: 会话请求包含会话ID和状态
    :param service: 会话服务实例
    :return: 更新后的会话信息包装在Result中
    """
    session_data = session_request.to_dict()
    session_id = session_data.get("session_id")
    status = session_data.get("status")
    try:
        if session_id <= 0:
            return Result.error(msg="会话ID必须为正整数", code=400)

        if status is None:
            return Result.error(msg="状态不能为空", code=400)

        logger.info(f"更新会话状态，会话ID: {session_id}, 状态: {status}")

        # 调用服务更新会话状态
        updated_session = service.update_session(session_id,session_data)

        if updated_session is False:
            logger.error(f"更新会话状态失败，会话ID: {session_id}")
            return Result.error(msg=f"更新会话状态失败，会话ID {session_id} 可能不存在", code=404)

        logger.info(f"更新会话状态成功，会话ID: {session_id}, 状态: {status}")
        return Result.success(data=updated_session)

    except ValueError as ve:
        logger.error(f"参数错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"更新会话状态失败: {str(e)}")
        return Result.error(msg=f"更新会话状态失败: {str(e)}", code=500)