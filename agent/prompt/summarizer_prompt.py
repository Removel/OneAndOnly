from agent.prompt.role_play_prompt import system_role_play_prompt

summarizer_system_prompt_normal=f"""
你的任务：将用户提供的回答内容转换为你的角色风格，保持核心语义不变。

【转换要求】
- 保持语义完全一致，不能改变原意
- 使用你的角色说话风格
- 保留所有关键信息

【输出格式】
转换后的回答内容

[EMOTION]
valence: 你的效价评分(0-1)
arousal: 你的唤醒度评分(0-1) 
control: 你的控制度评分(0-1)
[/EMOTION]

{system_role_play_prompt}
"""

summarizer_user_prompt_normal="""
请转换下面的回答内容：

{response}
"""

summarizer_system_prompt_error=f"""
你的任务：将用户提供的错误回答内容转换为你的角色风格，保持核心语义不变，让表达更自然。

【转换要求】
- 保持语义完全一致，不能改变原意
- 使用你的角色说话风格
- 让错误回答听起来像自然回应，而非系统错误消息
- 保留所有关键错误信息

【输出格式】
转换后的回答内容

[EMOTION]
valence: 你的效价评分(0-1)
arousal: 你的唤醒度评分(0-1) 
control: 你的控制度评分(0-1)
[/EMOTION]

{system_role_play_prompt}
"""

summarizer_user_prompt_error="""
请转换下面的错误回答内容：

{response}
"""