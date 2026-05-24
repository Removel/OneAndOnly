from langchain.agents.middleware import *


@wrap_tool_call()
def log_tool_calls(request, handler):
    """
    记录工具调用的包装器。

    Args:
        request: 包含工具调用信息的对象，属性有：
            - tool_name: 工具名称
            - tool_args: 参数字典
            - tool_call_id: 调用 ID
        handler: 真正的工具执行函数，接受 request 并返回结果
    """
    print("可用属性:", [attr for attr in dir(request) if not attr.startswith("_")])
    tool_name = request.tool
    tool_args = request.tool_call

    # 调用前日志
    print(f"[Tool Call] {tool_name} 被调用，参数: {tool_args}")

    # 执行工具
    result = handler(request)

    # 调用后日志
    print(f"[Tool Result] {tool_name} 返回: {result}")

    return result

@after_agent
def log_agent_output(state: AgentState, runtime: Runtime) -> dict | None:
    """
    在 Agent 执行完成后记录其最终输出。
    """
    # Agent 的最终输出通常是 state["messages"] 列表中的最后一条消息。
    # 这里假设输出是来自 AI 的消息。
    last_message = state["messages"][-1]
    print(f"[Agent Finished] 最终输出: {last_message.content}")
    return None