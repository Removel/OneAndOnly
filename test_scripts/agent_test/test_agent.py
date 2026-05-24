import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.main import chat_with_agent, get_conversation_history, clear_conversation_history

def test_agent():
    print("=== Agent 交互式测试脚本 ===")
    print("输入多轮对话，使用 session_id 保持会话连续性")
    print("特殊命令:")
    print("  /new <session_id> - 切换到新的会话ID")
    print("  /clear - 清空当前会话历史")
    print("  /history - 查看当前会话历史")
    print("  /quit 或 /exit - 退出程序")
    print("-" * 50)
    
    try:
        # 初始化会话ID
        session_id = "interactive_session_001"
        print(f"默认会话ID: {session_id}")
        
        while True:
            print(f"\n[{session_id}] 用户输入: ", end="")
            user_input = input().strip()
            
            if user_input.lower() in ['/quit', '/exit']:
                print("退出测试程序。")
                break
            
            elif user_input == '/clear':
                print("正在清空会话历史...")
                clear_conversation_history(session_id)
                history_after_clear = get_conversation_history(session_id)
                print(f"✓ 会话历史已清空 (清空后历史长度: {len(history_after_clear)})")
                continue
            
            elif user_input == '/history':
                print("正在获取会话历史...")
                history = get_conversation_history(session_id)
                print(f"当前会话历史长度: {len(history)} 条消息")
                for i, msg in enumerate(history):
                    print(f"  消息 {i+1}: {type(msg).__name__} - {str(msg)[:100]}...")
                continue
            
            elif user_input.startswith('/new '):
                parts = user_input.split(' ', 1)
                if len(parts) > 1:
                    new_session_id = parts[1].strip()
                    if new_session_id:
                        # 检查当前会话历史
                        current_history = get_conversation_history(session_id)
                        print(f"切换前 - 会话 '{session_id}' 历史长度: {len(current_history)}")
                        
                        session_id = new_session_id
                        print(f"✓ 已切换到新会话ID: {session_id}")
                        
                        # 检查新会话历史
                        new_history = get_conversation_history(session_id)
                        print(f"切换后 - 会话 '{session_id}' 历史长度: {len(new_history)}")
                    else:
                        print("错误: 请提供有效的会话ID")
                else:
                    print("错误: 请提供会话ID，格式: /new <session_id>")
                continue
            
            elif user_input == '':
                print("请输入有效内容或命令。")
                continue
            
            # 正常对话处理
            print(f"正在发送消息到会话 '{session_id}'...")
            start_time = time.time()
            result = chat_with_agent(
                user_input=user_input,
                session_id=session_id
            )
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                print(f"AI回复: {result.get('response_text', '无回复内容')}")
                print(f"耗时: {elapsed_time:.2f}秒")
            else:
                print(f"❌ 请求失败: {result.get('error_message', '未知错误')}")
                
    except KeyboardInterrupt:
        print("\n\n用户中断，退出测试。")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()