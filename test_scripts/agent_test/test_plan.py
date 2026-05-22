import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.plan import plan_node
from agent.graph.state import GlobalState
from langchain_core.messages import HumanMessage, AIMessage

def test_plan():
    print("=== Plan Node 测试脚本 ===")
    print("测试计划生成节点的功能\n")
    
    test_cases = [
        {
            "name": "简单问候",
            "user_input": "你好",
            "messages": [HumanMessage(content="你好")],
            "memory": "",
            "description": "测试简单问候场景，无需复杂计划"
        },
        {
            "name": "询问天气",
            "user_input": "今天天气怎么样？",
            "messages": [HumanMessage(content="今天天气怎么样？")],
            "memory": "",
            "description": "测试需要调用工具的场景"
        },
        {
            "name": "复杂任务规划",
            "user_input": "帮我分析一下最近的销售数据并生成一份报告",
            "messages": [
                HumanMessage(content="我需要分析销售数据"),
                AIMessage(content="好的，我可以帮你分析。"),
                HumanMessage(content="帮我分析一下最近的销售数据并生成一份报告")
            ],
            "memory": "用户之前提到过需要分析销售数据",
            "description": "测试需要多步骤计划的场景"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print("-" * 60)
        
        try:
            state: GlobalState = {
                "messages": test_case["messages"],
                "user_input": test_case["user_input"],
                "response_text": "",
                "plan": "",
                "memory": test_case["memory"],
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print("调用 plan_node...")
            result = plan_node(state)
            
            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")
            
            plan = result.get('plan', '')
            print(f"\n📋 生成的执行计划:")
            if plan:
                print(f"  {plan}")
            else:
                print(f"  无计划内容")
            
            need_evaluate = result.get('need_evaluate', False)
            print(f"\n🔍 是否需要评估: {'是' if need_evaluate else '否'}")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 所有测试完成 ===")

def test_single_input():
    print("=== Plan Node 单次输入测试 ===")
    print("请输入测试内容（直接回车退出）：\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("> ")
            
            if not user_input.strip():
                print("退出测试。")
                break
            
            conversation_history.append(HumanMessage(content=user_input))
            
            state: GlobalState = {
                "messages": conversation_history.copy(),
                "user_input": user_input,
                "response_text": "",
                "plan": "",
                "memory": "",
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "retry_times": 0,
                "error_message": None
            }
            
            print(f"\n正在处理: {user_input}")
            print("-" * 40)
            
            result = plan_node(state)
            
            print(f"\n📋 生成的执行计划:")
            plan = result.get('plan', '')
            if plan:
                print(f"  {plan}")
            else:
                print(f"  无计划内容")
            
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
    
    parser = argparse.ArgumentParser(description='Plan Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='使用交互式输入模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_single_input()
    else:
        test_plan()