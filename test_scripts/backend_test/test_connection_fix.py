import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.repository.SessionRepository import SessionRepository
from backend.service.SessionService import SessionService
import time

def test_connection_leak():
    """测试连接泄漏问题是否修复"""
    print("开始测试连接泄漏问题...")
    
    repository = SessionRepository()
    service = SessionService()
    
    # 模拟多次请求
    for i in range(20):
        try:
            print(f"第 {i+1} 次请求...")
            
            # 创建会话
            session = service.create_session()
            print(f"  创建会话成功: {session.id}")
            
            # 获取活跃会话
            active_sessions = service.get_active_sessions()
            print(f"  获取活跃会话成功: {len(active_sessions)} 个")
            
            # 获取单个会话
            retrieved_session = service.get_session_by_session_id(session.id)
            print(f"  获取会话详情成功: {retrieved_session.id}")
            
            # 更新会话
            service.update_session(session.id, {"status": "inactive"})
            print(f"  更新会话状态成功")
            
            # 删除会话
            service.delete_session(session.id)
            print(f"  删除会话成功")
            
        except Exception as e:
            print(f"  第 {i+1} 次请求失败: {str(e)}")
            break
    
    print("\n测试完成！如果所有20次请求都成功，说明连接泄漏问题已修复。")

if __name__ == "__main__":
    test_connection_leak()