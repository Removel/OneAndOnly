import logging
from typing import List
import asyncio

from fastapi import APIRouter, Depends

from backend.entity.request.SessionRequest import SessionRequest
from backend.entity.response.SessionResponse import SessionResponse
from backend.entity.Result import Result
from backend.service.SessionService import SessionService

logger = logging.getLogger(__name__)

session_router = APIRouter(prefix="/api/session", tags=["session"])


def get_session_service():
    logger.debug("创建SessionService实例")
    return SessionService()


@session_router.get("/active", response_model=Result[List[SessionResponse]])
async def get_active_sessions(service: SessionService = Depends(get_session_service)) -> Result[List[SessionResponse]]:
    """
    获取所有活跃会话信息
    :param service: 会话服务实例
    :return: 所有会话信息包装在Result中
    """
    logger.info("获取所有活跃会话请求")
    
    try:
        session_entities = await asyncio.to_thread(service.get_active_sessions)
        response_list = [SessionResponse.from_entity(session) for session in session_entities]
        
        logger.info(f"获取活跃会话成功，共 {len(response_list)} 个活跃会话")
        return Result.success(data=response_list)
    except Exception as e:
        logger.error(f"获取活跃会话失败: {str(e)}", exc_info=True)
        raise


@session_router.get("/", response_model=Result[List[SessionResponse]])
async def get_all_sessions(service: SessionService = Depends(get_session_service)) -> Result[List[SessionResponse]]:
    """
    获取所有会话信息（包括所有状态）
    :param service: 会话服务实例
    :return: 所有会话信息包装在Result中
    """
    logger.info("获取所有会话请求")
    
    try:
        session_entities = await asyncio.to_thread(service.get_all_sessions)
        response_list = [SessionResponse.from_entity(session) for session in session_entities]
        
        logger.info(f"获取所有会话成功，共 {len(response_list)} 个会话")
        return Result.success(data=response_list)
    except Exception as e:
        logger.error(f"获取所有会话失败: {str(e)}", exc_info=True)
        raise


@session_router.get("/{session_id}", response_model=Result[SessionResponse])
async def get_session(session_id: int, service: SessionService = Depends(get_session_service)) -> Result[SessionResponse]:
    """
    通过sessionId获取对话历史
    :param session_id: 会话ID
    :param service: 会话服务实例
    :return: 会话信息包装在Result中
    """
    logger.info(f"获取会话请求，会话ID: {session_id}")
    
    try:
        session_entity = await asyncio.to_thread(service.get_session_by_session_id, session_id)
        response = SessionResponse.from_entity(session_entity)
        
        logger.info(f"获取会话成功，会话ID: {session_id}, 状态: {session_entity.status}")
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"获取会话失败，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
        raise


@session_router.post("/", response_model=Result[SessionResponse])
async def create_session(service: SessionService = Depends(get_session_service)) -> Result[SessionResponse]:
    """
    新建对话会话
    :param service: 会话服务实例
    :return: 创建的会话信息包装在Result中
    """
    logger.info("创建会话请求")
    
    try:
        session_entity = await asyncio.to_thread(service.create_session)
        response = SessionResponse.from_entity(session_entity)
        
        logger.info(f"创建会话成功，会话ID: {session_entity.id}, 状态: {session_entity.status}")
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"创建会话失败: {str(e)}", exc_info=True)
        raise


@session_router.delete("/{session_id}", response_model=Result[bool])
async def delete_session(session_id: int, service: SessionService = Depends(get_session_service)) -> Result[bool]:
    """
    通过sessionId删除对话历史
    :param session_id: 会话ID
    :param service: 会话服务实例
    :return: 删除结果包装在Result中
    """
    logger.info(f"删除会话请求，会话ID: {session_id}")
    
    try:
        await asyncio.to_thread(service.delete_session, session_id)
        
        logger.info(f"删除会话成功，会话ID: {session_id}")
        return Result.success(data=True)
    except Exception as e:
        logger.error(f"删除会话失败，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
        raise


@session_router.put("/{session_id}", response_model=Result[SessionResponse])
async def update_session(session_id: int, session_request: SessionRequest, service: SessionService = Depends(get_session_service)) -> Result[SessionResponse]:
    """
    更新通过sessionId的会话状态
    :param session_id: 会话ID
    :param session_request: 会话请求包含会话ID和状态
    :param service: 会话服务实例
    :return: 更新后的会话信息包装在Result中
    """
    session_data = session_request.to_dict()
    logger.info(f"更新会话状态，会话ID: {session_id}, 更新数据: {session_data}")

    try:
        updated_session_entity = await asyncio.to_thread(service.update_session, session_id, session_data)
        response = SessionResponse.from_entity(updated_session_entity)

        logger.info(f"更新会话状态成功，会话ID: {session_id}, 新状态: {updated_session_entity.status}")
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"更新会话状态失败，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
        raise