from typing import Type

from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from .config_loader import load_agent_config
from .llm_factory import LLMFactory
from ..hooks.log_info import log_tool_calls, log_agent_output


class AgentFactory:

    @staticmethod
    def create_role_agent(
        agent_name: str,
        agent_tools: list[Tool],
        system_prompt: str,
        response_format: Type[BaseModel] | None = None,
    ):
        """
        根据配置创建指定类型的智能体

        Args:
            agent_name: 智能体名称 (planner, executor, evaluator, memory_manager, summarizer)
            agent_tools: 智能体可用的工具列表
            system_prompt: 智能体的系统提示
            response_format: 智能体的响应格式，用于结构化输出

        Returns:
            配置好的智能体实例
        """
        llm = LLMFactory.create_llm(agent_name)

        agent = create_agent(
            model=llm,
            tools=agent_tools,
            system_prompt=system_prompt,
            response_format=response_format,
            middleware=[log_tool_calls, log_agent_output]
        )

        return agent