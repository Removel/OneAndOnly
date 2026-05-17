import importlib
import os
from pathlib import Path
from typing import List, Any


def find_tools() -> List[Any]:
    """
    扫描tools包下的所有py文件，识别其中的@tool装饰的函数，并返回工具对象列表
    
    Returns:
        包含所有tools包下工具对象的列表
    """
    tools_dir = Path(__file__).parent.parent / "tools"
    tools = []
    
    # 遍历tools目录下的所有.py文件
    for file_path in tools_dir.glob("*.py"):
        # 跳过__init__.py文件
        if file_path.name == "__init__.py":
            continue
            
        try:
            # 动态导入模块
            module_name = f"agent.tools.{file_path.stem}"
            module = importlib.import_module(module_name)
            
            # 遍历模块的所有属性，查找工具对象
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # 检查是否是LangChain工具对象
                if hasattr(attr, 'name') and hasattr(attr, 'description'):
                    tools.append(attr)
                    
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    return tools

all_tools = find_tools()