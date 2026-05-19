from typing import Dict, Any
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.executor_prompt import executor_system_prompt
from agent.util import AgentFactory

class ExecuteResult(BaseModel):
    response_text: str = Field(description="executor执行计划后的响应")

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
        system_prompt=executor_system_prompt,
        response_format=ExecuteResult,
    )

    # 执行计划
    result = agent.invoke({
        "input": f"你的任务是：{plan}"
    })

    # 更新状态
    return {
        "response_text": result.get("response_text",""),
    }