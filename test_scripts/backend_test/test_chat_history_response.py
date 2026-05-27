import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.entity.response.MessageResponse import MessageResponse
from backend.entity.response.ChatHistoryResponse import ChatHistoryResponse


def test_message_response():
    print("测试 MessageResponse 类...")
    
    test_dict = {
        "type": "HumanMessage",
        "content": "你好，这是一个测试消息",
        "id": "msg_001",
        "additional_kwargs": {"key": "value"},
        "response_metadata": {"model": "gpt-4"}
    }
    
    message = MessageResponse.from_dict(test_dict)
    
    assert message.role == "user", f"期望 role 为 'user'，实际为 '{message.role}'"
    assert message.content == "你好，这是一个测试消息", f"内容不匹配"
    assert message.message_id == "msg_001", f"消息ID不匹配"
    
    print(f"✓ MessageResponse 测试通过")
    print(f"  - role: {message.role}")
    print(f"  - content: {message.content}")
    print(f"  - message_id: {message.message_id}")
    
    ai_test_dict = {
        "type": "AIMessage",
        "content": "你好！我是AI助手",
        "id": "msg_002"
    }
    
    ai_message = MessageResponse.from_dict(ai_test_dict)
    assert ai_message.role == "assistant", f"期望 role 为 'assistant'，实际为 '{ai_message.role}'"
    print(f"✓ AIMessage 角色映射测试通过: {ai_message.role}")


def test_chat_history_response():
    print("\n测试 ChatHistoryResponse 类...")
    
    test_messages = [
        {
            "type": "HumanMessage",
            "content": "第一个问题",
            "id": "msg_001"
        },
        {
            "type": "AIMessage",
            "content": "第一个回答",
            "id": "msg_002"
        },
        {
            "type": "HumanMessage",
            "content": "第二个问题",
            "id": "msg_003"
        }
    ]
    
    history = ChatHistoryResponse.from_data(session_id=123, messages=test_messages)
    
    assert history.session_id == 123, f"期望 session_id 为 123，实际为 {history.session_id}"
    assert history.total_count == 3, f"期望 total_count 为 3，实际为 {history.total_count}"
    assert len(history.messages) == 3, f"期望消息数量为 3，实际为 {len(history.messages)}"
    
    assert history.messages[0].role == "user", "第一条消息应该是 user"
    assert history.messages[1].role == "assistant", "第二条消息应该是 assistant"
    assert history.messages[2].role == "user", "第三条消息应该是 user"
    
    print(f"✓ ChatHistoryResponse 测试通过")
    print(f"  - session_id: {history.session_id}")
    print(f"  - total_count: {history.total_count}")
    print(f"  - 消息列表:")
    for i, msg in enumerate(history.messages):
        print(f"    {i+1}. [{msg.role}] {msg.content}")


def test_empty_history():
    print("\n测试空历史记录...")
    
    history = ChatHistoryResponse.from_data(session_id=456, messages=[])
    
    assert history.session_id == 456
    assert history.total_count == 0
    assert len(history.messages) == 0
    
    print(f"✓ 空历史记录测试通过")


if __name__ == "__main__":
    try:
        test_message_response()
        test_chat_history_response()
        test_empty_history()
        print("\n" + "="*50)
        print("所有测试通过！✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)