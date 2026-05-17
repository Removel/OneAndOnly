from langchain_core.tools import tool


@tool
def query_from_chromadb(query: str) -> str:
    """
    从外挂知识库（向量数据库）当中查询相关对话需要的相关信息，一般用于检索动态、非结构化、需语义检索的记忆（事件、观点、情绪、短期规划等）。
    """
    return query
