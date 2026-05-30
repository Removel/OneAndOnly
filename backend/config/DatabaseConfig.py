from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from backend.entity.pojo.Base import Base
import os

# 获取项目根目录（假设backend目录的父目录是项目根目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库配置 - SQLite文件将放在项目根目录下的database/backend文件夹中
DATABASE_DIR = os.path.join(PROJECT_ROOT, 'database', 'backend')
DATABASE_FILE = os.path.join(DATABASE_DIR, 'conversation.db')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATABASE_FILE}')

# 创建数据库引擎 - SQLite使用NullPool避免连接池问题
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite需要这个参数
    poolclass=NullPool,  # SQLite不需要连接池，使用NullPool
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    初始化数据库，创建所有表
    """
    # 确保数据目录存在
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print(f"创建数据目录: {DATABASE_DIR}")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print(f"数据库初始化完成: {DATABASE_FILE}")


def get_db():
    """
    获取数据库会话
    :return: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables():
    """
    删除所有表（谨慎使用）
    """
    Base.metadata.drop_all(bind=engine)
    print(f"已删除所有表: {DATABASE_FILE}")


def get_database_info():
    """
    获取数据库信息
    :return: 数据库信息字典
    """
    return {
        'database_file': DATABASE_FILE,
        'database_dir': DATABASE_DIR,
        'database_url': DATABASE_URL,
        'exists': os.path.exists(DATABASE_FILE),
        'size': os.path.getsize(DATABASE_FILE) if os.path.exists(DATABASE_FILE) else 0
    }