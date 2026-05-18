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
    
    def get_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        根据session_id获取对话历史
        :param session_id: 会话ID
        :return: 会话数据字典，如果不存在则返回None
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                return session.to_dict()
            return None
        except Exception as e:
            print(f"获取会话失败: {str(e)}")
            return None
    
    def create(self, session_request: SessionRequest) -> Optional[Dict[str, Any]]:
        """
        创建新的对话会话
        :param session_request: 会话请求对象
        :return: 创建的会话数据字典，如果失败则返回None
        """
        try:
            db = self._get_db()
            session = SessionPOJO(
                user_id=session_request.get_user_id(),
                session_name=session_request.get_session_name() or f"对话会话 {datetime.now().strftime('%Y%m%d%H%M%S')}",
                status='active',
                metadata=session_request.get_metadata()
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return session.to_dict()
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"创建会话失败: {str(e)}")
            return None
    
    def delete(self, session_id: int) -> bool:
        """
        删除指定的对话会话
        :param session_id: 要删除的会话ID
        :return: 是否删除成功
        """
        try:
            db = self._get_db()
            session = db.query(SessionPOJO).filter_by(id=session_id).first()
            if session:
                db.delete(session)
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
                if 'session_name' in session_data:
                    session.session_name = session_data['session_name']
                if 'status' in session_data:
                    session.status = session_data['status']
                if 'global_state' in session_data:
                    session.global_state = session_data['global_state']
                if 'metadata' in session_data:
                    session.metadata = session_data['metadata']
                
                session.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"更新会话失败: {str(e)}")
            return False
    
    def get_sessions_by_user_id(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        根据用户ID获取会话列表
        :param user_id: 用户ID
        :param limit: 返回数量限制
        :return: 会话列表
        """
        try:
            db = self._get_db()
            sessions = db.query(SessionPOJO).filter_by(
                user_id=user_id
            ).order_by(desc(SessionPOJO.last_activity_at)).limit(limit).all()
            
            return [session.to_dict() for session in sessions]
        except Exception as e:
            print(f"获取用户会话列表失败: {str(e)}")
            return []
    
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
    
    def get_active_sessions(self, user_id: int = None) -> List[Dict[str, Any]]:
        """
        获取活跃的会话列表
        :param user_id: 用户ID（可选）
        :return: 活跃会话列表
        """
        try:
            db = self._get_db()
            query = db.query(SessionPOJO).filter_by(status='active')
            if user_id:
                query = query.filter_by(user_id=user_id)
            
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