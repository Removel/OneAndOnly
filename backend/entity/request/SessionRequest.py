from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionRequest(BaseModel):
    session_id: Optional[int] = Field(default=None, description="会话ID")
    status: Optional[str] = Field(default=None, description="会话状态")
    last_activity_at: Optional[datetime] = Field(default=None, description="最后活动时间")

    def to_dict(self):
        result = {}
        if self.status is not None:
            result["status"] = self.status
        if self.last_activity_at is not None:
            result["last_activity_at"] = self.last_activity_at
        return result