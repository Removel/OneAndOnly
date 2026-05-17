from agent.graph.state import GlobalState


def route_after_evaluate(state: GlobalState) -> str:
    """
    Evaluate节点后的条件边路由函数
    
    根据文档设计：
    - 如果need_evaluate为False，评估通过，路由到FinalOutput节点
    - 如果need_evaluate为True且retry_times < 3，需要重试，路由到Plan节点
    - 如果need_evaluate为True且retry_times >= 3，重试次数超限，路由到FinalOutput节点（输出错误异常回答）
    
    Args:
        state: 当前全局状态
        
    Returns:
        str: 下一个节点的名称 ("plan" 或 "final_output")
    """
    need_evaluate = state.get("need_evaluate", False)
    retry_times = state.get("retry_times", 0)
    
    if not need_evaluate:
        # 评估通过，直接输出最终结果
        return "final_output"
    elif retry_times >= 3:
        # 重试次数超过限制，输出错误异常回答
        return "final_output"
    else:
        # 需要重试且回到Plan节点重新规划
        return "plan"