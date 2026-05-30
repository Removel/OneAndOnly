from typing import List, Dict, Any
import logging

from agent.main import chat_with_agent, get_conversation_history, clear_conversation_history
from backend.repository.SessionRepository import SessionRepository
from backend.exception.Exceptions import ParamValidationException, NotFoundException, ChatException
from backend.entity.response.ChatHistoryResponse import ChatHistoryResponse

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.session_repository = SessionRepository()
        logger.debug("ChatService初始化完成")

    def chat(self, human_input: str, session_id: int, clear_history: bool = False) -> Dict[str, Any]:
        """
        执行聊天操作
        :param human_input: 用户输入文本
        :param session_id: 会话ID
        :param clear_history: 是否清空历史记录
        :return: 聊天响应字典
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        :raises ChatException: 聊天操作失败
        """
        logger.info(f"执行聊天操作，会话ID: {session_id}, 清除历史: {clear_history}, 输入长度: {len(human_input)}")
        
        if not human_input or human_input.strip() == "":
            logger.warning("参数验证失败，输入文本不能为空")
            raise ParamValidationException(msg="输入文本不能为空")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            logger.debug(f"调用智能体进行对话，thread_id: {thread_id}")
            
            result = chat_with_agent(
                user_input=human_input,
                session_id=thread_id,
                clear_history=clear_history
            )
            
            if not result.get("success", False):
                error_msg = result.get("response_text", "聊天操作失败")
                logger.error(f"智能体对话失败，会话ID: {session_id}, 错误: {error_msg}")
                raise ChatException(msg=error_msg)
            
            logger.info(f"聊天操作成功，会话ID: {session_id}, 重试次数: {result.get('retry_times', 0)}")
            return result
        except ChatException:
            raise
        except Exception as e:
            logger.error(f"聊天操作异常，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
            raise ChatException(msg=f"聊天操作失败: {str(e)}")

    def get_conversation_history(self, session_id: int) -> ChatHistoryResponse:
        """
        获取会话的对话历史
        :param session_id: 会话ID
        :return: 对话历史响应对象
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        logger.info(f"获取对话历史，会话ID: {session_id}")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            logger.debug(f"查询对话历史，thread_id: {thread_id}")
            
            history = get_conversation_history(thread_id)
            
            history_dict = []
            for message in history:
                message_dict = {
                    "type": message.__class__.__name__,
                    "content": message.content,
                    "id": getattr(message, 'id', None)
                }
                if hasattr(message, 'additional_kwargs'):
                    message_dict["additional_kwargs"] = message.additional_kwargs
                if hasattr(message, 'response_metadata'):
                    message_dict["response_metadata"] = message.response_metadata
                history_dict.append(message_dict)
            
            response = ChatHistoryResponse.from_data(session_id, history_dict)
            logger.info(f"获取对话历史成功，会话ID: {session_id}, 消息数量: {len(history_dict)}")
            return response
        except Exception as e:
            logger.error(f"获取对话历史异常，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
            raise ChatException(msg=f"获取对话历史失败: {str(e)}")

    def clear_conversation_history(self, session_id: int):
        """
        清空会话的对话历史
        :param session_id: 会话ID
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        :raises ChatException: 清空历史失败
        """
        logger.info(f"清空对话历史，会话ID: {session_id}")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            logger.debug(f"清空对话历史，thread_id: {thread_id}")
            
            clear_conversation_history(thread_id)
            
            logger.info(f"清空对话历史成功，会话ID: {session_id}")
        except Exception as e:
            logger.error(f"清空对话历史异常，会话ID: {session_id}, 错误: {str(e)}", exc_info=True)
            raise ChatException(msg=f"清空对话历史失败: {str(e)}")