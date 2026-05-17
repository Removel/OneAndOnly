from langchain_core.tools import tool


@tool
def write_to_mds(content: str):
    """
    向外挂知识库(md文档)当中写入相关对话需要的相关信息，一般用于存储静态、结构化、不常变化的个人档案信息（基础属性、长期能力、固定偏好等）。
    """
