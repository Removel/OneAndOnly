from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.entity.pojo.Session import SessionPOJO
from backend.entity.response.SessionResponse import SessionResponse
from backend.entity.request.SessionRequest import SessionRequest
from backend.repository.SessionRepository import SessionRepository


class SessionService:
    def __init__(self):
        self.session_repository = SessionRepository()

    def get_session_by_session_id(self,session_id: int) -> Optional[SessionResponse]:
        """
        根据session_id获取会话详情
        :param session_id: 会话ID
        :return: SessionResponse对象，如果不存在则返回None
        """
        repository = self.session_repository
        try:
            result = repository.get_session_by_session_id(session_id)
            if result:
                return SessionResponse(
                    session=result
                )
            return None
        except Exception as e:
            print(f"获取会话失败: {str(e)}")
            return None
        finally:
            if repository.db:
                repository.db.close()

    def create_session(self)->Optional[int] :
        """
        创建新的对话会话
        :return: 创建的会话ID，如果失败则返回None
        """
        repository = self.session_repository
        try:
            session_id = repository.create()
            if session_id:
                return session_id
            return None
        except Exception as e:
            print(f"创建会话失败: {str(e)}")
            return None
        finally:
            if repository.db:
                repository.db.close()

    def delete_session(self,session_id: int) -> bool:
        """
        删除指定的对话会话
        :param session_id: 要删除的会话ID
        :return: 是否删除成功
        """
        repository = self.session_repository
        try:
            return repository.delete(session_id)
        except Exception as e:
            print(f"删除会话失败: {str(e)}")
            return False
        finally:
            if repository.db:
                repository.db.close()

    def update_session(self,session_id: int,to_update_data: Dict[str, Any]) -> bool:
        """
        更新指定的对话会话
        :param session_id: 要更新的会话ID
        :param to_update_data: 包含更新信息的字典对象
        :return: 是否更新成功
        """
        repository = self.session_repository
        try:
            return repository.update_session(session_id,to_update_data)
        except Exception as e:
            print(f"更新会话失败: {str(e)}")
            return False
        finally:
            if repository.db:
                repository.db.close()

    def get_active_sessions(self)->List[SessionPOJO]:
        """
        获取所有活跃会话信息
        :return: 活跃会话信息包装在SessionPOJO列表中
        """
        repository = self.session_repository
        try:
            result = repository.get_active_sessions()
            if result is not None:
                return result
            return []
        except Exception as e:
            print(f"获取活跃会话失败: {str(e)}")
            return None
        finally:
            if repository.db:
                repository.db.close()