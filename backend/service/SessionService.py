from typing import Optional, List, Dict, Any
import logging

from backend.entity.pojo.Session import SessionPOJO
from backend.repository.SessionRepository import SessionRepository
from backend.exception.Exceptions import ParamValidationException, NotFoundException

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self):
        self.session_repository = SessionRepository()
        logger.debug("SessionService初始化完成")

    def get_session_by_session_id(self, session_id: int) -> SessionPOJO:
        """
        根据session_id获取会话详情
        :param session_id: 会话ID
        :return: SessionPOJO实体
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        logger.debug(f"查询会话详情，会话ID: {session_id}")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        logger.debug(f"查询会话详情成功，会话ID: {session_id}, 状态: {result.status}")
        return result

    def create_session(self) -> SessionPOJO:
        """
        创建新的对话会话
        :return: 创建的会话实体
        """
        logger.info("创建新会话")
        result = self.session_repository.create()
        logger.info(f"创建会话成功，会话ID: {result.id}, 状态: {result.status}")
        return result

    def delete_session(self, session_id: int):
        """
        删除指定的对话会话
        :param session_id: 要删除的会话ID
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        logger.info(f"删除会话，会话ID: {session_id}")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        self.session_repository.delete(session_id)
        logger.info(f"删除会话成功，会话ID: {session_id}")

    def update_session(self, session_id: int, to_update_data: Dict[str, Any]) -> SessionPOJO:
        """
        更新指定的对话会话
        :param session_id: 要更新的会话ID
        :param to_update_data: 包含更新信息的字典对象
        :return: 更新后的会话实体
        :raises ParamValidationException: 参数验证失败
        :raises NotFoundException: 会话不存在
        """
        logger.info(f"更新会话，会话ID: {session_id}, 更新数据: {to_update_data}")
        
        if session_id <= 0:
            logger.warning(f"参数验证失败，会话ID必须为正整数，实际值: {session_id}")
            raise ParamValidationException(msg="会话ID必须为正整数")
        
        if not to_update_data:
            logger.warning("参数验证失败，更新数据不能为空")
            raise ParamValidationException(msg="更新数据不能为空")
        
        result = self.session_repository.get_session_by_session_id(session_id)
        if result is None:
            logger.warning(f"会话不存在，会话ID: {session_id}")
            raise NotFoundException(msg=f"会话ID {session_id} 不存在")
        
        self.session_repository.update_session(session_id, to_update_data)
        updated_result = self.session_repository.get_session_by_session_id(session_id)
        logger.info(f"更新会话成功，会话ID: {session_id}, 新状态: {updated_result.status}")
        return updated_result

    def get_active_sessions(self) -> List[SessionPOJO]:
        """
        获取所有活跃会话信息
        :return: 活跃会话实体列表
        """
        logger.debug("查询活跃会话列表")
        result = self.session_repository.get_active_sessions()
        if result is None:
            result = []
        logger.debug(f"查询活跃会话成功，共 {len(result)} 个活跃会话")
        return result

    def get_all_sessions(self) -> List[SessionPOJO]:
        """
        获取所有会话信息
        :return: 所有会话实体列表
        """
        logger.debug("查询所有会话列表")
        result = self.session_repository.get_all_sessions()
        if result is None:
            result = []
        logger.debug(f"查询所有会话成功，共 {len(result)} 个会话")
        return result