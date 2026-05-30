from typing import Optional, List, Dict, Any, cast
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config.DatabaseConfig import SessionLocal
from backend.entity.pojo.Session import SessionPOJO
from backend.exception.Exceptions import DatabaseException

class SessionRepository:
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        return SessionLocal()

    
    def create(self) -> SessionPOJO:
        """
        创建新的对话会话
        :return: 创建的会话实体
        :raises DatabaseException: 创建会话失败时抛出
        """
        db = self._get_db()
        try:
            new_session = SessionPOJO()
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session
        except Exception as e:
            db.rollback()
            raise DatabaseException(msg=f"创建会话失败: {str(e)}", cause=e)
        finally:
            db.close()
    
    def delete(self, session_id: int):
        """
        删除指定的对话会话（软删除，只修改状态）
        :param session_id: 要删除的会话ID
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.status = 'deleted'
                operated_session.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            raise DatabaseException(msg=f"删除会话失败: {str(e)}", cause=e)
        finally:
            db.close()

    def update_session(self, session_id: int, session_data: Dict[str, Any]):
        """
        更新会话信息
        :param session_id: 会话ID
        :param session_data: 要更新的会话数据
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                for field, value in session_data.items():
                    if hasattr(operated_session, field) and field not in [
                        "id",
                        "created_at",
                    ]:
                        setattr(operated_session, field, value)
                operated_session.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            raise DatabaseException(msg=f"更新会话失败: {str(e)}", cause=e)
        finally:
            db.close()

    
    def update_last_activity(self, session_id: int):
        """
        更新会话的最后活动时间
        :param session_id: 会话ID
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.last_activity_at = datetime.now()
                operated_session.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            raise DatabaseException(msg=f"更新最后活动时间失败: {str(e)}", cause=e)
        finally:
            db.close()

    def get_active_sessions(self) -> List[SessionPOJO]:
        """
        获取活跃的会话列表
        :return: 活跃会话列表
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            session_list = (
                db.query(SessionPOJO)
                .filter_by(status="active")
                .order_by(desc(SessionPOJO.last_activity_at))
                .all()
            )
            return cast(List[SessionPOJO], session_list)
        except Exception as e:
            raise DatabaseException(msg=f"获取活跃会话失败: {str(e)}", cause=e)
        finally:
            db.close()
    
    def get_all_sessions(self) -> List[SessionPOJO]:
        """
        获取所有会话列表
        :return: 所有会话列表
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            session_list = (
                db.query(SessionPOJO)
                .order_by(desc(SessionPOJO.last_activity_at))
                .all()
            )
            return cast(List[SessionPOJO], session_list)
        except Exception as e:
            raise DatabaseException(msg=f"获取所有会话失败: {str(e)}", cause=e)
        finally:
            db.close()
    
    def archive_session(self, session_id: int):
        """
        归档会话
        :param session_id: 会话ID
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                operated_session.status = 'archived'
                operated_session.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            db.rollback()
            raise DatabaseException(msg=f"归档会话失败: {str(e)}", cause=e)
        finally:
            db.close()

    def get_session_by_session_id(self, session_id: int) -> Optional[SessionPOJO]:
        """
        根据会话ID获取会话详情
        :param session_id: 会话ID
        :return: 会话实体，如果不存在则返回None
        :raises DatabaseException: 数据库操作失败时抛出
        """
        db = self._get_db()
        try:
            operated_session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if operated_session:
                return cast(SessionPOJO, operated_session)
            return None
        except Exception as e:
            raise DatabaseException(msg=f"查询会话失败: {str(e)}", cause=e)
        finally:
            db.close()