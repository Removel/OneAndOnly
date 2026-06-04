import importlib
import os
import sys
from pathlib import Path
from typing import List, Any


def find_tools_for_memory_manager() -> List[Any]:
    """
    扫描tools包下tools_for_memory_manager的所有py文件，识别其中的@tool装饰的函数，并返回工具对象列表
    
    Returns:
        包含所有tools_for_memory_manager包下的工具对象的列表
    """
    # 确保项目根目录在Python路径中
    project_root = Path(__file__).parent.parent.parent  # 到达 One_And_Only 目录
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    tools_dir = Path(__file__).parent.parent / "tools" / "tools_for_memory_manager"
    tools = []
    
    # 遍历tools目录下的所有.py文件
    for file_path in tools_dir.glob("*.py"):
        # 跳过__init__.py文件
        if file_path.name == "__init__.py":
            continue
            
        try:
            # 构建模块名 - 从项目根开始的完整路径
            # 文件路径: D:/Projects/One_And_Only/agent/tools/tools_for_memory_manager/some_file.py
            # 相对于项目根: agent/tools/tools_for_memory_manager/some_file.py
            # 模块名: agent.tools.tools_for_memory_manager.some_file
            relative_path = file_path.relative_to(project_root)  # 相对于项目根目录
            module_parts = list(relative_path.parts)
            module_name = ".".join(module_parts).replace('.py', '')
            
            # 确保模块名以 agent 开头
            if not module_name.startswith('agent.'):
                continue
                
            module = importlib.import_module(module_name)
            
            # 遍历模块的所有属性，查找工具对象
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # 检查是否是LangChain工具对象 - 修正条件：StructuredTool对象没有__name__属性
                if (hasattr(attr, 'name') and 
                    hasattr(attr, 'description') and 
                    hasattr(attr, 'invoke')):  # LangChain工具通常有invoke方法
                    tools.append(attr)
                    
        except ImportError as e:
            print(f"ImportError processing {file_path.name}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    return tools

def find_tools_for_plan_executor() -> List[Any]:
    """
    扫描tools包下tools_for_plan_executor的所有py文件，识别其中的@tool装饰的函数，并返回工具对象列表

    Returns:
        包含所有tools_for_plan_executor包下的工具对象的列表
    """
    # 确保项目根目录在Python路径中
    project_root = Path(__file__).parent.parent.parent  # 到达 One_And_Only 目录
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 当前为空实现，可根据实际需求添加工具
    tools_dir = Path(__file__).parent.parent / "tools" / "tools_for_plan_executor"
    tools = []
    
    # 检查目录是否存在
    if not tools_dir.exists():
        return []
    
    # 遍历tools目录下的所有.py文件
    for file_path in tools_dir.glob("*.py"):
        # 跳过__init__.py文件
        if file_path.name == "__init__.py":
            continue
            
        try:
            # 构建模块名 - 从项目根开始的完整路径
            relative_path = file_path.relative_to(project_root)  # 相对于项目根目录
            module_parts = list(relative_path.parts)
            module_name = ".".join(module_parts).replace('.py', '')
            
            # 确保模块名以 agent 开头
            if not module_name.startswith('agent.'):
                continue
                
            module = importlib.import_module(module_name)
            
            # 遍历模块的所有属性，查找工具对象
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                # 检查是否是LangChain工具对象 - 修正条件：StructuredTool对象没有__name__属性
                if (hasattr(attr, 'name') and 
                    hasattr(attr, 'description') and 
                    hasattr(attr, 'invoke')):  # LangChain工具通常有invoke方法
                    tools.append(attr)
                    
        except ImportError as e:
            print(f"ImportError processing {file_path.name}: {e}")
            continue
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    return tools


def find_all_tools() -> List[Any]:
    """
    扫描所有工具包中的工具
    
    Returns:
        包含所有工具对象的列表
    """
    all_tools = []
    all_tools.extend(find_tools_for_memory_manager())
    all_tools.extend(find_tools_for_plan_executor())
    return all_tools
    
tools_for_plan_executor = find_tools_for_plan_executor()
tools_for_memory_manager = find_tools_for_memory_manager()