from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.entity.pojo.Base import Base
from backend.util.SnowflakeIdGenerator import generate_snowflake_id


class SessionPOJO(Base):
    """
    会话POJO类，用于管理对话会话
    """
    __tablename__ = 'session'
    
    # 主键ID，使用雪花算法生成，全局唯一
    id = Column(Integer, primary_key=True, default=generate_snowflake_id, comment='会话ID')
    
    # 会话状态：active(活跃), archived(归档), deleted(已删除)
    status = Column(String(50), default='active', comment='会话状态')
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment='创建时间')
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 最后活动时间
    last_activity_at = Column(DateTime, default=datetime.now, comment='最后活动时间')


    def __repr__(self):
        return f"<Session(id={self.id}, status='{self.status}')>"
    
    def to_dict(self):
        """
        将对象转换为字典
        :return: 字典格式的会话数据
        """
        return {
            'id': self.id,
            'status': self.status,
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
            id=data.get('id'),
            status=data.get('status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            last_activity_at=data.get('last_activity_at'),
        )