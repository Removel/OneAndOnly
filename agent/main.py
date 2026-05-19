from typing import Optional, Dict, Any
from agent.util.build_and_compile_graph import build_graph
from agent.graph.state import GlobalState

# 聊天管理类
class ChatManager:

    def __init__(self):
        self._compiled_graph = None
        self._conversation_history = []
    
    def get_compiled_graph(self):
        if self._compiled_graph is None:
            graph = build_graph()
            self._compiled_graph = graph.compile()
        return self._compiled_graph

    def get_conversation_history(self):
        return self._conversation_history

    # 清空对话历史
    def clear_history(self):
        self._conversation_history = []

# 聊天管理类实体
_chat_manager = ChatManager()

# 聊天函数，对外暴露使用
def chat_with_agent(
    user_input: str, 
    conversation_history: Optional[list] = None,
    clear_history: bool = False
) -> Dict[str, Any]:
    try:
        # TODO：1、初始化对话状态所需参数
        if clear_history:
            _chat_manager.clear_history()
        
        if conversation_history is not None:
            _chat_manager._conversation_history = conversation_history
        
        compiled_graph = _chat_manager.get_compiled_graph()
        
        initial_state: GlobalState = {
            "messages": _chat_manager.get_conversation_history(),
            "user_input": user_input,
            "response_text": "",
            "plan": "",
            "memory": None,
            "tools": [],
            "emotion_vac": {},
            "need_evaluate": False,
            "retry_times": 0,
            "error_message": None
        }

        # TODO：2、执行智能体图
        result = compiled_graph.invoke(initial_state)

        # TODO：3、更新对话历史
        _chat_manager._conversation_history = result["messages"]

        # TODO：4、返回结果
        return {
            "response_text": result.get("response_text", ""),
            "emotion_vac": result.get("emotion_vac", {}),
            "retry_times": result.get("retry_times", 0),
            "error_message": result.get("error_message"),
            "success": True
        }

    # TODO：5、异常处理
    except Exception as e:
        return {
            "response_text": f"处理过程中发生错误: {str(e)}",
            "emotion_vac": {},
            "retry_times": 0,
            "error_message": str(e),
            "success": False
        }

def get_conversation_history() -> list:
    return _chat_manager.get_conversation_history()

def clear_conversation_history():
    _chat_manager.clear_history()