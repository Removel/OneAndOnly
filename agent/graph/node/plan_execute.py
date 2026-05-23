import json
import logging
from typing import Dict, Any

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.plan_execute_prompt import plan_execute_system_prompt
from agent.util import AgentFactory, LLMFactory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PlanExecuteResult(BaseModel):
    response_text: str = Field(description="对用户的回复文本")
    need_evaluate: bool = Field(description="是否需要评估执行结果，需要则为true，不需要则为false")

def plan_execute_node(state: GlobalState) -> Dict[str, Any]:
    """
    规划与执行合并节点：理解意图、生成回复、决策是否需要评估
    """
    logger.info("========== 进入 PlanExecute 节点 ==========")
    
    # 获取当前对话核心信息
    messages = state["messages"]
    user_input = state["user_input"]
    memory = state["memory"]
    tools = state["tools"]
    
    logger.info(f"用户输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户输入: {user_input}")
    logger.info(f"记忆内容: {memory[:50]}..." if memory and len(memory) > 50 else f"记忆内容: {memory if memory else '无'}")
    logger.info(f"可用工具: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]}")

    # 创建agent实例
    logger.debug("创建plan_execute agent实例")
    agent = AgentFactory.create_role_agent(
        "plan_execute",
        tools,
        system_prompt=plan_execute_system_prompt.format(memory=memory or "无"),
        response_format=None,
    )

    # 执行规划与执行（包含对话历史）
    logger.info("执行规划与执行...")
    
    # 构建消息列表，将当前用户输入添加到历史消息中
    input_messages = messages.copy()
    input_messages.append(HumanMessage(content=user_input))
    
    result = agent.invoke({"messages": input_messages})

    # 更新状态
    response_text = ""
    need_evaluate = False
    
    messages = result.get("messages", [])
    if messages:
        # 从最后一条消息中提取内容
        last_message = messages[-1]
        message_content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
        
        try:
            parsed = json.loads(message_content)
            response_text = parsed.get("response_text", message_content)
            need_evaluate = parsed.get("need_evaluate", False)
        except (json.JSONDecodeError, ValueError):
            response_text = message_content
            need_evaluate = False
    
    if not response_text:
        response_text = str(result)
    
    logger.info(f"回复文本: {response_text[:100]}..." if len(response_text) > 100 else f"回复文本: {response_text}")
    logger.info(f"是否需要评估: {need_evaluate}")
    logger.info("========== 离开 PlanExecute 节点 ==========\n")
    
    return {
        "response_text": response_text,
        "need_evaluate": need_evaluate,
    }