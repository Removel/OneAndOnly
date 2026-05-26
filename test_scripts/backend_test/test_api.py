"""
测试后端API接口
"""
import sys
import os
import time
import requests
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URL = "http://localhost:8000"


def test_api_connection():
    """测试API连接"""
    print("=" * 50)
    print("测试API连接")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"根路径响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("无法连接到API服务器，请确保后端服务已启动")
        return False
    except Exception as e:
        print(f"连接错误: {str(e)}")
        return False


def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 50)
    print("测试健康检查接口")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"健康检查响应: {response.status_code}")
        print(f"响应内容: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {str(e)}")
        return False


def test_session_api():
    """测试会话相关API"""
    print("\n" + "=" * 50)
    print("测试会话API")
    print("=" * 50)
    
    session_id = None
    
    try:
        # 1. 创建会话
        print("\n1. 创建会话 (POST /api/session/)")
        response = requests.post(f"{BASE_URL}/api/session/", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200 and result.get("data"):
            session_id = result["data"]["id"]
            print(f"创建会话成功，会话ID: {session_id}")
        else:
            print(f"创建会话失败: {result.get('msg', '未知错误')}")
            return False
        
        # 2. 获取所有会话
        print("\n2. 获取所有会话 (GET /api/session/)")
        response = requests.get(f"{BASE_URL}/api/session/", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200:
            sessions = result.get("data", [])
            print(f"获取到 {len(sessions)} 个会话")
        else:
            print(f"获取所有会话失败: {result.get('msg', '未知错误')}")
        
        # 3. 获取活跃会话
        print("\n3. 获取活跃会话 (GET /api/session/active)")
        response = requests.get(f"{BASE_URL}/api/session/active", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200:
            active_sessions = result.get("data", [])
            print(f"获取到 {len(active_sessions)} 个活跃会话")
        else:
            print(f"获取活跃会话失败: {result.get('msg', '未知错误')}")
        
        # 4. 获取单个会话
        print(f"\n4. 获取单个会话 (GET /api/session/{session_id})")
        response = requests.get(f"{BASE_URL}/api/session/{session_id}", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200 and result.get("data"):
            session_data = result["data"]
            print(f"获取会话成功，状态: {session_data.get('status')}")
        else:
            print(f"获取单个会话失败: {result.get('msg', '未知错误')}")
        
        # 5. 更新会话状态
        print(f"\n5. 更新会话状态 (PUT /api/session/{session_id})")
        update_data = {
            "status": "archived"
        }
        response = requests.put(
            f"{BASE_URL}/api/session/{session_id}",
            json=update_data,
            timeout=10
        )
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200 and result.get("data"):
            print(f"更新会话状态成功，新状态: {result['data'].get('status')}")
        else:
            print(f"更新会话状态失败: {result.get('msg', '未知错误')}")
        
        # 6. 删除会话
        print(f"\n6. 删除会话 (DELETE /api/session/{session_id})")
        response = requests.delete(f"{BASE_URL}/api/session/{session_id}", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200:
            print(f"删除会话成功")
        else:
            print(f"删除会话失败: {result.get('msg', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f"会话API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_api():
    """测试聊天相关API"""
    print("\n" + "=" * 50)
    print("测试聊天API")
    print("=" * 50)
    
    session_id = None
    
    try:
        # 首先创建一个会话用于聊天测试
        print("\n创建测试会话...")
        response = requests.post(f"{BASE_URL}/api/session/", timeout=10)
        result = response.json()
        
        if result.get("code") == 200 and result.get("data"):
            session_id = result["data"]["id"]
            print(f"测试会话创建成功，会话ID: {session_id}")
        else:
            print(f"创建测试会话失败，跳过聊天API测试")
            return False
        
        # 1. 发送聊天消息
        print(f"\n1. 发送聊天消息 (POST /api/chat)")
        chat_data = {
            "human_input": "你好，这是一个测试消息",
            "session_id": session_id,
            "clear_history": False
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            timeout=30
        )
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200 and result.get("data"):
            chat_response = result["data"]
            print(f"聊天响应成功")
            print(f"  回复内容: {chat_response.get('response', '')[:100]}...")
            print(f"  成功状态: {chat_response.get('success')}")
            print(f"  重试次数: {chat_response.get('retry_times')}")
        else:
            print(f"发送聊天消息失败: {result.get('msg', '未知错误')}")
            if result.get("data") and result["data"].get("error_message"):
                print(f"  错误详情: {result['data']['error_message']}")
        
        # 2. 获取对话历史
        print(f"\n2. 获取对话历史 (GET /api/session/{session_id}/history)")
        response = requests.get(f"{BASE_URL}/api/session/{session_id}/history", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200:
            history = result.get("data", [])
            print(f"获取到 {len(history)} 条对话历史")
            if history:
                first_message = history[0]
                print(f"  第一条消息类型: {first_message.get('type')}")
                print(f"  第一条消息内容: {first_message.get('content', '')[:50]}...")
        else:
            print(f"获取对话历史失败: {result.get('msg', '未知错误')}")
        
        # 3. 清空对话历史
        print(f"\n3. 清空对话历史 (DELETE /api/session/{session_id}/history)")
        response = requests.delete(f"{BASE_URL}/api/session/{session_id}/history", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        if result.get("code") == 200:
            print(f"清空对话历史成功")
        else:
            print(f"清空对话历史失败: {result.get('msg', '未知错误')}")
        
        # 4. 验证历史已清空
        print(f"\n4. 验证历史已清空")
        response = requests.get(f"{BASE_URL}/api/session/{session_id}/history", timeout=10)
        result = response.json()
        
        if result.get("code") == 200:
            history = result.get("data", [])
            print(f"清空后对话历史数量: {len(history)}")
        
        return True
        
    except Exception as e:
        print(f"聊天API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 50)
    print("测试错误处理")
    print("=" * 50)
    
    try:
        # 1. 测试获取不存在的会话
        print("\n1. 测试获取不存在的会话 (GET /api/session/99999)")
        response = requests.get(f"{BASE_URL}/api/session/99999", timeout=10)
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        # 2. 测试发送空消息
        print("\n2. 测试发送空消息 (POST /api/chat)")
        chat_data = {
            "human_input": "",
            "session_id": 1,
            "clear_history": False
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            timeout=10
        )
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        # 3. 测试使用无效的会话ID
        print("\n3. 测试使用无效的会话ID (POST /api/chat)")
        chat_data = {
            "human_input": "测试消息",
            "session_id": -1,
            "clear_history": False
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            timeout=10
        )
        print(f"响应状态码: {response.status_code}")
        result = response.json()
        print(f"响应内容: {result}")
        
        return True
        
    except Exception as e:
        print(f"错误处理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("*" * 50)
    print("开始后端API测试")
    print("*" * 50)
    
    # 测试API连接
    if not test_api_connection():
        print("\n无法连接到API服务器，请确保后端服务已启动:")
        print("  python backend/main.py")
        print("或")
        print("  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # 测试健康检查
    test_health_check()
    
    # 测试会话API
    test_session_api()
    
    # 测试聊天API
    test_chat_api()
    
    # 测试错误处理
    test_error_handling()
    
    print("\n")
    print("*" * 50)
    print("所有测试完成")
    print("*" * 50)


if __name__ == "__main__":
    run_all_tests()