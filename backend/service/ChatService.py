from agent.main import chat_with_agent
from backend.entity.response.ChatResponse import ChatResponse
from backend.repository.ChatRepository import ChatRepository
from backend.repository.SessionRepository import SessionRepository


class ChatService:
    def __init__(self):
        self.chat_repository = ChatRepository()
        self.session_repository = SessionRepository()

    @staticmethod
    def chat(human_input: str, conversation_id: int, clear_history: bool, user_id: int = 1) -> ChatResponse:
        """
        执行聊天操作
        :param human_input: 用户输入文本
        :param conversation_id: 对话ID
        :param clear_history: 是否清空历史记录
        :param user_id: 用户ID
        :return: ChatResponse对象
        """
        chat_repository = ChatRepository()
        session_repository = SessionRepository()
        
        try:
            session = session_repository.get_by_id(conversation_id)
            if not session:
                return ChatResponse(
                    response=f"会话ID {conversation_id} 不存在",
                    error_message=f"会话ID {conversation_id} 不存在",
                    success=False
                )
            
            conversation_history = []
            
            if clear_history:
                chat_repository.delete_conversation_history_by_session_id(conversation_id)
            else:
                histories = chat_repository.find_chat_history_by_id(conversation_id)
                conversation_history = histories
            
            chat_response_dict = chat_with_agent(
                user_input=human_input,
                conversation_history=conversation_history,
                clear_history=clear_history
            )
            
            if isinstance(chat_response_dict, dict):
                chat_response = ChatResponse(**chat_response_dict)
            else:
                chat_response = chat_response_dict
            
            message_order = chat_repository.get_conversation_count(conversation_id)
            
            user_history_data = {
                'session_id': conversation_id,
                'user_id': user_id,
                'message_type': 'human',
                'content': human_input,
                'message_order': message_order,
                'success': 1
            }
            chat_repository.create_conversation_history(user_history_data)
            
            ai_history_data = {
                'session_id': conversation_id,
                'user_id': user_id,
                'message_type': 'ai',
                'content': chat_response.response,
                'state_info': chat_response.vac,
                'message_order': message_order + 1,
                'success': 1 if chat_response.success else 0,
                'error_message': chat_response.error_message if not chat_response.success else None
            }
            chat_repository.create_conversation_history(ai_history_data)
            
            session_repository.update_last_activity(conversation_id)
            
            return chat_response

        except Exception as e:
            return ChatResponse(
                response=f"聊天过程中发生错误: {str(e)}",
                error_message=str(e),
                success=False
            )
        finally:
            if chat_repository.db:
                chat_repository.db.close()
            if session_repository.db:
                session_repository.db.close()