"""
编辑向量数据库工具，库设计：
每条记忆向量绑定一级类目：
- `category`：一级大类
- `importance`：important/normal
- `timestamp`：对话时间戳
"""
import os
import uuid
from datetime import datetime

import chromadb
from langchain_core.tools import tool


def collect_to_vector_db():
    db_path = os.path.join(os.path.dirname(__file__), "../../../database/agent/vector_memory.db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="vector_memory")
    return collection


@tool
def search_memory_ids(query: str, category: str = None, n_results: int = 5) -> str:
    """
    搜索记忆并返回匹配的记忆ID列表，用于后续的修改操作
    @param query: 搜索关键词
    @param category: 可选的类别筛选
    @param n_results: 返回结果数量
    @return: 包含记忆ID和内容的列表
    """
    try:
        collection = collect_to_vector_db()
        
        if category:
            results = collection.query(
                where={"category": category},
                query_texts=query,
                n_results=n_results,
                include=["metadatas", "documents", "distances"],
            )
        else:
            results = collection.query(
                query_texts=query,
                n_results=n_results,
                include=["metadatas", "documents", "distances"],
            )
        
        if not results["documents"] or not results["documents"][0]:
            return "未找到匹配的记忆"
        
        memory_list = []
        for i in range(len(results["documents"][0])):
            memory_info = {
                "document_id": results["metadatas"][0][i].get("id", results["ids"][0][i]),  # 优先使用元数据中的id，否则使用文档ID
                "content": results["documents"][0][i],
                "category": results["metadatas"][0][i].get("category", "unknown"),
                "importance": results["metadatas"][0][i].get("importance", "unknown"),
                "timestamp": results["metadatas"][0][i].get("timestamp", "unknown"),
                "distance": results["distances"][0][i]
            }
            memory_list.append(memory_info)
        
        return str(memory_list)
        
    except Exception as e:
        return f"搜索失败：{str(e)}"


@tool
def update_memory_content(doc_id: str, new_content: str) -> str:
    """
    更新向量数据库中指定记忆的内容
    @param doc_id: 要更新的记忆文档ID
    @param new_content: 新的记忆内容
    @return: 更新状态信息
    """
    if not doc_id.strip():
        return "错误：doc_id不能为空"
    
    if not new_content.strip():
        return "错误：new_content不能为空"
    
    try:
        collection = collect_to_vector_db()
        
        # 查询是否存在该文档
        existing_doc = collection.get(ids=[doc_id])
        if not existing_doc or not existing_doc['ids']:
            return f"错误：找不到ID为 {doc_id} 的文档"
        
        # 获取原有元数据
        old_metadata = existing_doc['metadatas'][0] if existing_doc['metadatas'] else {}
        
        # 更新文档内容和时间戳
        updated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 解析当前时间，转换为整数时间戳（按天对齐）
        parsed_datetime = datetime.strptime(updated_timestamp.split()[0], "%Y-%m-%d")
        date_timestamp = int(parsed_datetime.timestamp())
        
        # 保留原有的元数据，并更新时间戳
        updated_metadata = {
            **old_metadata,
            "timestamp": updated_timestamp,
            "date": date_timestamp  # 使用整数时间戳
        }
        
        # 更新文档
        collection.update(
            ids=[doc_id],
            documents=[new_content],
            metadatas=[updated_metadata]
        )
        
        return f"记忆内容更新成功，ID: {doc_id}"
        
    except Exception as e:
        return f"更新失败：{str(e)}"


@tool
def update_memory_importance(doc_id: str, new_importance: str) -> str:
    """
    更新向量数据库中指定记忆的重要性等级
    @param doc_id: 要更新的记忆文档ID
    @param new_importance: 新的重要性等级
    @param importance: 重要性级别
    @return: 更新状态信息
    """
    valid_importance_levels = ["important", "normal"]
    
    if not doc_id.strip():
        return "错误：doc_id不能为空"
    
    if new_importance not in valid_importance_levels:
        return f"错误：new_importance必须从以下列表中选择：{', '.join(valid_importance_levels)}"
    
    try:
        collection = collect_to_vector_db()
        
        # 查询是否存在该文档
        existing_doc = collection.get(ids=[doc_id])
        if not existing_doc or not existing_doc['ids']:
            return f"错误：找不到ID为 {doc_id} 的文档"
        
        # 获取原有元数据
        old_metadata = existing_doc['metadatas'][0] if existing_doc['metadatas'] else {}
        
        # 更新元数据中的重要性
        updated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 解析当前时间，转换为整数时间戳（按天对齐）
        parsed_datetime = datetime.strptime(updated_timestamp.split()[0], "%Y-%m-%d")
        date_timestamp = int(parsed_datetime.timestamp())
        
        updated_metadata = {
            **old_metadata,
            "importance": new_importance,
            "timestamp": updated_timestamp,  # 更新时间戳
            "date": date_timestamp  # 使用整数时间戳
        }
        
        # 更新文档
        collection.update(
            ids=[doc_id],
            documents=[existing_doc['documents'][0]] if existing_doc['documents'] else [""],
            metadatas=[updated_metadata]
        )
        
        return f"记忆重要性更新成功，ID: {doc_id}，新重要性: {new_importance}"
        
    except Exception as e:
        return f"更新失败：{str(e)}"


@tool
def delete_memory(doc_id: str) -> str:
    """
    删除向量数据库中指定的记忆
    @param doc_id: 要删除的记忆文档ID
    @return: 删除状态信息
    """
    if not doc_id.strip():
        return "错误：doc_id不能为空"
    
    try:
        collection = collect_to_vector_db()
        
        # 查询是否存在该文档
        existing_doc = collection.get(ids=[doc_id])
        if not existing_doc or not existing_doc['ids']:
            return f"错误：找不到ID为 {doc_id} 的文档"
        
        # 删除文档
        collection.delete(ids=[doc_id])
        
        return f"记忆删除成功，ID: {doc_id}"
        
    except Exception as e:
        return f"删除失败：{str(e)}"