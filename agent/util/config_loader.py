import os
from dotenv import load_dotenv
import yaml
from pathlib import Path

# 加载环境变量
load_dotenv()

def load_agent_config(agent_name: str) -> dict:
    """
    加载指定智能体的配置
    
    Args:
        agent_name: 智能体名称 (planner, executor, evaluator, finder, summarizer)
    
    Returns:
        包含完整配置的字典
    """
    config_path = Path(__file__).parent / "config" / f"{agent_name}.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    # 从环境变量获取API密钥
    if 'api_config' in config and 'api_key_env' in config['api_config']:
        api_key_env_var = config['api_config']['api_key_env']
        config['api_config']['api_key'] = os.getenv(api_key_env_var)
        
    return config

def get_api_key(agent_name: str) -> str:
    """
    获取指定智能体的API密钥
    
    Args:
        agent_name: 智能体名称
        
    Returns:
        API密钥字符串
    """
    config = load_agent_config(agent_name)
    return config.get('api_config', {}).get('api_key')