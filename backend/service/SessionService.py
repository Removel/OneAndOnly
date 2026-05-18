from typing import Optional
from datetime import datetime

from backend.entity.response.SessionResponse import SessionResponse
from backend.entity.request.SessionRequest import SessionRequest
from backend.repository.SessionRepository import SessionRepository


class SessionService:
    def __init__(self):
        self.session_repository = SessionRepository()

    @staticmethod
    def get_session_by_id(session_id: int) -> Optional[SessionResponse]:
        """
        根据session_id获取对话历史
        :param session_id: 会话ID
        :return: SessionResponse对象，如果不存在则返回None
        """
        repository = SessionRepository()
        try:
            session_data = repository.get_by_id(session_id)
            if session_data:
                return SessionResponse(
                    session_id=session_data['id'],
                    user_id=session_data['user_id'],
                    session_name=session_data['session_name'],
                    status=session_data['status'],
                    global_state=session_data['global_state'],
                    metadata=session_data['metadata'],
                    created_at=datetime.fromisoformat(session_data['created_at']) if session_data['created_at'] else None,
                    updated_at=datetime.fromisoformat(session_data['updated_at']) if session_data['updated_at'] else None,
                    last_activity_at=datetime.fromisoformat(session_data['last_activity_at']) if session_data['last_activity_at'] else None
                )
            return None
        except Exception as e:
            print(f"获取会话失败: {str(e)}")
            return None
        finally:
            if repository.db:
                repository.db.close()

    @staticmethod
    def create_session(session_request: SessionRequest) -> Optional[SessionResponse]:
        """
        创建新的对话会话
        :param session_request: 会话请求对象
        :return: 创建的SessionResponse对象，如果失败则返回None
        """
        repository = SessionRepository()
        try:
            session_data = repository.create(session_request)
            if session_data:
                return SessionResponse(
                    session_id=session_data['id'],
                    user_id=session_data['user_id'],
                    session_name=session_data['session_name'],
                    status=session_data['status'],
                    global_state=session_data['global_state'],
                    metadata=session_data['metadata'],
                    created_at=datetime.fromisoformat(session_data['created_at']) if session_data['created_at'] else None,
                    updated_at=datetime.fromisoformat(session_data['updated_at']) if session_data['updated_at'] else None,
                    last_activity_at=datetime.fromisoformat(session_data['last_activity_at']) if session_data['last_activity_at'] else None
                )
            return None
        except Exception as e:
            print(f"创建会话失败: {str(e)}")
            return None
        finally:
            if repository.db:
                repository.db.close()

    @staticmethod
    def delete_session(session_id: int) -> bool:
        """
        删除指定的对话会话
        :param session_id: 要删除的会话ID
        :return: 是否删除成功
        """
        repository = SessionRepository()
        try:
            return repository.delete(session_id)
        except Exception as e:
            print(f"删除会话失败: {str(e)}")
            return False
        finally:
            if repository.db:
                repository.db.close()