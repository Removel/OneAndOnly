import json
from typing import Dict, Any

from agent.graph.state import GlobalState
from agent.prompt.executor_prompt import executor_system_prompt
from agent.util import AgentFactory

def execute_node(state:GlobalState)->Dict[str, Any]:
    """
    执行计划节点，根据执行计划选择是否调用工具，执行计划任务
    """
    # 获取到当前对话核心信息
    plan = state["plan"]
    tools = state["tools"]

    # 创建agent实例
    agent = AgentFactory.create_role_agent(
        "executor",
        tools,
        system_prompt=executor_system_prompt.format(plan=plan),
        response_format=None,
    )

    # 执行计划
    result = agent.invoke({"input": "请执行计划"})

    # 更新状态
    response_text = ""
    
    messages = result.get("messages", [])
    if messages:
        # 从最后一条消息中提取内容
        last_message = messages[-1]
        message_content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
        
        try:
            parsed = json.loads(message_content)
            response_text = parsed.get("response_text", message_content)
        except (json.JSONDecodeError, ValueError):
            response_text = message_content
    
    if not response_text:
        response_text = str(result)
    
    return {
        "response_text": response_text
    }