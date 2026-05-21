import json
import logging
from typing import Dict, Any

from agent.graph.state import GlobalState
from agent.prompt.executor_prompt import executor_system_prompt
from agent.util import AgentFactory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def execute_node(state:GlobalState)->Dict[str, Any]:
    """
    执行计划节点，根据执行计划选择是否调用工具，执行计划任务
    """
    logger.info("========== 进入 Execute 节点 ==========")
    
    # 获取到当前对话核心信息
    plan = state["plan"]
    tools = state["tools"]
    
    logger.info(f"执行计划: {plan[:100]}..." if len(plan) > 100 else f"执行计划: {plan}")
    logger.info(f"可用工具: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]}")

    # 创建agent实例
    logger.debug("创建executor agent实例")
    agent = AgentFactory.create_role_agent(
        "executor",
        tools,
        system_prompt=executor_system_prompt.format(plan=plan),
        response_format=None,
    )

    # 执行计划
    logger.info("执行计划...")
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
    
    logger.info(f"执行结果: {response_text[:100]}..." if len(response_text) > 100 else f"执行结果: {response_text}")
    logger.info("========== 离开 Execute 节点 ==========\n")
    
    return {
        "response_text": response_text
    }