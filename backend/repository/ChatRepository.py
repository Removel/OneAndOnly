from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc, and_

from backend.config.DatabaseConfig import SessionLocal
from backend.entity.pojo.ConversationHistory import ConversationHistory


class ChatRepository:
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
    
    def find_chat_history_by_id(self, conversation_id: int) -> List[Dict[str, Any]]:
        """
        根据对话ID获取对话历史记录
        :param conversation_id: 对话ID（这里应该是session_id）
        :return: 对话历史记录列表
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter_by(
                session_id=conversation_id
            ).order_by(ConversationHistory.message_order, ConversationHistory.created_at).all()
            
            return [history.to_dict() for history in histories]
        except Exception as e:
            print(f"获取对话历史失败: {str(e)}")
            return []
    
    def create_conversation_history(self, history_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建新的对话历史记录
        :param history_data: 对话历史数据
        :return: 创建的对话历史记录，如果失败则返回None
        """
        try:
            db = self._get_db()
            history = ConversationHistory(
                session_id=history_data.get('session_id'),
                user_id=history_data.get('user_id'),
                message_type=history_data.get('message_type'),
                content=history_data.get('content'),
                state_info=history_data.get('state_info'),
                metadata=history_data.get('metadata'),
                retry_times=history_data.get('retry_times', 0),
                success=history_data.get('success', 1),
                error_message=history_data.get('error_message'),
                message_order=history_data.get('message_order', 0),
                parent_message_id=history_data.get('parent_message_id')
            )
            
            db.add(history)
            db.commit()
            db.refresh(history)
            
            return history.to_dict()
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"创建对话历史失败: {str(e)}")
            return None
    
    def get_conversation_by_id(self, history_id: int) -> Optional[Dict[str, Any]]:
        """
        根据历史记录ID获取单条对话历史
        :param history_id: 历史记录ID
        :return: 对话历史记录，如果不存在则返回None
        """
        try:
            db = self._get_db()
            history = db.query(ConversationHistory).filter_by(id=history_id).first()
            if history:
                return history.to_dict()
            return None
        except Exception as e:
            print(f"获取对话历史失败: {str(e)}")
            return None
    
    def delete_conversation_history(self, history_id: int) -> bool:
        """
        删除指定的对话历史记录
        :param history_id: 要删除的历史记录ID
        :return: 是否删除成功
        """
        try:
            db = self._get_db()
            history = db.query(ConversationHistory).filter_by(id=history_id).first()
            if history:
                db.delete(history)
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"删除对话历史失败: {str(e)}")
            return False
    
    def delete_conversation_history_by_session_id(self, session_id: int) -> bool:
        """
        删除指定会话的所有对话历史
        :param session_id: 会话ID
        :return: 是否删除成功
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter_by(session_id=session_id).all()
            for history in histories:
                db.delete(history)
            db.commit()
            return True
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"删除会话对话历史失败: {str(e)}")
            return False
    
    def update_conversation_history(self, history_id: int, history_data: Dict[str, Any]) -> bool:
        """
        更新对话历史记录
        :param history_id: 历史记录ID
        :param history_data: 要更新的对话历史数据
        :return: 是否更新成功
        """
        try:
            db = self._get_db()
            history = db.query(ConversationHistory).filter_by(id=history_id).first()
            if history:
                if 'content' in history_data:
                    history.content = history_data['content']
                if 'state_info' in history_data:
                    history.state_info = history_data['state_info']
                if 'metadata' in history_data:
                    history.metadata = history_data['metadata']
                if 'retry_times' in history_data:
                    history.retry_times = history_data['retry_times']
                if 'success' in history_data:
                    history.success = history_data['success']
                if 'error_message' in history_data:
                    history.error_message = history_data['error_message']
                
                history.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db = self._get_db()
            db.rollback()
            print(f"更新对话历史失败: {str(e)}")
            return False
    
    def get_conversations_by_type(self, session_id: int, message_type: str) -> List[Dict[str, Any]]:
        """
        根据消息类型获取对话历史
        :param session_id: 会话ID
        :param message_type: 消息类型
        :return: 对话历史记录列表
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter_by(
                session_id=session_id,
                message_type=message_type
            ).order_by(ConversationHistory.message_order, ConversationHistory.created_at).all()
            
            return [history.to_dict() for history in histories]
        except Exception as e:
            print(f"获取指定类型对话历史失败: {str(e)}")
            return []
    
    def get_latest_conversation(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        获取会话中最新的一条对话记录
        :param session_id: 会话ID
        :return: 最新的对话记录，如果不存在则返回None
        """
        try:
            db = self._get_db()
            history = db.query(ConversationHistory).filter_by(
                session_id=session_id
            ).order_by(desc(ConversationHistory.message_order), desc(ConversationHistory.created_at)).first()
            
            if history:
                return history.to_dict()
            return None
        except Exception as e:
            print(f"获取最新对话记录失败: {str(e)}")
            return None
    
    def get_conversations_by_user(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        根据用户ID获取对话历史
        :param user_id: 用户ID
        :param limit: 返回数量限制
        :return: 对话历史记录列表
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter_by(
                user_id=user_id
            ).order_by(desc(ConversationHistory.created_at)).limit(limit).all()
            
            return [history.to_dict() for history in histories]
        except Exception as e:
            print(f"获取用户对话历史失败: {str(e)}")
            return []
    
    def get_conversation_count(self, session_id: int) -> int:
        """
        获取会话的对话记录数量
        :param session_id: 会话ID
        :return: 对话记录数量
        """
        try:
            db = self._get_db()
            count = db.query(ConversationHistory).filter_by(session_id=session_id).count()
            return count
        except Exception as e:
            print(f"获取对话记录数量失败: {str(e)}")
            return 0
    
    def get_failed_conversations(self, session_id: int) -> List[Dict[str, Any]]:
        """
        获取会话中失败的对话记录
        :param session_id: 会话ID
        :return: 失败的对话记录列表
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter(
                and_(
                    ConversationHistory.session_id == session_id,
                    ConversationHistory.success == 0
                )
            ).order_by(ConversationHistory.created_at).all()
            
            return [history.to_dict() for history in histories]
        except Exception as e:
            print(f"获取失败对话记录失败: {str(e)}")
            return []
    
    def get_conversation_tree(self, session_id: int) -> List[Dict[str, Any]]:
        """
        获取会话的对话树结构
        :param session_id: 会话ID
        :return: 对话树结构
        """
        try:
            db = self._get_db()
            histories = db.query(ConversationHistory).filter_by(
                session_id=session_id
            ).order_by(ConversationHistory.message_order, ConversationHistory.created_at).all()
            
            tree = []
            history_dict = {h.id: h.to_dict() for h in histories}
            
            for history in histories:
                history_data = history_dict[history.id]
                if history.parent_message_id is None:
                    tree.append(history_data)
                else:
                    parent = history_dict.get(history.parent_message_id)
                    if parent:
                        if 'children' not in parent:
                            parent['children'] = []
                        parent['children'].append(history_data)
            
            return tree
        except Exception as e:
            print(f"获取对话树结构失败: {str(e)}")
            return []