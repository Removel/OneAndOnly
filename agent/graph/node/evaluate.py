from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any

from pyexpat.errors import messages

from agent.graph.state import GlobalState
from agent.prompt.evaluator_prompt import evaluator_system_prompt
from agent.util import LLMFactory


class EvaluationResult(BaseModel):
    should_retry: bool = Field(description="是否需要重试，是则true，否则false")

def evaluate_node(state: GlobalState) -> Dict[str, Any]:
    """
    评估节点，根据执行结果评估是否需要重试
    """
    # 获取到当前对话核心信息
    plan = state["plan"]
    response_text = state["response_text"]
    memory = state.get("memory", "")
    user_input = state.get("user_input", "")
    
    # 创建llm实例
    evaluator = LLMFactory.create_llm("evaluator")
    
    # 创建输出解析器
    output_parser = JsonOutputParser(pydantic_object=EvaluationResult)
    
    # 构建评估提示
    prompt = ChatPromptTemplate.from_messages([
        ("system", evaluator_system_prompt),
        ("ai", f"执行计划：{plan}"),
        ("human", f"用户输入：{user_input}\n执行结果：{response_text}\n当前记忆：{memory}")
    ])
    
    # 构建chain并执行评估
    chain = prompt | evaluator | output_parser
    evaluation = chain.invoke({
        "plan": plan,
        "user_input": user_input,
        "response_text": response_text,
        "memory": memory,
    })

    # 更新状态并返回评估结果
    return {
        "need_evaluate": evaluation.should_retry,
    }
