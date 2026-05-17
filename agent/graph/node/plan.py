from agent.graph.state import GlobalState


def plan_node (state: GlobalState)->dict:
    """
    理解意图、生成思考、决定是否调用技能、是否需要校验
    """
    # 获取到当前对话核心信息
    messages = state["messages"]
    user_input = state["user_input"]
    # 获取到当前长期记忆
    memory = state["memory"]

    planner = create_planner()

    return state
