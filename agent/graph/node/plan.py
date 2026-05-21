import logging

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import Dict, Any

from agent.graph.state import GlobalState
from agent.prompt.planner_prompt import planner_system_prompt
from agent.util import LLMFactory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PlanResult(BaseModel):
    plan: str = Field(description="执行计划，格式如：步骤1：任务内容->步骤2：任务内容->...")
    need_evaluate: bool = Field(description="是否需要评估执行结果，需要则为true，不需要则为false")

def plan_node (state: GlobalState)->Dict[str, Any]:
    """
    理解意图、生成思考、是否需要评估
    """
    logger.info("========== 进入 Plan 节点 ==========")
    
    # 获取到当前对话核心信息，获取到当前长期记忆
    messages = state["messages"]
    user_input = state["user_input"]
    memory = state["memory"]
    
    logger.info(f"用户输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户输入: {user_input}")
    logger.info(f"记忆内容: {memory[:50]}..." if memory and len(memory) > 50 else f"记忆内容: {memory if memory else '无'}")

    # 创建planner模型实例
    logger.debug("创建planner模型实例")
    planner = LLMFactory.create_llm("planner")

    # 构建提示词模板
    logger.debug("构建提示词模板")
    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", planner_system_prompt.format(memory=memory or "无")),
        MessagesPlaceholder("messages"),
        ("human", "当前用户输入: {user_input}"),
    ])

    # 创建输出解析器
    output_parser = JsonOutputParser(pydantic_object=PlanResult)

    # 构建chain
    chain = planner_prompt | planner | output_parser
    
    # 执行chain
    logger.info("执行planner chain...")
    result = chain.invoke({
        "messages": messages, 
        "user_input": user_input
    })
    
    # 从解析结果中提取信息
    plan = result.get("plan", "")
    need_evaluate = result.get("need_evaluate", False)
    
    logger.info(f"生成计划: {plan[:100]}..." if len(plan) > 100 else f"生成计划: {plan}")
    logger.info(f"是否需要评估: {need_evaluate}")
    logger.info("========== 离开 Plan 节点 ==========\n")
    
    # 更新状态并返回
    return {
        "plan": plan,
        "need_evaluate": need_evaluate,
    }