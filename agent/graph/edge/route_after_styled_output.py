import logging

from agent.graph.state import GlobalState

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def route_after_styled_output(state: GlobalState) -> str:
    """
    StyledOutput节点后的条件边路由函数

    根据文档设计：
    - 如果need_continue为True，路由到PlanExecute节点（复杂问题需要进一步处理）
    - 如果need_continue为False，直接结束（简单问题已直接回复，或风格化已完成）

    Args:
        state: 当前全局状态

    Returns:
        str: 下一个节点的名称 ("plan_execute" 或 "__end__")
    """
    need_continue = state.get("need_continue", True)

    logger.info(f"========== 路由判断 (route_after_styled_output) ==========")
    logger.info(f"need_continue: {need_continue}")

    if need_continue:
        logger.info("路由决策: 需要继续处理 → 前往 plan_execute 节点")
        logger.info(f"========== 路由判断结束 (route_after_styled_output) ==========")
        return "plan_execute"
    else:
        logger.info("路由决策: 无需继续 → 结束")
        logger.info(f"========== 路由判断结束 (route_after_styled_output) ==========")
        return "__end__"
