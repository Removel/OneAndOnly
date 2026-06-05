import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph.node.styled_output import styled_output_node
from agent.graph.state import GlobalState
from langchain_core.messages import HumanMessage

def test_styled_output():
    print("=== Styled Output Node 测试脚本 ===")
    print("测试最终输出节点的功能\n")
    
    test_cases = [
        {
            "name": "正常响应",
            "response_text": "你好！很高兴为你服务。",
            "user_input": "你好",
            "retry_times": 0,
            "description": "测试正常响应的总结输出"
        },
        {
            "name": "工具执行结果",
            "response_text": "已按计划执行步骤1，使用find_from_mds工具查找相关文档。查询结果：相关文档内容",
            "user_input": "帮我查找相关文档",
            "retry_times": 1,
            "description": "测试工具执行结果的总结输出"
        },
        {
            "name": "错误响应（重试3次）",
            "response_text": "执行失败：无法连接到数据库，请稍后重试",
            "user_input": "查询销售数据",
            "retry_times": 3,
            "description": "测试重试多次后的错误响应总结"
        },
        {
            "name": "复杂任务结果",
            "response_text": "已完成以下任务：1. 查询销售数据成功；2. 分析了数据趋势；3. 生成了报告并保存到文档系统",
            "user_input": "帮我分析销售数据并生成报告",
            "retry_times": 0,
            "description": "测试复杂任务的总结输出"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print(f"执行结果: {test_case['response_text']}")
        print(f"重试次数: {test_case['retry_times']}")
        print("-" * 60)
        
        try:
            state: GlobalState = {
                "messages": [HumanMessage(content=test_case["user_input"])],
                "user_input": test_case["user_input"],
                "response_text": test_case["response_text"],
                "plan": "",
                "memory": "",
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "need_continue": False,
                "retry_times": test_case["retry_times"],
                "error_message": None
            }

            print("调用 styled_output_node（风格模式）...")
            result = styled_output_node(state)

            print("\n=== 测试结果 ===")
            print(f"✓ 节点执行成功")

            response_text = result.get('response_text', '')
            print(f"\n📝 总结响应:")
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")

            need_continue = result.get('need_continue', None)
            if need_continue is not None:
                print(f"\n🔀 need_continue: {need_continue}")
            
            emotion_vac = result.get('emotion_vac', {})
            print(f"\n🎭 情绪VAC:")
            if emotion_vac:
                print(f"  Valence (效价): {emotion_vac.get('valence', 'N/A')}")
                print(f"  Arousal (唤醒度): {emotion_vac.get('arousal', 'N/A')}")
                print(f"  Control (控制度): {emotion_vac.get('control', 'N/A')}")
            else:
                print(f"  无情绪数据")
            
            messages = result.get('messages')
            if messages:
                print(f"\n💬 消息内容:")
                print(f"  {messages.content}")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60 + "\n")
    
    print("=== 风格模式测试完成 ===\n")


def test_gate_mode():
    print("=== Styled Output Node 门控模式测试 ===")
    print("测试门控模式的判断功能（response_text 为空）\n")

    gate_test_cases = [
        {
            "name": "简单问候",
            "user_input": "你好！",
            "description": "简单问候应判断为无需继续，直接回复"
        },
        {
            "name": "简单日常",
            "user_input": "今天天气真好",
            "description": "日常对话应判断为无需继续，直接回复"
        },
        {
            "name": "复杂查询",
            "user_input": "帮我查一下数据库里最近的销售数据，分析趋势并生成报告",
            "description": "复杂任务应判断为需要继续到 plan_execute"
        },
    ]

    for i, test_case in enumerate(gate_test_cases, 1):
        print(f"门控测试用例 {i}: {test_case['name']}")
        print(f"描述: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print("-" * 60)

        try:
            state: GlobalState = {
                "messages": [HumanMessage(content=test_case["user_input"])],
                "user_input": test_case["user_input"],
                "response_text": "",
                "plan": "",
                "memory": "",
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "need_continue": True,
                "retry_times": 0,
                "error_message": None
            }

            print("调用 styled_output_node（门控模式）...")
            result = styled_output_node(state)

            print("\n=== 门控结果 ===")
            need_continue = result.get('need_continue', None)
            print(f"🔀 need_continue: {need_continue}")

            response_text = result.get('response_text', '')
            if response_text:
                print(f"📝 直接回复: {response_text[:200]}..." if len(response_text) > 200 else f"📝 直接回复: {response_text}")

            emotion_vac = result.get('emotion_vac', {})
            if emotion_vac:
                print(f"🎭 情绪VAC: {emotion_vac}")

            if need_continue is True and not response_text:
                print("✓ 正确：复杂问题标记为需要继续处理，无直接回复")

        except Exception as e:
            print(f"\n✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60 + "\n")

    print("=== 门控模式测试完成 ===")

def test_single_input():
    print("=== Styled Output Node 单次输入测试 ===")
    print("请输入测试内容（直接回车退出）：\n")
    
    while True:
        try:
            response_input = input("执行结果: ")
            
            if not response_input.strip():
                print("退出测试。")
                break
            
            user_input = input("用户输入: ")
            retry_times_input = input("重试次数（默认0）: ")
            retry_times = int(retry_times_input) if retry_times_input.strip() else 0
            
            state: GlobalState = {
                "messages": [HumanMessage(content=user_input)],
                "user_input": user_input,
                "response_text": response_input,
                "plan": "",
                "memory": "",
                "tools": [],
                "emotion_vac": {},
                "need_evaluate": False,
                "need_continue": False,
                "retry_times": retry_times,
                "error_message": None
            }
            
            print(f"\n执行结果: {response_input}")
            print(f"用户输入: {user_input}")
            print(f"重试次数: {retry_times}")
            print("-" * 40)
            
            result = styled_output_node(state)
            
            print(f"\n📝 总结响应:")
            response_text = result.get('response_text', '')
            if response_text:
                print(f"  {response_text}")
            else:
                print(f"  无响应内容")
            
            emotion_vac = result.get('emotion_vac', {})
            print(f"\n🎭 情绪VAC:")
            if emotion_vac:
                print(f"  Valence (效价): {emotion_vac.get('valence', 'N/A')}")
                print(f"  Arousal (唤醒度): {emotion_vac.get('arousal', 'N/A')}")
                print(f"  Control (控制度): {emotion_vac.get('control', 'N/A')}")
            else:
                print(f"  无情绪数据")
            
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n用户中断，退出测试。")
            break
        except ValueError:
            print("请输入有效的重试次数（数字）")
        except Exception as e:
            print(f"\n处理过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Styled Output Node 测试脚本')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='使用交互式输入模式')
    parser.add_argument('--gate', '-g', action='store_true',
                       help='运行门控模式测试')

    args = parser.parse_args()

    if args.interactive:
        test_single_input()
    elif args.gate:
        test_gate_mode()
    else:
        test_styled_output()
        test_gate_mode()