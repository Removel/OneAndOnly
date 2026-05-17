from agent.graph.state import GlobalState


def route_after_execute(state: GlobalState) -> str:
    """
    Execute节点后的条件边路由函数
    
    根据文档设计：
    - 如果need_evaluate为True，路由到Evaluate节点进行评估
    - 如果need_evaluate为False，直接路由到FinalOutput节点（闲聊无需校验）
    
    Args:
        state: 当前全局状态
        
    Returns:
        str: 下一个节点的名称 ("evaluate" 或 "final_output")
    """
    if state.get("need_evaluate", False):
        return "evaluate"
    else:
        return "final_output"