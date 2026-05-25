from typing import Optional, List, Dict, Any, cast
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config.DatabaseConfig import SessionLocal
from backend.entity.pojo.Session import SessionPOJO
from backend.exception.Exceptions import DatabaseException

class SessionRepository:
    def __init__(self):
        self.db: Optional[Session] = None
    
    def __enter__(self):
        self.db = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
    
    def _get_db(self) -> Session:
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    
    def create(self) -> int:
        """
        创建新的对话会话
        :return: 创建的会话ID
        :raises DatabaseException: 创建会话失败时抛出
        """
        try:
            db = self._get_db()
            # 创建一个基本的SessionPOJO对象，ID将由数据库自动生成（雪花算法）
            new_session = SessionPOJO()
            db.add(new_session)
            db.commit()
            db.refresh(new_session)  # 刷新以获取数据库生成的ID
            return new_session.id
        except Exception as e:
            db = self._get_db()
            db.rollback()
            raise DatabaseException(msg=f"创建会话失败: {str(e)}", cause=e)
    
    def delete(self, session_id: int) -> bool:
        """
        删除指定的对话会话（软删除，只修改状态）
        :param session_id: 要删除的会话ID
        :return: 是否删除成功
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.status = 'deleted'
                operated_session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            raise DatabaseException(msg=f"删除会话失败: {str(e)}", cause=e)

    def update_session(self, session_id: int, session_data: Dict[str, Any]) -> bool:
        """
        更新会话信息
        :param session_id: 会话ID
        :param session_data: 要更新的会话数据
        :return: 是否更新成功
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                # 只更新提供的字段
                for field, value in session_data.items():
                    if hasattr(operated_session, field) and field not in [
                        "id",
                        "created_at",
                    ]:
                        setattr(operated_session, field, value)

                # 自动更新时间戳
                operated_session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            raise DatabaseException(msg=f"更新会话失败: {str(e)}", cause=e)

    
    def update_last_activity(self, session_id: int) -> bool:
        """
        更新会话的最后活动时间
        :param session_id: 会话ID
        :return: 是否更新成功
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.last_activity_at = datetime.now()
                operated_session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            raise DatabaseException(msg=f"更新最后活动时间失败: {str(e)}", cause=e)

    def get_active_sessions(self) -> List[SessionPOJO]:
        """
        获取活跃的会话列表
        :return: 活跃会话列表
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            # 查询所有状态为 'active' 的会话，按最后活动时间降序排列
            session_list = (
                db.query(SessionPOJO)
                .filter_by(status="active")
                .order_by(desc(SessionPOJO.last_activity_at))
                .all()
            )
            return cast(List[SessionPOJO], session_list)
        except Exception as e:
            raise DatabaseException(msg=f"获取活跃会话失败: {str(e)}", cause=e)
    
    def archive_session(self, session_id: int) -> bool:
        """
        归档会话
        :param session_id: 会话ID
        :return: 是否归档成功
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.status = 'archived'
                operated_session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            raise DatabaseException(msg=f"归档会话失败: {str(e)}", cause=e)

    def query_session_exists(self, session_id: int) -> bool:
        """
        查询会话是否存在
        :param session_id: 会话ID
        :return: 是否会话存在
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                return True
            return False
        except Exception as e:
            raise DatabaseException(msg=f"查询会话失败: {str(e)}", cause=e)

    def get_session_by_session_id(self, session_id: int) -> Optional[SessionPOJO]:
        """
        根据会话ID获取会话详情
        :param session_id: 会话ID
        :return: 会话字典，如果不存在则返回None
        :raises DatabaseException: 数据库操作失败时抛出
        """
        try:
            db = self._get_db()
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                return cast(SessionPOJO, operated_session)
            return None
        except Exception as e:
            raise DatabaseException(msg=f"查询会话失败: {str(e)}", cause=e)