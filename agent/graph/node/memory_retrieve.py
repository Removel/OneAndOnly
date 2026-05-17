from typing import Dict, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.graph.state import GlobalState
from agent.prompt.memory_manager_prompt import (
    memory_manager_system_prompt_find,
)
from agent.util import AgentFactory
from agent.util.find_tools import find_tools


def memory_retrieve_node(state: GlobalState) -> Dict[str, Any]:
    """
    从外挂知识库当中获取相关对话需要的相关信息
    """
    # 获取到当前对话核心信息
    user_input = state["user_input"]
    messages = state["messages"]

    # 获取到当前支持的tools工具列表
    tools = find_tools()

    # 创建agent实例
    memory_manager = AgentFactory.create_agent(
        "memory_manager",
        tools,
        memory_manager_system_prompt_find.format(user_input=user_input)
    )

    # 构建提示词模板
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{user_input}"),
    ])

    # 创建链式调用
    chain = prompt | memory_manager | JsonOutputParser()
    
    # 执行agent任务
    json_response = chain.invoke({
        "messages": messages,
        "user_input": user_input
    })
    
    # 解析agent任务结果
    executor_tools = json_response.get("tools", [])
    memory = json_response.get("memory", "")

    # 更新状态
    return {
        "tools": executor_tools,
        "memory": memory,
    }