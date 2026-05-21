import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from agent.graph.state import GlobalState
from agent.prompt.evaluator_prompt import evaluator_system_prompt
from agent.util import LLMFactory

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class EvaluationResult(BaseModel):
    should_retry: bool = Field(description="是否需要重试，是则true，否则false")
    error_message: Optional[str] = Field(description="错误信息，如果需要重试则必填")

def evaluate_node(state: GlobalState) -> Dict[str, Any]:
    """
    评估节点，根据执行结果评估是否需要重试
    """
    logger.info("========== 进入 Evaluate 节点 ==========")
    
    # 获取到当前对话核心信息
    plan = state["plan"]
    response_text = state["response_text"]
    memory = state.get("memory", "")
    user_input = state.get("user_input", "")
    retry_times = state.get("retry_times", 0)
    
    logger.info(f"执行计划: {plan[:100]}..." if len(plan) > 100 else f"执行计划: {plan}")
    logger.info(f"执行结果: {response_text[:100]}..." if len(response_text) > 100 else f"执行结果: {response_text}")
    logger.info(f"当前重试次数: {retry_times}")

    # 创建llm实例
    logger.debug("创建evaluator模型实例")
    evaluator = LLMFactory.create_llm("evaluator")

    # 创建输出解析器
    output_parser = JsonOutputParser(pydantic_object=EvaluationResult)
    
    # 转义执行结果中的花括号，避免被模板解析为变量
    escaped_plan = plan.replace("{", "{{").replace("}", "}}")
    escaped_response_text = response_text.replace("{", "{{").replace("}", "}}")
    escaped_memory = memory.replace("{", "{{").replace("}", "}}") if memory else ""
    
    # 构建评估提示
    prompt = ChatPromptTemplate.from_messages([
        ("system", evaluator_system_prompt.format(user_input=user_input)),
        ("ai", f"执行计划为：{escaped_plan}，当前记忆为：{escaped_memory}"),
        ("human", f"当前执行结果：{escaped_response_text}")
    ])
    
    # 构建chain并执行评估
    chain = prompt | evaluator | output_parser
    logger.info("执行评估...")
    evaluation = chain.invoke({
        "plan": plan,
        "user_input": user_input,
        "memory": memory,
    })

    should_retry = evaluation.get("should_retry", False)
    error_message = evaluation.get("error_message", "")
    
    logger.info(f"评估结果 - 是否需要重试: {should_retry}")
    if error_message:
        logger.info(f"错误信息: {error_message}")
    
    # 更新状态并返回评估结果
    if should_retry:
        logger.info("评估结果：需要重试")
        logger.info("========== 离开 Evaluate 节点 ==========\n")
        return {
            "need_evaluate": should_retry,
            "error_message": error_message,
            "retry_times": retry_times + 1,
        }
    else:
        logger.info("评估结果：无需重试，直接输出")
        logger.info("========== 离开 Evaluate 节点 ==========\n")
        return {
            "need_evaluate": should_retry,
        }