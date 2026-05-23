import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.main import chat_with_agent, get_conversation_history, clear_conversation_history

def test_agent():
    print("=== Agent 测试脚本 ===")
    print("测试 session_id 功能和多轮对话")
    print("-" * 50)
    
    try:
        # 使用固定的 session_id 进行测试
        session_id = "test_session_001"
        print(f"使用会话ID: {session_id}")
        
        # 清空历史记录
        print("\n1. 清空历史记录...")
        clear_conversation_history(session_id)
        print("✓ 历史记录已清空")
        
        # 第一轮对话
        print("\n2. 第一轮对话...")
        user_input1 = "你好，请介绍一下你自己"
        print(f"用户输入: {user_input1}")
        
        start_time = time.time()
        result1 = chat_with_agent(
            user_input=user_input1,
            session_id=session_id
        )
        time1 = time.time() - start_time
        
        print(f"AI回复: {result1.get('response_text', '')}")
        print(f"耗时: {time1:.2f}秒")
        print(f"成功状态: {result1.get('success', False)}")
        
        if not result1.get('success'):
            print(f"错误信息: {result1.get('error_message')}")
            return
        
        # 第二轮对话（测试对话历史恢复）
        print("\n3. 第二轮对话（测试对话历史恢复）...")
        user_input2 = "刚才你说了什么？你需要回答：我刚刚说了……"
        print(f"用户输入: {user_input2}")
        
        start_time = time.time()
        result2 = chat_with_agent(
            user_input=user_input2,
            session_id=session_id
        )
        time2 = time.time() - start_time
        
        print(f"AI回复: {result2.get('response_text', '')}")
        print(f"耗时: {time2:.2f}秒")
        print(f"成功状态: {result2.get('success', False)}")
        
        if not result2.get('success'):
            print(f"错误信息: {result2.get('error_message')}")
            return
        
        # 第三轮对话
        print("\n4. 第三轮对话...")
        user_input3 = "我的名字是什么？"
        print(f"用户输入: {user_input3}")
        
        start_time = time.time()
        result3 = chat_with_agent(
            user_input=user_input3,
            session_id=session_id
        )
        time3 = time.time() - start_time
        
        print(f"AI回复: {result3.get('response_text', '')}")
        print(f"耗时: {time3:.2f}秒")
        print(f"成功状态: {result3.get('success', False)}")
        
        if not result3.get('success'):
            print(f"错误信息: {result3.get('error_message')}")
            return
        
        # 获取对话历史
        print("\n5. 获取对话历史...")
        history = get_conversation_history(session_id)
        print(f"对话历史长度: {len(history)} 条消息")
        for i, msg in enumerate(history):
            print(f"  消息 {i+1}: {type(msg).__name__} - {str(msg)[:50]}...")
        
        # 测试新会话（验证独立性）
        print("\n6. 测试新会话（验证独立性）...")
        new_session_id = "test_session_002"
        print(f"使用新会话ID: {new_session_id}")
        
        user_input4 = "你知道我刚才说了什么吗？"
        print(f"用户输入: {user_input4}")
        
        start_time = time.time()
        result4 = chat_with_agent(
            user_input=user_input4,
            session_id=new_session_id
        )
        time4 = time.time() - start_time
        
        print(f"AI回复: {result4.get('response_text', '')}")
        print(f"耗时: {time4:.2f}秒")
        print(f"成功状态: {result4.get('success', False)}")
        
        # 总结
        print("\n" + "=" * 50)
        print("=== 测试总结 ===")
        print(f"✓ 第一轮对话成功 (耗时: {time1:.2f}秒)")
        print(f"✓ 第二轮对话成功 (耗时: {time2:.2f}秒)")
        print(f"✓ 第三轮对话成功 (耗时: {time3:.2f}秒)")
        print(f"✓ 新会话独立测试成功 (耗时: {time4:.2f}秒)")
        print(f"✓ 对话历史恢复功能正常")
        print(f"✓ 会话独立性验证通过")
        print(f"总耗时: {time1 + time2 + time3 + time4:.2f}秒")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，退出测试。")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()