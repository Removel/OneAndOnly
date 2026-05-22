import logging
import threading
from typing import Dict, Any

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

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 异步操作，更新外挂记忆库内容
def update_memory_async(user_input: str):
    try:
        memory_manager = AgentFactory.create_role_agent(
            "memory_manager",
            all_tools,
            memory_manager_system_prompt_summarize,
        )
        memory_manager.invoke({"input": user_input})
        logger.info("更新记忆成功")
    except Exception as e:
        logger.error(f"更新记忆失败: {e}")


def final_output_node(state: GlobalState)->Dict[str, Any]:
    """
    最终输出节点，根据状态生成最终输出
    """
    logger.info("========== 进入 Final Output 节点 ==========")
    
    # 获取到当前对话核心信息
    response = state["response_text"]
    user_input = state["user_input"]
    retry_times = state["retry_times"]
    
    logger.info(f"输入响应内容: {response[:100]}..." if len(response) > 100 else f"输入响应内容: {response}")
    logger.info(f"用户原始输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户原始输入: {user_input}")
    logger.info(f"重试次数: {retry_times}")

    # 创建llm实例
    logger.debug("创建summarizer模型实例")
    llm = LLMFactory.create_llm("summarizer")

    if retry_times >= 3:
        # 构建错误响应提示词模板
        logger.info("重试次数超过3次，使用错误响应模板")
        prompt = ChatPromptTemplate.from_messages([
            ("system", summarizer_system_prompt_error),
        ], template_format="jinja2")
    else:
        # 构建正常响应提示词模板
        logger.info("使用正常响应模板")
        prompt = ChatPromptTemplate.from_messages([
            ("system", summarizer_system_prompt_normal),
        ], template_format="jinja2")

    # 创建链式调用，直接获取文本内容
    chain = prompt | llm | StrOutputParser()
    # 执行llm任务
    logger.info("执行summarizer chain...")
    raw_content = chain.invoke({"response": response})
    logger.debug(f"LLM原始输出:\n{raw_content}")
    
    # 手动解析内容和情绪信息
    if "[EMOTION]" in raw_content and "[/EMOTION]" in raw_content:
        # 分离内容和情绪信息
        parts = raw_content.split("[EMOTION]")
        response_text = parts[0].strip()
        
        # 解析情绪信息
        emotion_section = parts[1].split("[/EMOTION]")[0].strip()
        logger.debug(f"情绪部分原始内容:\n{emotion_section}")
        emotion_vac = {}
        for line in emotion_section.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                try:
                    emotion_vac[key] = float(value)
                    logger.debug(f"解析情绪: {key} = {value}")
                except ValueError:
                    emotion_vac[key] = 0.5  # 默认值
                    logger.debug(f"解析失败，使用默认值: {key} = 0.5")
    else:
        # 如果没有情绪信息，使用默认值
        response_text = raw_content.strip()
        emotion_vac = {"valence": 0.5, "arousal": 0.5, "control": 0.5}

    # 使用后台线程执行记忆更新操作（主线程不等待）
    logger.debug("启动异步记忆更新（后台线程）")
    thread = threading.Thread(target=update_memory_async, args=(user_input,))
    thread.daemon = False
    thread.start()

    logger.info(f"最终响应: {response_text[:100]}..." if len(response_text) > 100 else f"最终响应: {response_text}")
    logger.info(f"情绪VAC: {emotion_vac}")
    logger.info("========== 离开 Final Output 节点 ==========\n")
    
    # 更新状态
    return {
        "response_text": response_text,
        "messages": AIMessage(content = response_text),
        "emotion_vac": emotion_vac,
    }