from pydantic import BaseModel, Field
from typing import List, Optional
from backend.entity.response.MessageResponse import MessageResponse


class ChatHistoryResponse(BaseModel):
    session_id: int = Field(..., description="会话ID")
    messages: List[MessageResponse] = Field(default_factory=list, description="消息历史列表")
    total_count: int = Field(default=0, description="消息总数")

    @classmethod
    def from_data(cls, session_id: int, messages: List[dict]) -> 'ChatHistoryResponse':
        message_responses = [MessageResponse.from_dict(msg) for msg in messages]
        return cls(
            session_id=session_id,
            messages=message_responses,
            total_count=len(message_responses)
        )