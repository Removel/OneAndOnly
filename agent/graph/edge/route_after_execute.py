import logging

from agent.graph.state import GlobalState

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    need_evaluate = state.get("need_evaluate", False)
    
    logger.info(f"========== 路由判断 (route_after_execute) ==========")
    logger.info(f"need_evaluate: {need_evaluate}")
    
    if need_evaluate:
        logger.info("路由决策: 需要评估 → 前往 evaluate 节点")
        return "evaluate"
    else:
        logger.info("路由决策: 无需评估 → 直接前往 final_output 节点")
        return "final_output"