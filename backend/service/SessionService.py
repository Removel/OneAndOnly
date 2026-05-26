from typing import Optional, List, Dict, Any

from backend.entity.pojo.Session import SessionPOJO
from backend.repository.SessionRepository import SessionRepository
from backend.exception.Exceptions import ParamValidationException, NotFoundException


class SessionService:
    def __init__(self):
        self.session_repository = SessionRepository()

    def get_session_by_session_id(self, session_id: int) -> SessionPOJO:
        """
        根据session_id获取会话详情
        :param session_id: 会话ID
        :return: SessionPOJO实体
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        return result

    def create_session(self) -> SessionPOJO:
        """
        创建新的对话会话
        :return: 创建的会话实体
        """
        return self.session_repository.create()

    def delete_session(self, session_id: int):
        """
        删除指定的对话会话
        :param session_id: 要删除的会话ID
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        self.session_repository.delete(session_id)

    def update_session(self, session_id: int, to_update_data: Dict[str, Any]) -> SessionPOJO:
        """
        更新指定的对话会话
        :param session_id: 要更新的会话ID
        :param to_update_data: 包含更新信息的字典对象
        :return: 更新后的会话实体
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        if session_id <= 0:
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        if not to_update_data:
            raise ParamValidationException(msg="更新数据不能为空")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        self.session_repository.update_session(session_id, to_update_data)
        return self.session_repository.get_session_by_session_id(session_id)

    def get_active_sessions(self) -> List[SessionPOJO]:
        """
        获取所有活跃会话信息
        :return: 活跃会话实体列表
        """
        result = self.session_repository.get_active_sessions()
        if result is None:
            return []
        return result

    def get_all_sessions(self) -> List[SessionPOJO]:
        """
        获取所有会话信息
        :return: 所有会话实体列表
        """
        result = self.session_repository.get_all_sessions()
        if result is None:
            return []
        return result