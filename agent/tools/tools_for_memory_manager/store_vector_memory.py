"""
存储向量数据库工具，库设计：
每条记忆向量绑定一级类目：
- `category`：一级大类
- `importance`：high/medium/low
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
def store_event(content: str, timestamp: str, importance: str = "medium"):
    """
    向向量数据库当中写入事件记忆
    @param content: 事件记忆内容，你必须总结对话内容，不能直接写入原始对话
    @param timestamp: 事件记忆时间戳，你必须根据当前对话内容推断出时间戳
    @param importance: 事件记忆重要性，默认medium，high/medium/low
    @return: 成功状态信息
    """
    valid_importance_levels = ["high", "medium", "low"]
    
    if importance not in valid_importance_levels:
        return f"错误：importance必须从以下列表中选择：{', '.join(valid_importance_levels)}"
    
    if not content.strip():
        return "错误：content不能为空"
    
    try:
        collection = collect_to_vector_db()
        
        # 生成唯一ID
        doc_id = str(uuid.uuid4())
        
        # 解析传入的时间戳，转换为整数时间戳
        from datetime import datetime
        parsed_datetime = datetime.strptime(timestamp.split()[0] if ' ' in timestamp else timestamp, "%Y-%m-%d")
        date_timestamp = int(parsed_datetime.timestamp())
        
        # 存储到向量数据库
        collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[{
                "id": doc_id,  # 保存ID到元数据中便于查找
                "category": "事件经历维度",  # 事件记忆归类到事件经历维度
                "importance": importance,
                "timestamp": timestamp,
                "date": date_timestamp,  # 存储为整数时间戳
                "event_type": "event"
            }],
        )
        
        return f"事件记忆存储成功，ID: {doc_id}"
        
    except Exception as e:
        return f"存储失败：{str(e)}"

@tool
def store_memory(content: str, category: str):
    """
    向向量数据库当中写入事件之外的其他记忆
    一级分类必须从以下选：
    三观与观念维度、性格与情绪维度、社交与关系维度、喜好与厌恶维度、习惯与行为维度、基础属性维度
    @param content: 记忆内容
    @param category: 一级分类
    @return: 成功状态信息
    """
    valid_categories = ["三观与观念维度", "性格与情绪维度", "社交与关系维度", 
                        "喜好与厌恶维度", "习惯与行为维度", "基础属性维度"]
    
    if category not in valid_categories:
        return f"错误：category必须从以下列表中选择：{', '.join(valid_categories)}"
    
    if not content.strip():
        return "错误：content不能为空"
    
    try:
        collection = collect_to_vector_db()
        
        # 生成唯一ID
        doc_id = str(uuid.uuid4())
        
        # 获取当前时间戳
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 解析当前时间，转换为整数时间戳（按天对齐）
        parsed_datetime = datetime.strptime(current_timestamp.split()[0], "%Y-%m-%d")
        date_timestamp = int(parsed_datetime.timestamp())
        
        # 存储到向量数据库
        collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[{
                "id": doc_id,  # 保存ID到元数据中便于查找
                "category": category,
                "importance": "medium",  # 默认为中等重要性
                "timestamp": current_timestamp,
                "date": date_timestamp,  # 存储为整数时间戳
                "event_type": "memory"  # 标识为记忆而非事件
            }],
        )
        
        return f"记忆存储成功，ID: {doc_id}"
        
    except Exception as e:
        return f"存储失败：{str(e)}"