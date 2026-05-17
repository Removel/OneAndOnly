from langchain_openai import ChatOpenAI

from agent.util import load_agent_config


class LLMFactory:

    @staticmethod
    def create_llm(llm_name: str)->ChatOpenAI:
        """
        创建ChatOpenAI模型实例

        Args:
            llm_name (str): 智能体名称 (planner, executor)

        Returns:
            ChatOpenAI模型实例

        """
        config = load_agent_config(llm_name)
        model_name = config['model_config']['model_name']

        temperature = config['model_config'].get('temperature')
        max_tokens = config['model_config'].get('max_tokens')
        base_url = config['api_config']['base_url']
        api_key = config['api_config']['api_key']
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            api_key=api_key,
        )
        return llm
