import logging

from agent.graph.state import GlobalState

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def route_after_evaluate(state: GlobalState) -> str:
    """
    Evaluate节点后的条件边路由函数
    
    根据文档设计：
    - 如果need_evaluate为False，评估通过，路由到StyledOutput节点
    - 如果need_evaluate为True且retry_times < 3，需要重试，路由到Plan节点
    - 如果need_evaluate为True且retry_times >= 3，重试次数超限，路由到StyledOutput节点（输出错误异常回答）
    
    Args:
        state: 当前全局状态
        
    Returns:
        str: 下一个节点的名称 ("plan" 或 "styled_output")
    """
    need_evaluate = state.get("need_evaluate", False)
    retry_times = state.get("retry_times", 0)
    
    logger.info(f"========== 路由判断 (route_after_evaluate) ==========")
    logger.info(f"need_evaluate: {need_evaluate}")
    logger.info(f"retry_times: {retry_times}")
    
    if not need_evaluate:
        # 评估通过，直接输出最终结果
        logger.info("路由决策: 评估通过 → 前往 styled_output 节点")
        logger.info(f"========== 路由判断结束 (route_after_evaluate) ==========")
        return "styled_output"
    elif retry_times >= 3:
        # 重试次数超过限制，输出错误异常回答
        logger.info("路由决策: 重试次数超限(>=3) → 前往 styled_output 节点")
        logger.info(f"========== 路由判断 (route_after_evaluate) ==========")
        return "styled_output"
    else:
        # 需要重试且回到Plan节点重新规划
        logger.info(
            f"路由决策: 需要重试，当前重试次数({retry_times}) < 3 → 前往 plan 节点"
        )
        logger.info(f"========== 路由判断结束 (route_after_evaluate) ==========")
        return "plan"