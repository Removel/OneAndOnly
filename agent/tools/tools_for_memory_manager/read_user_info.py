from pathlib import Path
from langchain_core.tools import tool


@tool
def read_user_info() -> str:
    """
    通过直接读取并返回用户信息文件，从外挂知识库(md文档)当中获取相关对话需要的相关信息，一般用于获取静态、结构化、不常变化的个人档案信息（基础属性、长期能力、固定偏好等）。
    @return: md文档中查询返回的所有的个人档案信息
    """
    # TODO：0：检查个人文档是否存在
    user_info_path = Path(__file__).parent.parent.parent.parent / "database" / "agent" / "user_info.md"
    
    if not user_info_path.exists():
        return f"个人档案文档不存在：{user_info_path}"
    
    # TODO：1：读取个人档案文档内容
    with open(user_info_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # TODO：2：返回整个文档为字符串形式
    return content