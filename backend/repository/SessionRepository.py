from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config.DatabaseConfig import SessionLocal
from backend.entity.pojo.Session import Session as SessionPOJO
from backend.entity.request.SessionRequest import SessionRequest


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

    
    def create(self, new_session:SessionPOJO) -> Optional[Dict[str, Any]]:
        """
        创建新的对话会话
        :param new_session: 新会话对象
        :return: 创建的会话数据字典，如果失败则返回None
        """
        try:
            db = self._get_db()
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session.to_dict()
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"创建会话失败: {str(e)}")
            return None
    
    def delete(self, session_id: int) -> bool:
        """
        删除指定的对话会话（软删除，只修改状态）
        :param session_id: 要删除的会话ID
        :return: 是否删除成功
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                session.status = 'deleted'
                session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"删除会话失败: {str(e)}")
            return False
    
    def update_session(self, session_id: int, session_data: Dict[str, Any]) -> bool:
        """
        更新会话信息
        :param session_id: 会话ID
        :param session_data: 要更新的会话数据
        :return: 是否更新成功
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                if 'status' in session_data:
                    session.status = session_data['status']
                if 'last_activity_at' in session_data:
                    session.last_activity_at = session_data['last_activity_at']

                session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"更新会话失败: {str(e)}")
            return False
    
    def update_last_activity(self, session_id: int) -> bool:
        """
        更新会话的最后活动时间
        :param session_id: 会话ID
        :return: 是否更新成功
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                session.last_activity_at = datetime.now()
                session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"更新最后活动时间失败: {str(e)}")
            return False
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        获取活跃的会话列表
        :return: 活跃会话列表
        """
        try:
            db = self._get_db()
            query = db.query(SessionPOJO).filter_by(status='active')
            
            sessions = query.order_by(desc(SessionPOJO.last_activity_at)).all()
            return [session.to_dict() for session in sessions]
        except Exception as e:
            print(f"获取活跃会话失败: {str(e)}")
            return []
    
    def archive_session(self, session_id: int) -> bool:
        """
        归档会话
        :param session_id: 会话ID
        :return: 是否归档成功
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                session.status = 'archived'
                session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"归档会话失败: {str(e)}")
            return False