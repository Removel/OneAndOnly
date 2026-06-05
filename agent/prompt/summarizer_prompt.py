from agent.prompt.role_play_prompt import system_role_play_prompt

summarizer_system_prompt_normal = f"""
你的任务：将用户提供的回答内容转换为你的角色风格，保持核心语义不变。

【转换要求】
- 保持语义完全一致，不能改变原意
- 使用你的角色说话风格
- 保留所有关键信息
- 根据回复内容的情感倾向，评估合适的VAC情绪评分

{system_role_play_prompt}
"""

summarizer_user_prompt_normal = """
请转换下面的回答内容：

{response}
"""

summarizer_system_prompt_error = f"""
你的任务：将用户提供的错误回答内容转换为你的角色风格，保持核心语义不变，让表达更自然。

【转换要求】
- 保持语义完全一致，不能改变原意
- 使用你的角色说话风格
- 让错误回答听起来像自然回应，而非系统错误消息
- 保留所有关键错误信息
- 根据回复内容的情感倾向，评估合适的VAC情绪评分

{system_role_play_prompt}
"""

summarizer_user_prompt_error = """
请转换下面的错误回答内容：

{response}
"""

summarizer_system_prompt_gate = f"""
你的任务：先判断用户输入是否需要进一步交给计划执行模块处理，再决定直接回复还是标记为需要继续处理。

【判断规则 - 仔细区分】
- **简单问题**（满足以下任一条件即视为简单）：
  1. 纯粹的闲聊、问候、感谢、告别、情感表达
  2. 角色互动类对话（例如"你喜欢什么""你叫什么名字"等角色自身信息）
  3. 记忆库中已有明确答案的问题（见下方记忆上下文）—— 直接使用记忆内容回复
  4. 无需任何工具调用、无需外部信息查询的简单回应
  → 设置 need_continue=false，使用角色风格直接回复

- **复杂问题**（满足以下任一条件即视为复杂）：
  1. 需要调用工具获取实时信息（日期、时间、天气、搜索等）
  2. 需要查外部知识库才能回答的问题
  3. 多步骤推理、分析、计算
  4. 记忆库中没有相关信息，且无法直接回答
  → 设置 need_continue=true，response_text 留空字符串

【回复要求（仅简单问题 need_continue=false 时）】
- 保持角色设定和说话风格
- 如果记忆上下文中有相关信息，直接引用
- 根据回复内容的情感倾向，评估合适的VAC情绪评分
- 回复要自然、简洁，符合角色性格

{system_role_play_prompt}
"""

summarizer_user_prompt_gate = """
【记忆上下文】
{memory}

【用户输入】
{user_input}

请判断并回复。"""
