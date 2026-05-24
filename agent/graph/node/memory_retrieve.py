import json
import logging
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.memory_manager_prompt import memory_manager_system_prompt_find
from agent.util import AgentFactory
from agent.util.find_tools import all_tools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MemoryRetrieveResult(BaseModel):
    tools: list[str] = Field(description="executor可能调用的工具名称列表")
    memory: str = Field(description="召回记忆内容")

def memory_retrieve_node(state: GlobalState) -> Dict[str, Any]:
    """
    从外挂知识库当中获取相关对话需要的相关信息
    """
    logger.info("========== 进入 Memory Retrieve 节点 ==========")
    
    # 获取到当前对话核心信息
    user_input = state["user_input"]
    messages = state["messages"]
    
    logger.info(f"用户输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户输入: {user_input}")
    logger.info(f"对话历史条数: {len(messages)}")

    # 创建agent实例
    logger.debug("创建memory_manager agent实例")
    memory_manager = AgentFactory.create_role_agent(
        agent_name="memory_manager",
        agent_tools=all_tools,
        system_prompt=memory_manager_system_prompt_find,
        response_format=MemoryRetrieveResult,
    )

    # 构建提示词模板
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("messages"),
        ("human", "{input}")
    ])

    # 执行agent任务
    logger.info("执行memory_manager任务...")
    
    # 构建消息列表，将当前用户输入添加到历史消息中
    input_messages = messages.copy()
    input_messages.append(HumanMessage(content=user_input))
    
    str_response = memory_manager.invoke({"messages": input_messages})

    final_reply = str_response["messages"][-1].content

    json_response = json.loads(final_reply)

    # 解析agent任务结果
    executor_tools = json_response.get("tools", [])
    memory = json_response.get("memory", "")

    logger.info(f"将要给下一个智能体的工具: {executor_tools}")
    logger.info(f"召回的记忆: {memory[:100]}..." if memory and len(memory) > 100 else f"召回的记忆: {memory if memory else '无'}")
    logger.info("========== 离开 Memory Retrieve 节点 ==========\n")
    
    # 更新状态
    return {
        "tools": executor_tools,
        "memory": memory,
    }