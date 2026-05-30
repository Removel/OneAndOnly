import logging
from typing import List
import asyncio

from fastapi import APIRouter, Depends

from backend.entity.request.ChatRequest import ChatRequest
from backend.entity.response.ChatResponse import ChatResponse
from backend.entity.response.ChatHistoryResponse import ChatHistoryResponse
from backend.entity.Result import Result
from backend.service.ChatService import ChatService

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix="/api", tags=["chat"])


def get_chat_service():
    logger.debug("创建ChatService实例")
    return ChatService()


@chat_router.post("/chat", response_model=Result[ChatResponse])
async def chat(chat_request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> Result[ChatResponse]:
    """
    处理用户输入，调用智能体进行对话
    :param chat_request: 用户对话请求内容
    :param service: 聊天服务实例
    :return: 智能体的回复包装在Result中
    """
    logger.info(f"收到聊天请求，会话ID: {chat_request.session_id}, 清除历史: {chat_request.clear_history}, 用户输入长度: {len(chat_request.human_input)}")
    
    try:
        result_dict = await asyncio.to_thread(
            service.chat,
            human_input=chat_request.human_input,
            session_id=chat_request.session_id,
            clear_history=chat_request.clear_history
        )
        
        response = ChatResponse(
            response=result_dict.get("response_text", ""),
            emotion_vac=result_dict.get("emotion_vac", {}),
            retry_times=result_dict.get("retry_times", 0),
            error_message=result_dict.get("error_message"),
            success=result_dict.get("success", True)
        )
        
        logger.info(f"聊天响应成功，会话ID: {chat_request.session_id}, 成功: {response.success}, 重试次数: {response.retry_times}, 回复长度: {len(response.response)}")
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"聊天处理失败，会话ID: {chat_request.session_id}, 错误: {str(e)}", exc_info=True)
        raise


@chat_router.get("/session/{session_id}/history", response_model=Result[ChatHistoryResponse])
async def get_conversation_history(session_id: int, service: ChatService = Depends(get_chat_service)) -> Result[ChatHistoryResponse]:
    """
    获取会话的对话历史
    :param session_id: 会话ID
    :param service: 聊天服务实例
    :return: 对话历史响应对象包装在Result中
    """
    logger.info(f"获取对话历史请求，会话ID: {session_id}")
    
    try:
        history_response = await asyncio.to_thread(service.get_conversation_history, session_id)
        
        logger.info(f"获取对话历史成功，会话ID: {session_id}, 消息数量: {len(history_response.messages) if history_response.messages else 0}")
        return Result.success(data=history_response)
    except Exception as e:
        logger.error(f"获取对话历史失败，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
        raise


@chat_router.delete("/session/{session_id}/history", response_model=Result[bool])
async def clear_conversation_history(session_id: int, service: ChatService = Depends(get_chat_service)) -> Result[bool]:
    """
    清空会话的对话历史
    :param session_id: 会话ID
    :param service: 聊天服务实例
    :return: 清空结果包装在Result中
    """
    logger.info(f"清空对话历史请求，会话ID: {session_id}")
    
    try:
        await asyncio.to_thread(service.clear_conversation_history, session_id)
        
        logger.info(f"清空对话历史成功，会话ID: {session_id}")
        return Result.success(data=True)
    except Exception as e:
        logger.error(f"清空对话历史失败，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
        raise