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

    def get_checkpointer(self):
        return self._checkpointer

    def get_compiled_graph(self):
        if self._compiled_graph is None:
            graph = build_graph()
            db_path = Path(__file__).parent.parent / "database" / "agent" /"checkpoints.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            self._checkpointer = SqliteSaver(conn)
            self._compiled_graph = graph.compile(checkpointer=self._checkpointer)
        return self._compiled_graph

    def get_conversation_history(self, thread_id: Optional[str] = None):
        if thread_id and self._checkpointer:
            try:
                config = {"configurable": {"thread_id": thread_id}}
                checkpoint = self._checkpointer.get(config)
                if checkpoint:
                    # checkpoint的结构是Checkpoint对象，需要访问其属性
                    if hasattr(checkpoint, 'channel_values'):
                        state = checkpoint.channel_values
                        if isinstance(state, dict) and 'messages' in state:
                            return state['messages']
                    elif isinstance(checkpoint, dict):
                        return checkpoint.get("messages", [])
            except Exception as e:
                print(f"获取对话历史失败: {str(e)}")
                import traceback
                traceback.print_exc()
        return []

    # 清空对话历史
    def clear_history(self, thread_id: Optional[str] = None):
        if thread_id and self._checkpointer:
            try:
                config = {"configurable": {"thread_id": thread_id}}
                self._checkpointer.put(config, {}, {})
            except Exception as e:
                print(f"清空对话历史失败: {str(e)}")



# 聊天管理类实体
_chat_manager = ChatManager()


# 聊天函数，对外暴露使用
def chat_with_agent(
    user_input: str,
    session_id: Optional[str] = None,
    conversation_history: Optional[list] = None,
    clear_history: bool = False,
) -> Dict[str, Any]:
    """
    聊天函数，对外暴露使用

    :param user_input: 用户输入文本
    :param session_id: 会话ID，用于存储和检索对话历史
    :param conversation_history: 对话历史，用于初始化状态
    :param clear_history: 是否清空会话历史
    :return: 包含模型回复、情绪VAC、重试次数、错误信息、是否成功等信息的字典
    """

    try:
        # TODO：1、初始化对话状态所需参数
        if clear_history:
            _chat_manager.clear_history(session_id)

        compiled_graph = _chat_manager.get_compiled_graph()

        initial_state: GlobalState = {
            "messages": [],  # 初始化为空列表，LangGraph 会自动从 checkpointer 恢复历史消息
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
        # LangGraph 会自动从 checkpointer 恢复状态（包括 messages）
        config = {"configurable": {"thread_id": session_id}} if session_id else {}
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