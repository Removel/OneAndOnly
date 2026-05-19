import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.main import chat_with_agent

def test_agent():
    print("=== Agent 测试脚本 ===")
    print("请输入您想对 Agent 说的话：")
    
    try:
        user_input = input("> ")
        
        if not user_input.strip():
            print("输入不能为空，退出测试。")
            return
        
        print(f"\n正在处理您的输入: {user_input}")
        print("-" * 50)
        
        result = chat_with_agent(
            user_input=user_input,
            conversation_history=None,
            clear_history=True
        )
        
        print("\n=== 测试结果 ===")
        print(f"成功状态: {result.get('success', False)}")
        print(f"响应内容: {result.get('response_text', '')}")
        print(f"情感状态: {result.get('emotion_vac', {})}")
        print(f"重试次数: {result.get('retry_times', 0)}")
        
        if result.get('error_message'):
            print(f"错误信息: {result.get('error_message')}")
        
        print("-" * 50)
        print("测试完成，退出程序。")
        
    except KeyboardInterrupt:
        print("\n\n用户中断，退出测试。")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()