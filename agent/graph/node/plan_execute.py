import json
import logging
import re
from typing import Dict, Any, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.plan_execute_prompt import plan_execute_system_prompt
from agent.util import AgentFactory
from agent.util.find_tools import tools_for_plan_executor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _extract_json(text: str) -> Optional[str]:
    """从混合文本中提取 JSON 对象子串（找到第一个 { 和最后一个 } 之间的内容）"""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return None


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

    logger.info(f"用户输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户输入: {user_input}")
    logger.info(f"记忆内容: {memory[:50]}..." if memory and len(memory) > 50 else f"记忆内容: {memory if memory else '无'}")
    logger.info(f"可用工具: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in tools_for_plan_executor]}")

    # 创建agent实例
    logger.debug("创建plan_execute agent实例")
    agent = AgentFactory.create_role_agent(
        agent_name="plan_execute",
        agent_tools=tools_for_plan_executor,
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

        parsed = None
        # 先尝试直接解析整个内容为 JSON
        try:
            parsed = json.loads(message_content)
        except (json.JSONDecodeError, ValueError):
            pass

        # 如果失败，尝试提取 JSON 子串（处理 LLM 输出"文本+JSON"混合体）
        if parsed is None:
            json_substr = _extract_json(message_content)
            if json_substr:
                try:
                    parsed = json.loads(json_substr)
                    logger.debug("从混合输出中成功提取 JSON 子串")
                except (json.JSONDecodeError, ValueError):
                    pass

        if parsed is not None:
            response_text = parsed.get("response_text", message_content)
            need_evaluate = parsed.get("need_evaluate", False)
        else:
            # 完全无法解析 JSON，使用原始文本作为回复
            response_text = message_content
            need_evaluate = False
            logger.debug("无法解析 JSON，使用原始文本作为 response_text")

    if not response_text:
        response_text = str(result)
    
    logger.info(f"回复文本: {response_text[:100]}..." if len(response_text) > 100 else f"回复文本: {response_text}")
    logger.info(f"是否需要评估: {need_evaluate}")
    logger.info("========== 离开 PlanExecute 节点 ==========\n")
    
    return {
        "response_text": response_text,
        "need_evaluate": need_evaluate,
    }