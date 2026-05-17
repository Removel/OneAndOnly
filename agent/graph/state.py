from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class GlobalState (TypedDict):
    # 对话核心
    messages: Annotated[list[BaseMessage], add_messages]    #对话历史
    user_input: str                                         #用户当前输入
    response_text: str                                      #模型回复文本

    #认知处理
    plan: str                                               #执行计划
    memory: Optional[str]                                   #召回长期记忆内容

    #技能调用
    # skills相关的内容后面再说
    #skill_names: list[str]                                  #调用的技能名称
    #skill_result: Optional[str]                             #技能执行结果
    tools: list[str]                                        #调用的工具名称列表

    #情绪
    emotion_vac:dict[str, float]                            #情绪VAC：Valence/Arousal/Control ：{'valence': 0.8, 'arousal': 0.3, 'control': 0.5}

    #评估相关
    need_evaluate: bool                                     #是否需要评估
    retry_times: int                                        #重试次数
    error_message: Optional[str]                            #错误信息


class GlobalStafrom:
    pass