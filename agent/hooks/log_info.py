import logging

from langchain.agents.middleware import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    logger.info(f"[tool monitor]执行工具: {request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")
        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败, 原因: {str(e)}")
        raise e

@after_agent
def log_agent_output(state: AgentState, runtime: Runtime) -> dict | None:
    """
    在 Agent 执行完成后记录其最终输出。
    """
    # Agent 的最终输出通常是 state["messages"] 列表中的最后一条消息。
    # 这里假设输出是来自 AI 的消息。
    last_message = state["messages"][-1]
    logger.info(f"[Agent Finished] 最终输出: {last_message.content}")
    return None