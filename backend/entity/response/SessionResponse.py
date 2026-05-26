from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from backend.entity.pojo.Session import SessionPOJO


class SessionResponse(BaseModel):
    id: int = Field(..., description="会话ID")
    status: str = Field(..., description="会话状态")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    last_activity_at: Optional[datetime] = Field(default=None, description="最后活动时间")

    @classmethod
    def from_entity(cls, session: SessionPOJO) -> 'SessionResponse':
        return cls(
            id=session.id,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_activity_at=session.last_activity_at
        )