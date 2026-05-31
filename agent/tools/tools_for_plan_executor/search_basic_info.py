from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """
    获取当前时间信息，包括日期、时间、星期等
    
    @return: 当前时间的详细信息，包括日期、时间、星期几等
    """
    try:
        now = datetime.now()
        
        # 获取各种时间信息
        current_date = now.strftime("%Y年%m月%d日")
        current_time = now.strftime("%H:%M:%S")
        weekday = now.strftime("%A")
        weekday_cn = now.strftime("%w")
        
        # 星期映射
        weekday_map = {
            "0": "星期日",
            "1": "星期一", 
            "2": "星期二",
            "3": "星期三",
            "4": "星期四",
            "5": "星期五",
            "6": "星期六"
        }
        
        weekday_cn_name = weekday_map.get(weekday_cn, "未知")
        
        # 构建返回信息
        time_info = f"""
当前时间信息：
- 日期：{current_date}
- 时间：{current_time}
- 星期：{weekday_cn_name}
- 完整时间：{now.strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return time_info.strip()
        
    except Exception as e:
        return f"获取时间失败：{str(e)}"


@tool
def get_current_date() -> str:
    """
    获取当前日期信息
    
    @return: 当前日期，格式为 YYYY年MM月DD日
    """
    try:
        now = datetime.now()
        return now.strftime("%Y年%m月%d日")
    except Exception as e:
        return f"获取日期失败：{str(e)}"


@tool
def get_current_timestamp() -> str:
    """
    获取当前时间戳信息
    
    @return: 当前时间戳，包括秒级和毫秒级时间戳
    """
    try:
        import time
        now = datetime.now()
        
        timestamp_seconds = int(now.timestamp())
        timestamp_milliseconds = int(now.timestamp() * 1000)
        
        return f"""
当前时间戳：
- 秒级时间戳：{timestamp_seconds}
- 毫秒级时间戳：{timestamp_milliseconds}
- ISO格式：{now.isoformat()}
""".strip()
        
    except Exception as e:
        return f"获取时间戳失败：{str(e)}"