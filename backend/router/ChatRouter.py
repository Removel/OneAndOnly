import logging
from fastapi import APIRouter

from backend.entity.request.ChatRequest import ChatRequest
from backend.entity.response.ChatResponse import ChatResponse
from backend.entity.Result import Result
from backend.service.ChatService import ChatService

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用APIRouter而不是FastAPI主应用，更适合模块化路由管理
chat_router = APIRouter(prefix="/api", tags=["chat"])

@chat_router.post("/chat", response_model=Result[ChatResponse])
async def chat_endpoint(chat_request: ChatRequest) -> Result[ChatResponse]:
    """
    处理用户输入，调用智能体进行对话
    :param chat_request: 用户对话请求内容
    :return: 智能体的回复包装在Result中
    """
    try:
        # 输入验证
        input_text = chat_request.get_human_input()
        conversation_id = chat_request.get_conversation_id()
        clear_history = chat_request.get_clear_history()
        
        if not input_text or input_text.strip() == "":
            return Result.error(msg="输入文本不能为空", code=400)
        
        logger.info(f"收到聊天请求，对话ID: {conversation_id}, 清除历史: {clear_history}")
        
        # 调用聊天服务处理请求
        chat_response = ChatService.chat(
            human_input=input_text, 
            conversation_id=conversation_id, 
            clear_history=clear_history
        )
        
        logger.info(f"聊天响应成功，对话ID: {conversation_id}, 成功: {chat_response.success}")
        
        return Result.success(data=chat_response)
    
    except ValueError as ve:
        logger.error(f"值错误: {str(ve)}")
        return Result.error(msg=f"参数错误: {str(ve)}", code=400)
    except Exception as e:
        logger.error(f"聊天服务处理失败: {str(e)}")
        # 捕获异常并返回错误结果
        error_msg = f"聊天服务处理失败: {str(e)}"
        return Result.error(msg=error_msg, code=500)