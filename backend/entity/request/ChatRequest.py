from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    human_input: str = Field(..., description="用户输入文本")
    session_id: int = Field(..., description="会话ID")
    clear_history: bool = Field(default=False, description="是否清空历史记录")