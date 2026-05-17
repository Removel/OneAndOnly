from langchain.agents import create_agent
from .config_loader import load_agent_config

class AgentFactory:
    @staticmethod
    def create_agent(agent_name: str,agent_tools: list,system_prompt: str):
        """
        根据配置创建指定类型的智能体
        
        Args:
            agent_name: 智能体名称 (planner, executor, evaluator, finder, summarizer)
            agent_tools: 智能体可用的工具列表
            system_prompt: 智能体的系统提示

        Returns:
            配置好的智能体实例
        """
        config = load_agent_config(agent_name)
        model_name = config['model_config']['model_name']
        """
        temperature = config['model_config'].get('temperature', 0.7)
        max_tokens = config['model_config'].get('max_tokens', 512)
        base_url = config['api_config']['base_url']
        api_key = config['api_config']['api_key']
        """
        
        # 创建带有自定义配置的ChatOpenAI实例
        agent = create_agent(
            model=model_name,
            tools=agent_tools,
            system_prompt=system_prompt
        )
        
        return agent
