from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.entity.pojo.Session import SessionPOJO


class SessionRequest:
    def __init__(
        self,
        session_id: Optional[int] = None,
        status: Optional[str] = None,
        last_activity_at: Optional[datetime] = None,
    ):
        self.last_activity_at = last_activity_at
        self.session_id = session_id
        self.status = status

    def get_session_id(self) -> Optional[int]:
        return self.session_id

    def set_session_id(self, session_id: int):
        self.session_id = session_id

    def get_status(self) -> Optional[str]:
        return self.status

    def set_status(self, status: str):
        self.status = status
        return self.last_activity_at

    def set_last_activity_at(self, last_activity_at: datetime):
        self.last_activity_at = last_activity_at

    def get_last_activity_at(self) -> Optional[datetime]:
        return self.last_activity_at

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "status": self.status,
            "last_activity_at": self.last_activity_at,
        }
