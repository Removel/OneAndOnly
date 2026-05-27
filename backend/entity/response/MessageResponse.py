from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MessageResponse(BaseModel):
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")
    message_id: Optional[str] = Field(default=None, description="消息ID")
    additional_kwargs: Optional[Dict[str, Any]] = Field(default=None, description="额外参数")
    response_metadata: Optional[Dict[str, Any]] = Field(default=None, description="响应元数据")

    @classmethod
    def from_dict(cls, message_dict: Dict[str, Any]) -> 'MessageResponse':
        type_name = message_dict.get("type", "")
        
        if type_name == "HumanMessage":
            role = "user"
        elif type_name == "AIMessage":
            role = "assistant"
        elif type_name == "SystemMessage":
            role = "system"
        else:
            role = "unknown"
        
        return cls(
            role=role,
            content=message_dict.get("content", ""),
            message_id=message_dict.get("id"),
            additional_kwargs=message_dict.get("additional_kwargs"),
            response_metadata=message_dict.get("response_metadata")
        )