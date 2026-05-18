"""
测试数据库配置和初始化
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.DatabaseConfig import init_db, get_database_info, get_db
from backend.entity.pojo.Session import Session
from backend.entity.pojo.ConversationHistory import ConversationHistory


def test_database():
    print("=" * 50)
    print("测试数据库配置")
    print("=" * 50)
    
    # 显示数据库信息
    db_info = get_database_info()
    print(f"\n数据库信息:")
    print(f"  数据库文件: {db_info['database_file']}")
    print(f"  数据库目录: {db_info['database_dir']}")
    print(f"  数据库URL: {db_info['database_url']}")
    print(f"  文件存在: {db_info['exists']}")
    print(f"  文件大小: {db_info['size']} 字节")
    
    # 初始化数据库
    print("\n" + "=" * 50)
    print("初始化数据库...")
    print("=" * 50)
    init_db()
    
    # 测试创建会话
    print("\n" + "=" * 50)
    print("测试创建会话...")
    print("=" * 50)
    db = next(get_db())
    
    try:
        # 创建测试会话
        session = Session(
            user_id=1,
            session_name="测试会话",
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        print(f"创建会话成功:")
        print(f"  会话ID: {session.id}")
        print(f"  用户ID: {session.user_id}")
        print(f"  会话名称: {session.session_name}")
        print(f"  状态: {session.status}")
        
        # 测试创建对话历史
        print("\n" + "=" * 50)
        print("测试创建对话历史...")
        print("=" * 50)
        
        history = ConversationHistory(
            session_id=session.id,
            user_id=1,
            message_type="human",
            content="你好，这是一个测试消息",
            message_order=1
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        
        print(f"创建对话历史成功:")
        print(f"  消息ID: {history.id}")
        print(f"  会话ID: {history.session_id}")
        print(f"  消息类型: {history.message_type}")
        print(f"  内容: {history.content}")
        
        # 测试查询
        print("\n" + "=" * 50)
        print("测试查询...")
        print("=" * 50)
        
        # 查询会话
        found_session = db.query(Session).filter_by(id=session.id).first()
        if found_session:
            print(f"查询到会话: {found_session.session_name}")
        
        # 查询对话历史
        found_history = db.query(ConversationHistory).filter_by(session_id=session.id).all()
        print(f"查询到 {len(found_history)} 条对话历史")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    # 显示最终数据库信息
    print("\n" + "=" * 50)
    print("最终数据库信息")
    print("=" * 50)
    final_db_info = get_database_info()
    print(f"  文件存在: {final_db_info['exists']}")
    print(f"  文件大小: {final_db_info['size']} 字节")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_database()