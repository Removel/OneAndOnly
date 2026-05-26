import re
from pathlib import Path
from langchain_core.tools import tool


@tool
def edit_user_info(
    updated_content: str,
    dry_run: bool = False
):
    """
    向外挂知识库(md文档)当中编辑个人档案信息，一般用于存储静态、结构化、不常变化的个人档案信息。
    你必须严格按照根据上面的该文档特性与内容进行编辑。不能随意记录任何其他信息。
    如果文档当中由不符合结构或者不符合文档要求记录的内容，你需要删除它。
    结构如下：
    # 用户档案 （一级标题，不可更改）
    ## 个人基础属性 （二级标题，一般是某个大方面的属性）
    ### 基础身份  （三级标题，一般是某个具体方面的属性）
    - 姓名：用户姓名
    - 家乡：用户家乡
    ...
    ### 生理特征
    - 身高：用户身高
    - 体重：用户体重
    ...

    请务必按照以上结构进行编辑。
    @param updated_content: 更新后的所有用户档案内容，将完全替换原文件内容
    @param dry_run: 是否为预览模式（true则只返回预览结果，不实际修改文件）
    @return: 修改结果或预览信息
    """
    user_info_path = (
        Path(__file__).parent.parent.parent.parent
        / "database"
        / "agent"
        / "user_info.md"
    )
    
    # 验证更新内容
    if not updated_content or not updated_content.strip():
        return "更新内容不能为空"
    
    if dry_run:
        return f"预览：将完全替换用户档案内容\n\n{updated_content[:200]}..."
    
    # 创建目录（如果不存在）
    user_info_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 将更新后的内容完全写入文件
    with open(user_info_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    return "用户档案更新成功"