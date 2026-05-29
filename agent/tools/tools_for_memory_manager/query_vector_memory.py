import chromadb
from langchain_core.tools import tool
from datetime import datetime, timedelta

import os

"""
查询向量数据库工具，库设计：
每条记忆向量绑定一级类目：
- `category`：一级大类
- `importance`：low/medium/high
- `timestamp`：对话时间戳
"""

def collect_to_vector_db():
    db_path = os.path.join(os.path.dirname(__file__), "../../../database/agent/vector_memory.db")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="vector_memory")
    return collection


@tool
def query_from_category(category: str, query: str ,n_results: int = 3) -> str:
    """
    从向量数据库当中查询事件记忆，根据一级大类进行筛选。
    一级分类必须从以下选：
        事件经历维度、三观与观念维度、性格与情绪维度、
        社交与关系维度、喜好与厌恶维度、习惯与行为维度、基础属性维度
    @param category: 一级大类
    @param query: 查询的对话内容
    @param n_results: 返回的相关对话数量，默认3条
    @return: 相关对话需要的相关前三条信息
    """
    # TODO: 1. 检查category是否在以上列表中，检查query是否为空字符串
    valid_categories = ["事件经历维度", "三观与观念维度", "性格与情绪维度",
                        "社交与关系维度", "喜好与厌恶维度", "习惯与行为维度", "基础属性维度"]

    if category not in valid_categories:
        return f"错误：category必须从以下列表中选择：{', '.join(valid_categories)}"

    if not query.strip():
        return "错误：query不能为空字符串"

    # TODO: 2. 从向量数据库中查询相关对话,选取前n_results条相关对话
    try:
        collection = collect_to_vector_db()
        results = collection.query(
            where={"category": category},
            query_texts=query,
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return "未找到相关对话"

        # 构建格式化结果列表
        formatted_results = []
        for i in range(min(n_results, len(results["documents"][0]))):
            formatted_results.append({
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })

    # TODO: 3. 返回相关对话需要的相关信息
        return str(formatted_results)
        
    except Exception as e:
        return f"查询失败：{str(e)}"

@tool
def query_from_category_and_time(category: str, time_range: list[str], query: str, n_results: int = 3) -> str:
    """
    从外挂知识库（向量数据库）当中查询相关对话需要的相关信息，根据一级大类和时间进行筛选。
    @param category: 一级大类目
    @param time_range: 时间戳范围
    @param query: 查询的对话内容
    @param n_results: 返回的相关对话数量，默认3条
    @return: 相关记忆前n_results条信息，默认3条信息
    category（一级类目）固定 7 个,只能从下面选，不能自创：
    ["事件经历维度", "三观与观念维度", "性格与情绪维度","社交与关系维度", "喜好与厌恶维度", "习惯与行为维度", "基础属性维度"]
    时间戳范围参数应当是格式为[开始时间, 结束时间]，例子：["2024-01-01", "2024-01-02"]
    """
    # TODO: 1. 检查category是否在以上列表中，检查query是否为空字符串
    valid_categories = ["事件经历维度", "三观与观念维度", "性格与情绪维度",
                        "社交与关系维度", "喜好与厌恶维度", "习惯与行为维度", "基础属性维度"]

    if category not in valid_categories:
        return f"错误：category必须从以下列表中选择：{', '.join(valid_categories)}"

    if not query.strip():
        return "错误：query不能为空字符串"

    # TODO: 2. 检查time_range是否为2个元素的列表，且元素为符合格式的字符串
    if len(time_range) != 2:
        return "错误：time_range必须包含开始时间和结束时间[开始时间, 结束时间]"
    
    # TODO：3. 转化列表为int类型的时间戳用于查询
    try:
        # 验证时间格式
        start_time = datetime.strptime(time_range[0], "%Y-%m-%d")
        end_time = datetime.strptime(time_range[1], "%Y-%m-%d")

        if start_time > end_time:
            return "错误：开始时间不能晚于结束时间"

        # 转换为整数时间戳，对齐到天
        start_ts = int(start_time.timestamp())
        end_ts = int(end_time.replace(hour=23, minute=59, second=59).timestamp())

    # TODO: 4. 从向量数据库中查询相关对话,选取前n_results条相关对话
        collection = collect_to_vector_db()

        # 构建查询条件，同时包含类别和时间范围
        # 注意：ChromaDB 需要使用整数时间戳进行查询
        where_clause = {
            "$and": [
                {"category": category},
                {"date": {"$gte": start_ts}},  # 使用整数时间戳
                {"date": {"$lte": end_ts}}   # 使用整数时间戳
            ]
        }
        
        results = collection.query(
            where=where_clause,
            query_texts=query,
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )
        
        if not results["documents"] or not results["documents"][0]:
            return "在指定时间范围内未找到相关对话"
        
        formatted_results = []
        for i in range(min(n_results, len(results["documents"][0]))):
            formatted_results.append({
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })
        
        # TODO: 5. 返回相关对话需要的相关信息
        return str(formatted_results)
        
    except ValueError as ve:
        return f"时间格式错误：{str(ve)}，请使用 YYYY-MM-DD 格式"
    except Exception as e:
        return f"查询失败：{str(e)}"

@tool
def query_events(time_type: str, query: str, importance: str, n_results: int = 3) -> str:
    """
    从向量数据库当中查询事件记忆，根据时间类型和重要性进行筛选。
    时间类型包括：
        - "recent": 最近的事件
        - "past": 过去的事件
        - "future": 未来的事件
    重要性包括：
        - "high": 高重要性
        - "medium": 中等重要性
        - "low": 低重要性
    @param time_type: 时间类型
    @param query: 查询的事件内容
    @param importance: 重要性级别
    @param n_results: 返回结果数量，默认为3
    @return: 相关事件信息
    """
    valid_time_types = ["recent", "past", "future"]
    valid_importance_levels = ["high", "medium", "low"]
    
    if time_type not in valid_time_types:
        return f"错误：time_type必须从以下列表中选择：{', '.join(valid_time_types)}"
    
    if importance not in valid_importance_levels:
        return f"错误：importance必须从以下列表中选择：{', '.join(valid_importance_levels)}"
    
    if not query.strip():
        return "错误：query不能为空字符串"
    
    try:
        from datetime import datetime, timedelta
        
        collection = collect_to_vector_db()
        
        # 根据时间类型构建查询条件
        if time_type == "recent":
            # 最近事件（过去7天）
            recent_date = datetime.now() - timedelta(days=7)
            recent_timestamp = int(recent_date.timestamp())
            where_clause = {
                "$and": [
                    {"importance": importance},
                    {"date": {"$gte": recent_timestamp}}
                ]
            }
        elif time_type == "past":
            # 过去的事件（早于今天）
            today = datetime.now().replace(hour=23, minute=59, second=59)
            today_timestamp = int(today.timestamp())
            where_clause = {
                "$and": [
                    {"importance": importance},
                    {"date": {"$lte": today_timestamp}}
                ]
            }
        else:  # future
            # 未来的事件（晚于今天）
            today = datetime.now()
            today_timestamp = int(today.timestamp())
            where_clause = {
                "$and": [
                    {"importance": importance},
                    {"date": {"$gte": today_timestamp}}
                ]
            }
        
        results = collection.query(
            where=where_clause,
            query_texts=query,
            n_results=n_results,
            include=["metadatas", "documents", "distances"],
        )
        
        if not results["documents"] or not results["documents"][0]:
            return f"未找到{time_type}时间类型且重要性为{importance}的相关事件"
        
        formatted_results = []
        for i in range(min(n_results, len(results["documents"][0]))):
            formatted_results.append({
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })
        
        return str(formatted_results)
        
    except Exception as e:
        return f"查询失败：{str(e)}"