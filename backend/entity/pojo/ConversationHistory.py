from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.entity.pojo.Base import Base


class ConversationHistory(Base):
    """
    对话历史POJO类，用于记录langgraph的对话历史信息
    使用SQLAlchemy ORM映射到SQLite数据库
    """
    __tablename__ = 'conversation_history'
    
    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='消息ID')
    
    # 会话ID，关联到session表
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False, index=True, comment='会话ID')
    
    # 用户ID
    user_id = Column(Integer, nullable=False, index=True, comment='用户ID')
    
    # 消息类型：human(用户消息), ai(智能体回复), system(系统消息), tool(工具调用)
    message_type = Column(String(50), nullable=False, index=True, comment='消息类型')
    
    # 消息内容
    content = Column(Text, nullable=False, comment='消息内容')
    
    # langgraph状态信息，存储为JSON格式
    state_info = Column(JSON, comment='langgraph状态信息')
    
    # 元数据，存储其他附加信息
    metadata = Column(JSON, comment='元数据')
    
    # 消息时间戳
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True, comment='创建时间')
    
    # 更新时间戳
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 重试次数
    retry_times = Column(Integer, default=0, comment='重试次数')
    
    # 是否成功
    success = Column(Integer, default=1, comment='是否成功：1-成功，0-失败')
    
    # 错误信息
    error_message = Column(Text, comment='错误信息')
    
    # 消息顺序，用于保持对话顺序
    message_order = Column(Integer, default=0, comment='消息顺序')
    
    # 父消息ID，用于构建对话树
    parent_message_id = Column(Integer, ForeignKey('conversation_history.id'), comment='父消息ID')
    
    # 关系定义 - 使用字符串引用避免循环导入
    session = relationship("Session", back_populates="conversation_histories")
    parent_message = relationship("ConversationHistory", remote_side=[id])
    child_messages = relationship("ConversationHistory", back_populates="parent_message")
    
    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, session_id={self.session_id}, message_type='{self.message_type}', content='{self.content[:50]}...')>"
    
    def to_dict(self):
        """
        将对象转换为字典
        :return: 字典格式的对话历史数据
        """
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'message_type': self.message_type,
            'content': self.content,
            'state_info': self.state_info,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'retry_times': self.retry_times,
            'success': self.success,
            'error_message': self.error_message,
            'message_order': self.message_order,
            'parent_message_id': self.parent_message_id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建对象
        :param data: 字典数据
        :return: ConversationHistory对象
        """
        return cls(
            session_id=data.get('session_id'),
            user_id=data.get('user_id'),
            message_type=data.get('message_type'),
            content=data.get('content'),
            state_info=data.get('state_info'),
            metadata=data.get('metadata'),
            retry_times=data.get('retry_times', 0),
            success=data.get('success', 1),
            error_message=data.get('error_message'),
            message_order=data.get('message_order', 0),
            parent_message_id=data.get('parent_message_id')
        )