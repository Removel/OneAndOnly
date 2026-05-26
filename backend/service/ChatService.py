from typing import List, Dict, Any

from agent.main import chat_with_agent, get_conversation_history, clear_conversation_history
from backend.repository.SessionRepository import SessionRepository
from backend.exception.Exceptions import ParamValidationException, NotFoundException, ChatException


class ChatService:
    def __init__(self):
        self.session_repository = SessionRepository()

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
        if not human_input or human_input.strip() == "":
            raise ParamValidationException(msg="输入文本不能为空")
        
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            result = chat_with_agent(
                user_input=human_input,
                session_id=thread_id,
                clear_history=clear_history
            )
            
            if not result.get("success", False):
                raise ChatException(msg=result.get("response_text", "聊天操作失败"))
            
            return result
        except ChatException:
            raise
        except Exception as e:
            raise ChatException(msg=f"聊天操作失败: {str(e)}")

    def get_conversation_history(self, session_id: int) -> List[Dict[str, Any]]:
        """
        获取会话的对话历史
        :param session_id: 会话ID
        :return: 对话历史列表
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            history = get_conversation_history(thread_id)
            
            # 将消息对象转换为字典
            history_dict = []
            for message in history:
                message_dict = {
                    "type": message.__class__.__name__,
                    "content": message.content,
                    "id": getattr(message, 'id', None)
                }
                # 添加其他可能的属性
                if hasattr(message, 'additional_kwargs'):
                    message_dict["additional_kwargs"] = message.additional_kwargs
                if hasattr(message, 'response_metadata'):
                    message_dict["response_metadata"] = message.response_metadata
                history_dict.append(message_dict)
            
            return history_dict
        except Exception as e:
            raise ChatException(msg=f"获取对话历史失败: {str(e)}")

    def clear_conversation_history(self, session_id: int):
        """
        清空会话的对话历史
        :param session_id: 会话ID
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        :raises ChatException: 清空历史失败
        """
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        session = self.session_repository.get_session_by_session_id(session_id)
        if session is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        try:
            thread_id = str(session_id)
            clear_conversation_history(thread_id)
        except Exception as e:
            raise ChatException(msg=f"清空对话历史失败: {str(e)}")