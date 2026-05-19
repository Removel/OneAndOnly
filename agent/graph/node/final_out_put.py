from typing import Dict, Any
import concurrent.futures

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agent.graph.state import GlobalState
from agent.prompt.memory_manager_prompt import (
    memory_manager_system_prompt_summarize,
)
from agent.prompt.summarizer_prompt import  summarizer_system_prompt_error, \
    summarizer_system_prompt_normal
from agent.util import LLMFactory, AgentFactory
from agent.util.find_tools import find_tools, all_tools


# 异步操作，更新外挂记忆库内容
def update_memory_async(user_input: str):
    try:
        memory_manager = AgentFactory.create_role_agent(
            "memory_manager",
            all_tools,
            memory_manager_system_prompt_summarize,
        )
        summarize_result = memory_manager.invoke(user_input)
        print(summarize_result)
    except Exception as e:
        print(f"Error updating memory: {e}")


def final_output_node(state: GlobalState)->Dict[str, Any]:
    """
    最终输出节点，根据状态生成最终输出
    """
    # 获取到当前对话核心信息
    response = state["response_text"]
    user_input = state["user_input"]
    retry_times = state["retry_times"]

    # 创建llm实例
    llm = LLMFactory.create_llm("summarizer")

    if retry_times >= 3:
        # 构建错误响应提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", summarizer_system_prompt_error),
            ("human", "{response}"),
        ])
    else:
        # 构建正常响应提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", summarizer_system_prompt_normal),
            ("human", "{response}"),
        ])

    # 创建链式调用
    chain = prompt | llm | JsonOutputParser()
    # 执行llm任务
    json_response = chain.invoke({"response": response})
    # 解析llm任务结果
    response_text = json_response.get("response_text", "")
    emotion_vac = json_response.get("emotion_vac", {})

    # 使用线程池在后台执行记忆更新操作
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(update_memory_async, user_input)

    # 更新状态
    return {
        "response_text": response_text,
        "messages": AIMessage(content = response_text),
        "emotion_vac": emotion_vac,
    }