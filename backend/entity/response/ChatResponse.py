from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI回复文本")
    emotion_vac: Dict[str, Any] = Field(default_factory=dict, description="情感向量")
    retry_times: int = Field(default=0, description="重试次数")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    success: bool = Field(default=True, description="是否成功")