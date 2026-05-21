import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.execute import execute_node
from agent.graph.state import GlobalState
from agent.util.find_tools import find_tools
from langchain_core.messages import HumanMessage

def get_tool_by_name(tool_name, all_tools):
    """根据工具名称获取工具对象"""
    for tool in all_tools:
        if hasattr(tool, 'name') and tool.name == tool_name:
            return tool
    return None

def test_execute():
    print("=== Execute Node 测试脚本 ===")
    print("测试计划执行节点的功能\n")
    
    all_tools = find_tools()
    print(f"发现 {len(all_tools)} 个可用工具: {[t.name for t in all_tools]}\n")
    
    test_cases = [
        {
            "name": "简单任务执行",
            "plan": "步骤1：直接回答用户的问候",
            "tool_names": [],
            "description": "测试不需要工具的简单执行场景"
        },
        {
            "name": "需要工具的任务",
            "plan": "步骤1：使用find_from_mds工具查找相关文档",
            "tool_names": ["find_from_mds"],
            "description": "测试需要调用工具的执行场景"
        },
        {
            "name": "多步骤任务",
            "plan": "步骤1：查询销售数据->步骤2：分析数据趋势->步骤3：生成报告",
            "tool_names": ["query_from_chromadb", "write_to_mds"],
            "description": "测试多步骤执行计划"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"执行计划: {test_case['plan']}")
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
                "messages": [HumanMessage(content="测试消息")],
                "user_input": "测试输入",
                "response_text": "",
                "plan": test_case["plan"],
                "memory": "",
                "tools": tools,
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print("调用 execute_node...")
            result = execute_node(state)
            
            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")
            
            response_text = result.get('response_text', '')
            print(f"\n📝 执行结果:")
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 所有测试完成 ===")

def test_single_input():
    print("=== Execute Node 单次输入测试 ===")
    print("可用工具:")
    all_tools = find_tools()
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description}")
    print("\n请输入执行计划（直接回车退出）：\n")
    
    while True:
        try:
            plan_input = input("执行计划: ")
            
            if not plan_input.strip():
                print("退出测试。")
                break
            
            tools_input = input("可用工具名称（逗号分隔）: ")
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
                "messages": [HumanMessage(content="测试消息")],
                "user_input": "测试输入",
                "response_text": "",
                "plan": plan_input,
                "memory": "",
                "tools": tools,
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print(f"\n正在执行计划: {plan_input}")
            print(f"可用工具: {[t.name for t in tools]}")
            print("-" * 40)
            
            result = execute_node(state)
            
            print(f"\n📝 执行结果:")
            response_text = result.get('response_text', '')
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")
            
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
    
    parser = argparse.ArgumentParser(description='Execute Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='使用交互式输入模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_single_input()
    else:
        test_execute()