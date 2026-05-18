from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.entity.pojo.Base import Base


class Session(Base):
    """
    会话POJO类，用于管理对话会话
    """
    __tablename__ = 'session'
    
    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='会话ID')
    
    # 用户ID
    user_id = Column(Integer, nullable=False, index=True, comment='用户ID')
    
    # 会话名称
    session_name = Column(String(200), nullable=False, comment='会话名称')
    
    # 会话状态：active(活跃), archived(归档), deleted(已删除)
    status = Column(String(50), default='active', comment='会话状态')
    
    # langgraph全局状态
    global_state = Column(JSON, comment='langgraph全局状态')
    
    # 元数据
    metadata = Column(JSON, comment='元数据')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 最后活动时间
    last_activity_at = Column(DateTime, default=datetime.now, comment='最后活动时间')
    
    # 关系定义
    conversation_histories = relationship("ConversationHistory", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, session_name='{self.session_name}', status='{self.status}')>"
    
    def to_dict(self):
        """
        将对象转换为字典
        :return: 字典格式的会话数据
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_name': self.session_name,
            'status': self.status,
            'global_state': self.global_state,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建对象
        :param data: 字典数据
        :return: Session对象
        """
        return cls(
            user_id=data.get('user_id'),
            session_name=data.get('session_name'),
            status=data.get('status', 'active'),
            global_state=data.get('global_state'),
            metadata=data.get('metadata')
        )