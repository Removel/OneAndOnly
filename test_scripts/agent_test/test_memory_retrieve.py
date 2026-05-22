import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.memory_retrieve import memory_retrieve_node
from agent.graph.state import GlobalState
from langchain_core.messages import HumanMessage, AIMessage

def test_memory_retrieve():
    print("=== Memory Retrieve Node 测试脚本 ===")
    print("测试记忆检索节点的功能\n")
    
    # 创建测试状态
    test_cases = [
        {
            "name": "简单问候",
            "user_input": "你好",
            "messages": [HumanMessage(content="你好")],
            "description": "测试简单问候场景"
        },
        {
            "name": "询问个人信息",
            "user_input": "我叫什么名字？",
            "messages": [
                HumanMessage(content="我叫张三"),
                AIMessage(content="你好张三，很高兴认识你！"),
                HumanMessage(content="我叫什么名字？")
            ],
            "description": "测试需要查询记忆的场景"
        },
        {
            "name": "复杂对话",
            "user_input": "我昨天提到的那个项目怎么样了？",
            "messages": [
                HumanMessage(content="我昨天开始了一个新项目"),
                AIMessage(content="听起来很有趣，能告诉我更多关于这个项目的信息吗？"),
                HumanMessage(content="我昨天提到的那个项目怎么样了？")
            ],
            "description": "测试需要检索历史记忆的场景"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print("-" * 60)
        
        try:
            # 构建测试状态
            state: GlobalState = {
                "messages": test_case["messages"],
                "user_input": test_case["user_input"],
                "response_text": "",
                "plan": "",
                "memory": None,
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print("调用 memory_retrieve_node...")
            result = memory_retrieve_node(state)
            
            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")
            
            # 输出工具列表详细信息
            tools = result.get('tools', [])
            print(f"\n📋 记忆管理者识别的工具列表:")
            if tools:
                for i, tool in enumerate(tools, 1):
                    print(f"  {i}. {tool}")
            else:
                print(f"  无工具调用")
            
            # 输出记忆内容详细信息
            memory = result.get('memory', '')
            print(f"\n🧠 记忆管理者召回的记忆内容:")
            if memory:
                print(f"  {memory}")
            else:
                print(f"  无记忆内容")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 所有测试完成 ===")

def test_single_input():
    """单次输入测试模式"""
    print("=== Memory Retrieve Node 单次输入测试 ===")
    print("请输入测试内容（直接回车退出）：\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("> ")
            
            if not user_input.strip():
                print("退出测试。")
                break
            
            # 添加用户消息到历史
            conversation_history.append(HumanMessage(content=user_input))
            
            # 构建测试状态
            state: GlobalState = {
                "messages": conversation_history.copy(),
                "user_input": user_input,
                "response_text": "",
                "plan": "",
                "memory": None,
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print(f"\n正在处理: {user_input}")
            print("-" * 40)
            
            result = memory_retrieve_node(state)
            
            # 输出详细的对话结果
            print(f"\n📋 记忆管理者识别的工具列表:")
            tools = result.get('tools', [])
            if tools:
                for i, tool in enumerate(tools, 1):
                    print(f"  {i}. {tool}")
            else:
                print(f"  无工具调用")
            
            print(f"\n🧠 记忆管理者召回的记忆内容:")
            memory = result.get('memory', '')
            if memory:
                print(f"  {memory}")
            else:
                print(f"  无记忆内容")
            
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n用户中断，退出测试。")
            break
        except Exception as e:
            print(f"\n处理过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Retrieve Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='使用交互式输入模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_single_input()
    else:
        test_memory_retrieve()