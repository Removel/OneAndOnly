"""
测试数据库配置和初始化
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.DatabaseConfig import init_db, get_database_info, get_db
from backend.entity.pojo.Session import SessionPOJO


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
        session = SessionPOJO()
        db.add(session)
        db.commit()
        db.refresh(session)
        
        print(f"创建会话成功:")
        print(f"  会话ID: {session.id}")
        print(f"  会话状态: {session.status}")
        print(f"  创建时间: {session.created_at}")
        print(f"  更新时间: {session.updated_at}")
        print(f"  最后活动时间: {session.last_activity_at}")
        
        # 测试查询
        print("\n" + "=" * 50)
        print("测试查询...")
        print("=" * 50)
        
        # 查询会话
        found_session = db.query(SessionPOJO).filter_by(id=session.id).first()
        if found_session:
            print(f"查询到会话: ID={found_session.id}, 状态={found_session.status}")
        
        # 查询所有会话
        all_sessions = db.query(SessionPOJO).all()
        print(f"查询到 {len(all_sessions)} 个会话")
        
        # 查询活跃会话
        active_sessions = db.query(SessionPOJO).filter_by(status="active").all()
        print(f"查询到 {len(active_sessions)} 个活跃会话")
        
        # 测试更新会话
        print("\n" + "=" * 50)
        print("测试更新会话...")
        print("=" * 50)
        
        found_session.status = "archived"
        db.commit()
        db.refresh(found_session)
        print(f"更新会话状态成功: {found_session.status}")
        
        # 测试软删除会话
        print("\n" + "=" * 50)
        print("测试软删除会话...")
        print("=" * 50)
        
        found_session.status = "deleted"
        db.commit()
        db.refresh(found_session)
        print(f"软删除会话成功: {found_session.status}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
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