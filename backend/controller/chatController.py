from dask.array import empty
from fastapi import FastAPI

from backend.model.ChatRequest import ChatRequest
from backend.model.ChatResponse import ChatResponse
from backend.model.Result import Result
from backend.service.ChatService import ChatService

app = FastAPI()

@app.post("/api/chat")
def chat(chat_request: ChatRequest)->Result[ChatResponse]:
    """
    处理用户输入，调用智能体进行对话
    :param chat_request: 用户对话请求内容
    :return: 智能体的回复
    """
    input_text = chat_request.get_human_input()
    conversation_id = chat_request.get_conversation_id()
    clear_history = chat_request.get_clear_history()
    chat_response = ChatService.chat(human_input=input_text, conversation_id=conversation_id, clear_history=clear_history)
    return Result.success(chat_response)



