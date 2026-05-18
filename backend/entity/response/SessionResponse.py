from typing import List, Dict, Any, Optional
from datetime import datetime


class SessionResponse:
    def __init__(self, 
                 session_id: int = 0,
                 user_id: int = 0,
                 session_name: str = "",
                 status: str = "active",
                 global_state: Dict[str, Any] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 last_activity_at: Optional[datetime] = None,
                 metadata: Dict[str, Any] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.session_name = session_name
        self.status = status
        self.global_state = global_state or {}
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_activity_at = last_activity_at
        self.metadata = metadata or {}

    def get_session_id(self) -> int:
        return self.session_id
    
    def get_user_id(self) -> int:
        return self.user_id
    
    def get_session_name(self) -> str:
        return self.session_name
    
    def get_status(self) -> str:
        return self.status
    
    def get_global_state(self) -> Dict[str, Any]:
        return self.global_state
    
    def get_created_at(self) -> Optional[datetime]:
        return self.created_at
    
    def get_updated_at(self) -> Optional[datetime]:
        return self.updated_at
    
    def get_last_activity_at(self) -> Optional[datetime]:
        return self.last_activity_at
    
    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata

    def set_session_id(self, session_id: int):
        self.session_id = session_id
    
    def set_user_id(self, user_id: int):
        self.user_id = user_id
    
    def set_session_name(self, session_name: str):
        self.session_name = session_name
    
    def set_status(self, status: str):
        self.status = status
    
    def set_global_state(self, global_state: Dict[str, Any]):
        self.global_state = global_state
    
    def set_created_at(self, created_at: datetime):
        self.created_at = created_at
    
    def set_updated_at(self, updated_at: datetime):
        self.updated_at = updated_at
    
    def set_last_activity_at(self, last_activity_at: datetime):
        self.last_activity_at = last_activity_at
    
    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata = metadata