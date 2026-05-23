import importlib
import inspect
from pathlib import Path
from typing import Dict, Callable, Any, Optional

from langgraph.graph import StateGraph
from langgraph.types import Checkpointer

from agent.graph.state import GlobalState


def scan_conditional_edges() -> Dict[str, Dict[str, Any]]:
    """
    扫描edge目录下的所有条件边函数，返回用于图构建的条件边配置
    
    Returns:
        Dict[str, Dict[str, Any]]: 条件边配置字典
        {
            "源节点名": {
                "function": 条件边函数,
                "function_name": 函数名,
                "module": 模块名
            }
        }
    """
    edge_dir = Path(__file__).parent.parent / "graph" / "edge"
    conditional_edges = {}
    
    # 遍历edge目录下的所有.py文件
    for file_path in edge_dir.glob("*.py"):
        # 跳过__init__.py文件
        if file_path.name == "__init__.py":
            continue
        
        try:
            # 动态导入模块
            module_name = f"agent.graph.edge.{file_path.stem}"
            module = importlib.import_module(module_name)
            
            # 遍历模块的所有属性，查找条件边函数
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                    
                attr = getattr(module, attr_name)
                
                # 检查是否是函数
                if not inspect.isfunction(attr):
                    continue
                
                # 检查函数签名：应该接受GlobalState参数，返回str
                sig = inspect.signature(attr)
                params = list(sig.parameters.keys())
                
                # 验证函数签名：第一个参数应该是GlobalState类型
                if len(params) != 1:
                    continue
                    
                param = sig.parameters[params[0]]
                if param.annotation != GlobalState:
                    continue
                
                # 验证返回类型应该是str
                if sig.return_annotation != str:
                    continue
                
                # 从函数名推断源节点名称
                # 例如：route_after_execute -> execute
                if attr_name.startswith("route_after_"):
                    source_node = attr_name.replace("route_after_", "")
                    conditional_edges[source_node] = {
                        "function": attr,
                        "function_name": attr_name,
                        "module": module_name
                    }
                    
        except Exception as e:
            print(f"Error processing edge file {file_path.name}: {e}")
            continue
    
    return conditional_edges


def get_conditional_edge_functions() -> Dict[str, Callable]:
    """
    获取所有条件边函数的简化版本，直接返回函数映射
    
    Returns:
        Dict[str, Callable]: 源节点名到条件边函数的映射
        {
            "execute": route_after_execute函数,
            "evaluate": route_after_evaluate函数
        }
    """
    conditional_edges_config = scan_conditional_edges()
    return {
        source_node: config["function"] 
        for source_node, config in conditional_edges_config.items()
    }


def scan_nodes() -> Dict[str, Dict[str, Any]]:
    """
    扫描node目录下的所有节点函数，返回用于图构建的节点配置
    
    Returns:
        Dict[str, Dict[str, Any]]: 节点配置字典
        {
            "节点名": {
                "function": 节点函数,
                "function_name": 函数名,
                "module": 模块名
            }
        }
    """
    node_dir = Path(__file__).parent.parent / "graph" / "node"
    nodes = {}
    
    # 遍历node目录下的所有.py文件
    for file_path in node_dir.glob("*.py"):
        # 跳过__init__.py文件
        if file_path.name == "__init__.py":
            continue
        
        try:
            # 动态导入模块
            module_name = f"agent.graph.node.{file_path.stem}"
            module = importlib.import_module(module_name)
            
            # 遍历模块的所有属性，查找节点函数
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                    
                attr = getattr(module, attr_name)
                
                # 检查是否是函数
                if not inspect.isfunction(attr):
                    continue
                
                # 检查函数签名：应该接受GlobalState参数，返回Dict[str, Any]
                sig = inspect.signature(attr)
                params = list(sig.parameters.keys())
                
                # 验证函数签名：第一个参数应该是GlobalState类型
                if len(params) != 1:
                    continue
                    
                param = sig.parameters[params[0]]
                if param.annotation != GlobalState:
                    continue
                
                # 验证返回类型应该是Dict[str, Any]
                if sig.return_annotation != Dict[str, Any]:
                    continue
                
                # 从函数名推断节点名称
                # 例如：memory_retrieve -> memory_retrieve, plan_node -> plan, final_output_node -> final_output
                node_name = attr_name
                
                # 处理特殊命名情况
                if node_name.endswith("_node"):
                    node_name = node_name.replace("_node", "")
                elif node_name == "memory_retrieve":
                    node_name = "memory_retrieve"
                elif node_name == "final_output_node":
                    node_name = "final_output"
                
                nodes[node_name] = {
                    "function": attr,
                    "function_name": attr_name,
                    "module": module_name
                }
                    
        except Exception as e:
            print(f"Error processing node file {file_path.name}: {e}")
            continue
    
    return nodes


def get_node_functions() -> Dict[str, Callable]:
    """
    获取所有节点函数的简化版本，直接返回函数映射
    
    Returns:
        Dict[str, Callable]: 节点名到节点函数的映射
        {
            "memory_retrieve": memory_retrieve函数,
            "plan_execute": plan_execute_node函数,
            "evaluate": evaluate_node函数,
            "final_output": final_output_node函数
        }
    """
    nodes_config = scan_nodes()
    return {
        node_name: config["function"] 
        for node_name, config in nodes_config.items()
    }


def build_graph() -> StateGraph:
    """
    构建完整的LangGraph图，包括所有节点和边
    
    根据文档设计的流程：
    Start → MemoryRetrieve → PlanExecute → (条件边)
                                              ↓
                                          if need_evaluate?
                                              ↓
                                          Evaluate → (条件边)
                                                  ↓
                                              need_evaluate?
                                            ↙         ↘
                                          true       false
                                            ↓           ↓
                                  重试次数>=3?     FinalOutput
                                    ↙       ↘
                                   否       是
                                   ↓         ↓
                                  PlanExecute    FinalOutput
    
    Returns:
        StateGraph: 构建完成的图对象
    """
    # 获取所有节点和条件边
    nodes = get_node_functions()
    edges = get_conditional_edge_functions()
    
    # 创建状态图
    graph = StateGraph(GlobalState)
    
    # 添加所有节点
    for node_name, node_func in nodes.items():
        graph.add_node(node_name, node_func)
    
    # 设置入口点
    graph.set_entry_point("memory_retrieve")
    
    # 添加固定边（无条件边）
    # MemoryRetrieve → PlanExecute
    graph.add_edge("memory_retrieve", "plan_execute")
    
    # 添加条件边
    # PlanExecute → (evaluate 或 final_output)
    if "plan_execute" in edges:
        graph.add_conditional_edges(
            "plan_execute",
            edges["plan_execute"],
            {
                "evaluate": "evaluate",
                "final_output": "final_output"
            }
        )
    
    # Evaluate → (plan_execute 或 final_output)
    if "evaluate" in edges:
        graph.add_conditional_edges(
            "evaluate",
            edges["evaluate"],
            {"plan_execute": "plan_execute", "final_output": "final_output"},
        )

    # 设置终点
    graph.set_finish_point("final_output")
    
    return graph


def compile_graph(checkpointer: Optional[Checkpointer] = None) -> Any:
    """
    构建并编译完整的LangGraph图

    Args:
        checkpointer (Optional[Checkpointer], optional): 用于状态检查和恢复的检查点对象。默认值为None。

    Returns:
        编译后的图对象，可以直接用于执行
    """
    graph = build_graph()
    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()