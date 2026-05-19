from typing import Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.memory_manager_prompt import memory_manager_system_prompt_find
from agent.util import AgentFactory
from agent.util.find_tools import find_tools, all_tools


class MemoryRetrieveResult(BaseModel):
    tools: list[str] = Field(description="executor可能调用的工具名称列表")
    memory: str = Field(description="召回记忆内容")

def memory_retrieve_node(state: GlobalState) -> Dict[str, Any]:
    """
    从外挂知识库当中获取相关对话需要的相关信息
    """
    # 获取到当前对话核心信息
    user_input = state["user_input"]
    messages = state["messages"]

    # 创建agent实例
    memory_manager = AgentFactory.create_role_agent(
        "memory_manager",
        all_tools,
        memory_manager_system_prompt_find,
        MemoryRetrieveResult,
    )

    # 构建提示词模板
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("messages"),
        ("human", "{input}")
    ])

    # 执行agent任务
    json_response = memory_manager.invoke({
        "messages": messages,
        "input": user_input
    })

    # 解析agent任务结果
    executor_tools = json_response.get("tools", [])
    memory = json_response.get("memory", "")

    # 更新状态
    return {
        "tools": executor_tools,
        "memory": memory,
    }