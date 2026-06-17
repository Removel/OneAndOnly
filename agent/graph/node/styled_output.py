import json
import logging
import threading
from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from agent.graph.state import GlobalState
from agent.prompt.memory_manager_prompt import (
    memory_manager_system_prompt_summarize,
)
from agent.prompt.summarizer_prompt import (
    summarizer_system_prompt_error,
    summarizer_system_prompt_normal,
    summarizer_system_prompt_gate,
    summarizer_user_prompt_normal,
    summarizer_user_prompt_error,
    summarizer_user_prompt_gate,
)
from agent.util import AgentFactory
from agent.util.find_tools import tools_for_memory_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmotionVAC(BaseModel):
    """情绪VAC三维评分"""
    valence: float = Field(ge=0, le=1, description="效价评分(0-1)，表示情绪的正负性，越高越积极")
    arousal: float = Field(ge=0, le=1, description="唤醒度评分(0-1)，表示情绪的强度，越高越强烈")
    control: float = Field(ge=0, le=1, description="控制度评分(0-1)，表示对情绪的控制程度，越高控制力越强")


class StyledOutputResult(BaseModel):
    """summarizer 节点的结构化输出"""
    response_text: str = Field(description="转换后的回答内容，使用角色风格，不含任何动作描述或元信息")
    emotion_vac: EmotionVAC = Field(description="当前回复对应的情绪VAC评分")
    need_continue: bool = Field(default=False, description="是否需要继续执行plan_execute节点进行进一步处理")


# 异步操作，更新外挂记忆库内容
def update_memory_async(user_input: str, conversation_history: list = None):
    try:
        memory_manager = AgentFactory.create_role_agent(
            "memory_manager",
            tools_for_memory_manager,
            memory_manager_system_prompt_summarize,
        )
        # 构建消息列表，包含对话历史和当前用户输入
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append(HumanMessage(content=f"这是新的用户输入: '{user_input}'\n你不需要对用户输入回应，请你开始更新记忆"))

        response = memory_manager.invoke({"messages": messages})
        logger.info("更新记忆成功")
    except Exception as e:
        logger.error(f"更新记忆失败: {e}")


def styled_output_node(state: GlobalState) -> Dict[str, Any]:
    """
    Styled Output 节点，支持双模式：
    - **门控模式**（response_text 为空）：首次调用，判断是否需要 plan_execute
      简单问题直接回复并结束（need_continue=False）
      复杂问题标记继续处理（need_continue=True）
    - **风格模式**（response_text 有内容）：最终调用，格式化 plan_execute 的输出
      设置 need_continue=False，直接结束
    """
    user_input = state["user_input"]
    response = state.get("response_text", "")
    retry_times = state.get("retry_times", 0)

    # 模式判断：response_text 是否有实质内容
    is_style_mode = bool(response and response.strip())

    if is_style_mode:
        return _style_mode(state, response, user_input, retry_times)
    else:
        memory = state.get("memory") or "无相关记忆"
        return _gate_mode(state, user_input, memory)


def _gate_mode(state: GlobalState, user_input: str, memory: str) -> Dict[str, Any]:
    """门控模式：判断是否需要继续到 plan_execute"""
    logger.info("========== 进入 Styled Output 节点 [门控模式] ==========")
    logger.info(f"用户原始输入: {user_input[:100]}..." if len(user_input) > 100 else f"用户原始输入: {user_input}")
    logger.info(f"记忆上下文: {memory[:100]}..." if len(memory) > 100 else f"记忆上下文: {memory}")

    # 创建 summarizer agent（门控 prompt）
    logger.debug("创建summarizer agent实例（门控模式）")
    summarizer = AgentFactory.create_role_agent(
        agent_name="summarizer",
        agent_tools=[],
        system_prompt=summarizer_system_prompt_gate,
        response_format=StyledOutputResult,
    )

    # 执行 agent
    logger.info("执行summarizer agent（门控判断）...")
    user_message = summarizer_user_prompt_gate.format(memory=memory, user_input=user_input)
    input_messages = list(state.get("messages", []))
    input_messages.append(HumanMessage(content=user_message))
    result = summarizer.invoke({"messages": input_messages})

    # 解析结构化输出
    str_response = result["messages"][-1].content
    logger.debug(f"LLM结构化输出:\n{str_response}")

    try:
        json_response = json.loads(str_response)
        need_continue = json_response.get("need_continue", True)
        response_text = json_response.get("response_text", "")
        emotion_data = json_response.get("emotion_vac", {})
        emotion_vac = {
            "valence": float(emotion_data.get("valence", 0.5)),
            "arousal": float(emotion_data.get("arousal", 0.5)),
            "control": float(emotion_data.get("control", 0.5)),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"解析结构化输出失败，默认继续到plan_execute: {e}")
        need_continue = True
        response_text = ""
        emotion_vac = {"valence": 0.5, "arousal": 0.5, "control": 0.5}

    if need_continue:
        # 复杂问题：仅设置 need_continue=True，不更新记忆
        logger.info("门控判断: 复杂问题 → 继续到 plan_execute")
        logger.info("========== 离开 Styled Output 节点 [门控模式] ==========\n")
        return {"need_continue": True}
    else:
        # 简单问题：直接输出回复，更新记忆
        logger.info(f"门控判断: 简单问题 → 直接回复")
        logger.info(f"直接回复: {response_text[:100]}..." if len(response_text) > 100 else f"直接回复: {response_text}")
        logger.info(f"情绪VAC: {emotion_vac}")

        # 异步更新记忆
        logger.debug("启动异步记忆更新（后台线程）")
        conversation_history = state.get("messages", [])
        thread = threading.Thread(target=update_memory_async, args=(user_input, conversation_history))
        thread.daemon = False
        thread.start()

        logger.info("========== 离开 Styled Output 节点 [门控模式] ==========\n")

        return {
            "need_continue": False,
            "response_text": response_text,
            "messages": [HumanMessage(content=user_input), AIMessage(content=response_text)],
            "emotion_vac": emotion_vac,
        }


def _style_mode(state: GlobalState, response: str, user_input: str, retry_times: int) -> Dict[str, Any]:
    """风格模式：格式化 plan_execute 的输出（原有逻辑）"""
    logger.info("========== 进入 Styled Output 节点 [风格模式] ==========")

    logger.info(f"输入响应内容: {response[:100]}..." if len(response) > 100 else f"输入响应内容: {response}")
    logger.info(f"用户原始输入: {user_input[:50]}..." if len(user_input) > 50 else f"用户原始输入: {user_input}")
    logger.info(f"重试次数: {retry_times}")

    # 根据重试次数选择提示词
    if retry_times >= 3:
        logger.info("重试次数超过3次，使用错误响应模板")
        system_prompt = summarizer_system_prompt_error
        user_prompt = summarizer_user_prompt_error
    else:
        logger.info("使用正常响应模板")
        system_prompt = summarizer_system_prompt_normal
        user_prompt = summarizer_user_prompt_normal

    # 创建 summarizer agent 实例（无工具，仅结构化输出）
    logger.debug("创建summarizer agent实例（风格模式）")
    summarizer = AgentFactory.create_role_agent(
        agent_name="summarizer",
        agent_tools=[],
        system_prompt=system_prompt,
        response_format=StyledOutputResult,
    )

    # 执行 agent
    logger.info("执行summarizer agent...")
    user_message = user_prompt.format(response=response)
    result = summarizer.invoke({"messages": [HumanMessage(content=user_message)]})

    # 解析结构化输出
    str_response = result["messages"][-1].content
    logger.debug(f"LLM结构化输出:\n{str_response}")

    try:
        json_response = json.loads(str_response)
        response_text = json_response.get("response_text", response)
        emotion_data = json_response.get("emotion_vac", {})
        emotion_vac = {
            "valence": float(emotion_data.get("valence", 0.5)),
            "arousal": float(emotion_data.get("arousal", 0.5)),
            "control": float(emotion_data.get("control", 0.5)),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"解析结构化输出失败，使用默认值: {e}")
        response_text = response  # 回退：直接使用 plan_execute 的原始输出
        emotion_vac = {"valence": 0.5, "arousal": 0.5, "control": 0.5}

    # 使用后台线程执行记忆更新操作（主线程不等待）
    logger.debug("启动异步记忆更新（后台线程）")
    conversation_history = state.get("messages", [])
    thread = threading.Thread(target=update_memory_async, args=(user_input, conversation_history))
    thread.daemon = False
    thread.start()

    logger.info(f"最终响应: {response_text[:100]}..." if len(response_text) > 100 else f"最终响应: {response_text}")
    logger.info(f"情绪VAC: {emotion_vac}")
    logger.info("========== 离开 Styled Output 节点 [风格模式] ==========\n")

    # 更新状态
    return {
        "response_text": response_text,
        "messages": [HumanMessage(content=user_input), AIMessage(content=response_text)],
        "emotion_vac": emotion_vac,
        "need_continue": False,
    }
