from typing import Optional, Dict, Any, AsyncGenerator
from pathlib import Path
from agent.util.build_and_compile_graph import build_graph
from agent.graph.state import GlobalState
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import aiosqlite
import json
import asyncio


# 聊天管理类（统一使用异步数据库驱动，对外同时提供同步和异步接口）
class ChatManager:

    def __init__(self):
        self._compiled_graph = None
        self._checkpointer = None
        self._conn = None

    async def _get_checkpointer(self):
        if self._checkpointer is None:
            db_path = Path(__file__).parent.parent / "database" / "agent" / "checkpoints.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(str(db_path))
            self._checkpointer = AsyncSqliteSaver(self._conn)
        return self._checkpointer

    async def _get_compiled_graph(self):
        if self._compiled_graph is None:
            graph = build_graph()
            await self._get_checkpointer()
            self._compiled_graph = graph.compile(checkpointer=self._checkpointer)
        return self._compiled_graph

    async def get_conversation_history_async(self, thread_id: str) -> list:
        """异步获取对话历史"""
        config = {"configurable": {"thread_id": thread_id}}
        compiled_graph = await self._get_compiled_graph()
        state = await compiled_graph.aget_state(config)
        return state.values.get("messages", []) if state else []

    def get_conversation_history(self, thread_id: str) -> list:
        """同步获取对话历史（内部通过 asyncio.run 桥接）"""
        return asyncio.run(self.get_conversation_history_async(thread_id))

    async def clear_history_async(self, thread_id: Optional[str] = None):
        """异步清空会话历史"""
        if thread_id and self._checkpointer:
            try:
                await self._checkpointer.adelete_thread(thread_id)
                print(f"成功清空会话 {thread_id} 的历史")
            except Exception as e:
                print(f"清空对话历史失败: {str(e)}")
                import traceback
                traceback.print_exc()

    def clear_history(self, thread_id: Optional[str] = None):
        """同步清空会话历史（内部通过 asyncio.run 桥接）"""
        asyncio.run(self.clear_history_async(thread_id))

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None
            self._checkpointer = None
            self._compiled_graph = None


# 全局单例
_manager = ChatManager()


# ======================== 对外暴露的函数 ========================

def chat_with_agent(
    user_input: str,
    session_id: Optional[str] = None,
    clear_history: bool = False,
) -> Dict[str, Any]:
    """
    同步聊天函数（非流式），对外暴露使用

    :param user_input: 用户输入文本
    :param session_id: 会话ID，用于存储和检索对话历史
    :param clear_history: 是否清空会话历史
    :return: 包含模型回复、情绪VAC、重试次数、错误信息、是否成功等信息的字典
    """
    async def _run():
        try:
            if clear_history:
                await _manager.clear_history_async(session_id)

            compiled_graph = await _manager._get_compiled_graph()

            initial_state: GlobalState = {
                "messages": [],
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

            config = {"configurable": {"thread_id": session_id}} if session_id else {}

            result = await compiled_graph.ainvoke(initial_state, config=config)

            return {
                "response_text": result.get("response_text", ""),
                "emotion_vac": result.get("emotion_vac", {}),
                "retry_times": result.get("retry_times", 0),
                "error_message": result.get("error_message"),
                "success": True,
            }
        except Exception as e:
            return {
                "response_text": f"处理过程中发生错误: {str(e)}",
                "emotion_vac": {},
                "error_message": str(e),
                "success": False,
            }

    return asyncio.run(_run())


def get_conversation_history(session_id: Optional[str] = None) -> list:
    """同步获取对话历史"""
    return _manager.get_conversation_history(session_id)


def clear_conversation_history(session_id: Optional[str] = None):
    """同步清空对话历史"""
    _manager.clear_history(session_id)


async def chat_stream_with_agent(
    user_input: str,
    session_id: Optional[str] = None,
    clear_history: bool = False,
) -> AsyncGenerator[str, None]:
    """
    流式聊天函数，对外暴露使用

    :param user_input: 用户输入文本
    :param session_id: 会话ID，用于存储和检索对话历史
    :param clear_history: 是否清空会话历史
    :return: 异步生成器，产生 SSE 格式的事件流
    """

    try:
        if clear_history:
            await _manager.clear_history_async(session_id)

        compiled_graph = await _manager._get_compiled_graph()

        initial_state: GlobalState = {
            "messages": [],
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

        config = {"configurable": {"thread_id": session_id}} if session_id else {}

        final_state = None

        async for event in compiled_graph.astream_events(initial_state, config=config, version="v2"):
            event_type = event.get("event", "")

            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    data = json.dumps({"content": chunk.content})
                    yield f"event: token\ndata: {data}\n\n"

            elif event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input")
                data = json.dumps({"tool": tool_name, "input": str(tool_input)})
                yield f"event: tool_start\ndata: {data}\n\n"

            elif event_type == "on_tool_end":
                tool_output = event.get("data", {}).get("output")
                output_str = str(tool_output)[:500] if tool_output else ""
                data = json.dumps({"result": output_str})
                yield f"event: tool_end\ndata: {data}\n\n"

            elif event_type == "on_chain_start":
                chain_name = event.get("name", "unknown")
                if chain_name and not chain_name.startswith("LangGraph"):
                    data = json.dumps({"node": chain_name})
                    yield f"event: node_start\ndata: {data}\n\n"

            elif event_type == "on_chain_end":
                chain_name = event.get("name", "unknown")
                if chain_name and not chain_name.startswith("LangGraph"):
                    data = json.dumps({"node": chain_name})
                    yield f"event: node_end\ndata: {data}\n\n"

                final_state = event.get("data", {}).get("output")

        if final_state:
            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'emotion_vac': final_state.get('emotion_vac', {}), 'retry_times': final_state.get('retry_times', 0)})}\n\n"
        else:
            yield f"event: done\ndata: {json.dumps({'status': 'completed', 'emotion_vac': {}, 'retry_times': 0})}\n\n"

    except Exception as e:
        error_data = json.dumps({"message": str(e)})
        yield f"event: error\ndata: {error_data}\n\n"
