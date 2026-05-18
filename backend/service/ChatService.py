from agent.main import chat_with_agent
from backend.model.ChatResponse import ChatResponse


class ChatService:
    def __init__(self):
        pass

    @staticmethod
    def chat(self, human_input:str, conversation_id:int, clear_history:bool)->ChatResponse:
        # 通过conversation_id获取对话历史
        conversation_history =
        # 调用agent进行对话
        chat_response_dict = chat_with_agent(
            user_input=human_input,
            conversation_history=conversation_history,
            clear_history=clear_history
        )
        # 转换为ChatResponse对象
        chat_response = ChatResponse(**chat_response_dict)
        # 返回对话结果
        return chat_response
