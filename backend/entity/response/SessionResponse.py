from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.entity.pojo.Session import SessionPOJO


class SessionResponse:

    def __init__(self, session: SessionPOJO = None):
        self.session = session or SessionPOJO()
        self.session_list = []

    def get_session_id(self) -> int:
        return self.session.id

    def get_status(self) -> str:
        return self.session.status

    def get_created_at(self) -> Optional[datetime]:
        return self.session.created_at
    
    def get_updated_at(self) -> Optional[datetime]:
        return self.session.updated_at
    
    def get_last_activity_at(self) -> Optional[datetime]:
        return self.session.last_activity_at

    def set_session_id(self, session_id: int):
        self.session.id = session_id
    
    def set_status(self, status: str):
        self.session.status = status

    def set_created_at(self, created_at: datetime):
        self.session.created_at = created_at
    
    def set_updated_at(self, updated_at: datetime):
        self.session.updated_at = updated_at
    
    def set_last_activity_at(self, last_activity_at: datetime):
        self.session.last_activity_at = last_activity_at
