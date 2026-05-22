import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.evaluate import evaluate_node
from agent.graph.state import GlobalState
from langchain_core.messages import HumanMessage

def test_evaluate():
    print("=== Evaluate Node 测试脚本 ===")
    print("测试评估节点的功能\n")
    
    test_cases = [
        {
            "name": "成功执行",
            "plan": "步骤1：回答用户的问候",
            "response_text": "你好！很高兴为你服务。",
            "user_input": "你好",
            "memory": "",
            "retry_times": 0,
            "description": "测试执行成功不需要重试的场景"
        },
        {
            "name": "执行失败需要重试",
            "plan": "步骤1：调用工具查询天气",
            "response_text": "工具调用失败，请重试",
            "user_input": "今天天气怎么样？",
            "memory": "",
            "retry_times": 0,
            "description": "测试执行失败需要重试的场景"
        },
        {
            "name": "部分成功",
            "plan": "步骤1：分析销售数据->步骤2：生成报告",
            "response_text": "数据已分析，但报告生成部分有问题",
            "user_input": "帮我分析销售数据并生成报告",
            "memory": "用户需要详细的销售报告",
            "retry_times": 1,
            "description": "测试部分成功需要评估的场景"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"执行计划: {test_case['plan']}")
        print(f"执行结果: {test_case['response_text']}")
        print("-" * 60)
        
        try:
            state: GlobalState = {
                "messages": [HumanMessage(content=test_case["user_input"])],
                "user_input": test_case["user_input"],
                "response_text": test_case["response_text"],
                "plan": test_case["plan"],
                "memory": test_case["memory"],
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": True,
                "retry_times": test_case["retry_times"],
                "error_message": None
            }
            
            print("调用 evaluate_node...")
            result = evaluate_node(state)
            
            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")
            
            need_evaluate = result.get('need_evaluate', False)
            print(f"\n🔍 是否需要重试: {'是' if need_evaluate else '否'}")
            
            error_message = result.get('error_message', '')
            if error_message:
                print(f"\n❌ 错误信息: {error_message}")
            
            retry_times = result.get('retry_times', test_case["retry_times"])
            if retry_times > test_case["retry_times"]:
                print(f"\n🔄 重试次数: {retry_times}")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 所有测试完成 ===")

def test_single_input():
    print("=== Evaluate Node 单次输入测试 ===")
    print("请输入测试内容（直接回车退出）：\n")
    
    while True:
        try:
            plan_input = input("执行计划: ")
            if not plan_input.strip():
                print("退出测试。")
                break
            
            response_input = input("执行结果: ")
            user_input = input("用户输入: ")
            
            state: GlobalState = {
                "messages": [HumanMessage(content=user_input)],
                "user_input": user_input,
                "response_text": response_input,
                "plan": plan_input,
                "memory": "",
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": True,
                "retry_times": 0,
                "error_message": None
            }
            
            print(f"\n执行计划: {plan_input}")
            print(f"执行结果: {response_input}")
            print("-" * 40)
            
            result = evaluate_node(state)
            
            print(f"\n🔍 是否需要重试: {'是' if result.get('need_evaluate', False) else '否'}")
            
            error_message = result.get('error_message', '')
            if error_message:
                print(f"\n❌ 错误信息: {error_message}")
            
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
    
    parser = argparse.ArgumentParser(description='Evaluate Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='使用交互式输入模式')
    
    args = parser.parse_args()
    
    if args.interactive:
        test_single_input()
    else:
        test_evaluate()