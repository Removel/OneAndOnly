from typing import Optional, Dict, Any
from pathlib import Path
from agent.util.build_and_compile_graph import build_graph
from agent.graph.state import GlobalState
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# 聊天管理类
class ChatManager:

    def __init__(self):
        self._compiled_graph = None
        self._checkpointer = None
        self._conn = None

    def get_checkpointer(self):
        if self._checkpointer is None:
            db_path = Path(__file__).parent.parent / "database" / "agent" /"checkpoints.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
            self._checkpointer = SqliteSaver(self._conn)
        return self._checkpointer

    def get_compiled_graph(self):
        if self._compiled_graph is None:
            graph = build_graph()
            self.get_checkpointer()
            self._compiled_graph = graph.compile(checkpointer=self._checkpointer)
        return self._compiled_graph

    def get_conversation_history(self, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        compiled_graph = self.get_compiled_graph()
        state = compiled_graph.get_state(config)
        return state.values.get("messages", []) if state else []

    def clear_history(self, thread_id: Optional[str] = None):
        if thread_id and self._checkpointer:
            try:
                self._checkpointer.delete_thread(thread_id)
                print(f"成功清空会话 {thread_id} 的历史")
            except Exception as e:
                print(f"清空对话历史失败: {str(e)}")
                import traceback
                traceback.print_exc()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._checkpointer = None
            self._compiled_graph = None


# 聊天管理类实体
_chat_manager = ChatManager()


# 聊天函数，对外暴露使用
def chat_with_agent(
    user_input: str,
    session_id: Optional[str] = None,
    clear_history: bool = False,
) -> Dict[str, Any]:
    """
    聊天函数，对外暴露使用

    :param user_input: 用户输入文本
    :param session_id: 会话ID，用于存储和检索对话历史
    :param clear_history: 是否清空会话历史
    :return: 包含模型回复、情绪VAC、重试次数、错误信息、是否成功等信息的字典
    """

    try:
        # TODO：1、初始化对话状态所需参数
        if clear_history:
            _chat_manager.clear_history(session_id)

        compiled_graph = _chat_manager.get_compiled_graph()

        initial_state: GlobalState = {
            "messages": [],  # 初始化为空列表
            "user_input": user_input,
            "response_text": "",
            "plan": "",
            "memory": None,
            "error_message": None,
            "tools": [],
            "need_evaluate": False,
            "retry_times": 0,
            "emotion_vac": {},
        }
        
        # TODO：2、执行智能体图
        # 创建配置，如果有 session_id
        config = {"configurable": {"thread_id": session_id}} if session_id else {}
        
        # 如果设置了 clear_history，确保不从检查点恢复消息
        if clear_history and session_id:
            # 在这种情况下，我们已经清空了历史，invoke 将使用提供的初始状态
            # 不会恢复检查点中的历史消息
            pass
        
        result = compiled_graph.invoke(initial_state, config=config)
        # TODO：3、返回结果
        return {
            "response_text": result.get("response_text", ""),
            "emotion_vac": result.get("emotion_vac", {}),
            "retry_times": result.get("retry_times", 0),
            "error_message": result.get("error_message"),
            "success": True,
        }
    # TODO：4、异常处理
    except Exception as e:
        return {
            "response_text": f"处理过程中发生错误: {str(e)}",
            "emotion_vac": {},
            "error_message": str(e),
            "success": False,
        }

def get_conversation_history(session_id: Optional[str] = None) -> list:
    return _chat_manager.get_conversation_history(session_id)

def clear_conversation_history(session_id: Optional[str] = None):
    _chat_manager.clear_history(session_id)