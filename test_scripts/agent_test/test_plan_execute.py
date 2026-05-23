import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.plan_execute import plan_execute_node
from agent.graph.state import GlobalState
from agent.util.find_tools import find_tools
from langchain_core.messages import HumanMessage, AIMessage

def get_tool_by_name(tool_name, all_tools):
    """根据工具名称获取工具对象"""
    for tool in all_tools:
        if hasattr(tool, 'name') and tool.name == tool_name:
            return tool
    return None

def test_plan_execute():
    print("=== PlanExecute Node 测试脚本 ===")
    print("测试规划与执行合并节点的功能\n")
    
    all_tools = find_tools()
    print(f"发现 {len(all_tools)} 个可用工具: {[t.name for t in all_tools]}\n")
    
    test_cases = [
        {
            "name": "简单问候",
            "user_input": "你好",
            "messages": [HumanMessage(content="你好")],
            "memory": "",
            "tool_names": [],
            "description": "测试简单问候场景，无需复杂计划"
        },
        {
            "name": "询问天气",
            "user_input": "今天天气怎么样？",
            "messages": [HumanMessage(content="今天天气怎么样？")],
            "memory": "",
            "tool_names": [],
            "description": "测试需要调用工具的场景"
        },
        {
            "name": "复杂任务",
            "user_input": "帮我分析一下最近的销售数据并生成一份报告",
            "messages": [
                HumanMessage(content="我需要分析销售数据"),
                AIMessage(content="好的，我可以帮你分析。"),
                HumanMessage(content="帮我分析一下最近的销售数据并生成一份报告")
            ],
            "memory": "用户之前提到过需要分析销售数据",
            "tool_names": ["query_from_chromadb", "write_to_mds"],
            "description": "测试需要多步骤处理的场景"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print(f"可用工具名称: {test_case['tool_names']}")
        
        # 将工具名称转换为工具对象
        tools = []
        for tool_name in test_case['tool_names']:
            tool = get_tool_by_name(tool_name, all_tools)
            if tool:
                tools.append(tool)
                print(f"  ✓ 找到工具: {tool.name}")
            else:
                print(f"  ✗ 未找到工具: {tool_name}")
        
        print("-" * 60)
        
        try:
            state: GlobalState = {
                "messages": test_case["messages"],
                "user_input": test_case["user_input"],
                "response_text": "",
                "plan": "",
                "memory": test_case["memory"],
                "tools": tools,
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print("调用 plan_execute_node...")
            result = plan_execute_node(state)
            
            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")
            
            response_text = result.get('response_text', '')
            print(f"\n📝 回复文本:")
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")
            
            need_evaluate = result.get('need_evaluate', False)
            print(f"\n🔍 是否需要评估: {'是' if need_evaluate else '否'}")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 所有测试完成 ===")

def test_single_input():
    print("=== PlanExecute Node 单次输入测试 ===")
    print("可用工具:")
    all_tools = find_tools()
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description}")
    print("\n请输入测试内容（直接回车退出）：\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("> ")
            
            if not user_input.strip():
                print("退出测试。")
                break
            
            conversation_history.append(HumanMessage(content=user_input))
            
            tools_input = input("可用工具名称（逗号分隔，直接回车跳过）: ")
            tool_names = [t.strip() for t in tools_input.split(',')] if tools_input.strip() else []
            
            # 将工具名称转换为工具对象
            tools = []
            for tool_name in tool_names:
                tool = get_tool_by_name(tool_name, all_tools)
                if tool:
                    tools.append(tool)
                else:
                    print(f"警告：未找到工具 '{tool_name}'")
            
            state: GlobalState = {
                "messages": conversation_history.copy(),
                "user_input": user_input,
                "response_text": "",
                "plan": "",
                "memory": "",
                "tools": tools,
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print(f"\n正在处理: {user_input}")
            print(f"可用工具: {[t.name for t in tools]}")
            print("-" * 40)
            
            result = plan_execute_node(state)
            
            print(f"\n📝 回复文本:")
            response_text = result.get('response_text', '')
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")
            
            need_evaluate = result.get('need_evaluate', False)
            print(f"\n🔍 是否需要评估: {'是' if need_evaluate else '否'}")
            
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
    
    parser = argparse.ArgumentParser(description='PlanExecute Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='使用交互式输入模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_single_input()
    else:
        test_plan_execute()