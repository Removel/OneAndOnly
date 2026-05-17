from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import Dict, Any

from agent.graph.state import GlobalState
from agent.prompt.planner_prompt import planner_system_prompt
from agent.util import LLMFactory

class PlanResult(BaseModel):
    execution_plan: str = Field(description="执行计划，格式如：步骤1：任务内容->步骤2：任务内容->...")
    needs_evaluate: bool = Field(description="是否需要评估执行结果，需要则为true，不需要则为false")

def plan_node (state: GlobalState)->Dict[str, Any]:
    """
    理解意图、生成思考、是否需要评估
    """
    # 获取到当前对话核心信息
    messages = state["messages"]
    user_input = state["user_input"]
    # 获取到当前长期记忆
    memory = state["memory"]

    # 构建提示词模板
    planner_prompt = ChatPromptTemplate.from_messages([
        ("system", planner_system_prompt.format(memory=memory or "无")),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "当前用户输入: {user_input}"),
    ])

    # 创建planner模型实例
    planner = LLMFactory.create_llm("planner")
    
    # 使用结构化输出解析器
    output_parser = JsonOutputParser(pydantic_object=PlanResult)
    
    # 构建chain
    chain = planner_prompt | planner | output_parser
    
    # 执行chain
    plan = chain.invoke({
        "messages": messages, 
        "user_input": user_input
    })
    
    # 从解析结果中提取信息并更新状态
    return {
        "plan": plan.execution_plan,
        "need_evaluate": plan.needs_evaluate,
    }