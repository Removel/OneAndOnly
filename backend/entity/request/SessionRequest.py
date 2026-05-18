from typing import List, Dict, Any, Optional


class SessionRequest:
    def __init__(self):
        self.user_id: int = 0
        self.session_name: str = ""
        self.metadata: Dict[str, Any] = {}

    def get_user_id(self) -> int:
        return self.user_id
    
    def get_session_name(self) -> str:
        return self.session_name
    
    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata

    def set_user_id(self, user_id: int):
        self.user_id = user_id
    
    def set_session_name(self, session_name: str):
        self.session_name = session_name
    
    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata = metadata