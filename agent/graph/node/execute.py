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
    agent = AgentFactory.create_agent("executor",tools,executor_system_prompt.format(plan=plan))

    # 执行计划
    response = agent.invoke(plan)
    
    # 更新状态
    return {
        "response_text": response.content,
    }
