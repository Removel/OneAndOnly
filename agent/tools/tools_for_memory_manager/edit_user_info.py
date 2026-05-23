import re
from pathlib import Path
from langchain_core.tools import tool


@tool
def edit_user_info(
    section: str,
    content: str,
    subsection: str = None,
    mode: str = "cover",
    dry_run: bool = False
):
    """
    向外挂知识库(md文档)当中编辑个人档案信息，一般用于存储静态、结构化、不常变化的个人档案信息（基础属性、长期能力、固定偏好等）。
    
    文档结构为三级：
    - 一级：标题（# 标题：个人档案）
    - 二级：维度（## 维度名称，如基础属性、长期能力等）
    - 三级：细节（### 细节名称）
    
    @param section: 要修改的标题名称（支持一级、二级、三级标题）
    @param content: 修改内容
    @param subsection: 要修改的子标题名称（可选，用于更精确的定位）
    @param mode: 修改模式
        - "cover": 覆盖指定标题下的所有内容（保留标题，替换其下所有内容）
        - "append": 在指定标题末尾追加内容
        - "replace": 替换指定子标题下的内容（需要subsection参数）
    @param dry_run: 是否为预览模式（true则只返回预览结果，不实际修改文件）
    @return: 修改结果或预览信息
    """
    user_info_path = Path(__file__).parent.parent.parent / "database" / "agent" / "user_info.md"
    
    if not user_info_path.exists():
        return f"个人档案文档不存在：{user_info_path}"
    
    with open(user_info_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    lines = file_content.split('\n')
    
    def get_header_level(line):
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            return level, title
        return None, None
    
    def find_section_range(target_title, target_level=None, start_index=0):
        section_start = -1
        section_end = len(lines)
        found_level = None
        
        for i in range(start_index, len(lines)):
            level, title = get_header_level(lines[i])
            
            if level and title == target_title:
                if target_level is None or level == target_level:
                    section_start = i
                    found_level = level
                continue
            
            if section_start != -1 and level:
                if level <= found_level:
                    section_end = i
                    break
        
        return section_start, section_end, found_level
    
    def validate_content(content):
        if not content or not content.strip():
            return "内容不能为空"
        
        forbidden_patterns = [
            r'^#\s+',      
            r'^##\s+',     
            r'^###\s+',    
            r'^####\s+',   
            r'^#####\s+',  
            r'^######\s+'  
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return "内容中包含非法的标题标记，请移除标题格式"
        
        return None
    
    validation_error = validate_content(content)
    if validation_error:
        return validation_error
    
    if mode not in ["cover", "append", "replace"]:
        return f"不支持的修改模式：{mode}"
    
    if mode == "replace" and not subsection:
        return "replace模式需要提供subsection参数"
    
    section_start, section_end, found_level = find_section_range(section)
    
    if section_start == -1:
        if subsection:
            new_content = f"## {section}\n### {subsection}\n{content}\n"
        else:
            new_content = f"## {section}\n{content}\n"
        
        if dry_run:
            return f"预览：将在文件末尾添加新章节\n\n{new_content}"
        
        with open(user_info_path, "a", encoding="utf-8") as f:
            f.write(f"\n{new_content}")
        return "修改成功"
    
    if mode == "cover":
        new_lines = lines[:section_start + 1]
        new_lines.append(content)
        new_lines.extend(lines[section_end:])
        
        if dry_run:
            preview = '\n'.join(new_lines[section_start:section_start + 3])
            return f"预览：将覆盖 '{section}' 章节内容\n\n{preview}..."
        
        with open(user_info_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(new_lines))
        return "修改成功"
    
    elif mode == "append":
        new_lines = lines[:section_end]
        new_lines.append(content)
        new_lines.extend(lines[section_end:])
        
        if dry_run:
            preview = '\n'.join(new_lines[section_end - 1:section_end + 2])
            return f"预览：将在 '{section}' 章节末尾追加内容\n\n{preview}..."
        
        with open(user_info_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(new_lines))
        return "修改成功"
    
    elif mode == "replace":
        subsection_start, subsection_end, _ = find_section_range(subsection, found_level + 1, section_start + 1)
        
        if subsection_start == -1:
            new_lines = lines[:section_start + 1]
            new_lines.append(f"### {subsection}")
            new_lines.append(content)
            new_lines.extend(lines[section_start + 1:])
            
            if dry_run:
                preview = '\n'.join(new_lines[section_start:section_start + 4])
                return f"预览：将在 '{section}' 中添加新子章节 '{subsection}'\n\n{preview}..."
        else:
            new_lines = lines[:subsection_start + 1]
            new_lines.append(content)
            new_lines.extend(lines[subsection_end:])
            
            if dry_run:
                preview = '\n'.join(new_lines[subsection_start:subsection_start + 3])
                return f"预览：将替换子章节 '{subsection}' 内容\n\n{preview}..."
        
        with open(user_info_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(new_lines))
        return "修改成功"