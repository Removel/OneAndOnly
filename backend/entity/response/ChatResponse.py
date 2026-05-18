from datetime import datetime
from typing import Dict, Any, Optional

from agent.graph.state import GlobalState


class ChatResponse:
    def __init__(self,
                 vac: Dict[str, Any] = None,  # 情感向量
                 response: str = "",    # 囙复文本
                 error_message: str = "",    # 错误信息
                 retry_times: int = 0,    # 重试次数
                 success: bool = True,    # 是否成功
                 ):
        self.vac = vac or {}
        self.response = response
        self.error_message = error_message
        self.retry_times = retry_times
        self.success = success


