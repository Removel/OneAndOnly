# One and Only 项目结构

## 目录结构

```
OneAndOnly/
├── .harness/                      # 配置与文档
│   ├── doc/                       # 项目文档
│   │   └── structure.md           # 项目结构说明
│   └── AGENTS.md                  # AI智能体架构文档
│
├── agent/                         # AI智能体核心模块
│   ├── config/                    # 智能体配置文件
│   │   ├── evaluator.yaml         # 评估器配置
│   │   ├── executor.yaml          # 执行器配置
│   │   ├── memory_manager.yaml    # 记忆管理器配置
│   │   ├── planner.yaml           # 规划器配置
│   │   └── summarizer.yaml        # 总结器配置
│   ├── graph/                     # LangGraph图结构
│   │   ├── edge/                  # 边逻辑
│   │   │   ├── route_after_evaluate.py   # 评估后路由
│   │   │   └── route_after_execute.py    # 执行后路由
│   │   ├── node/                  # 节点实现
│   │   │   ├── evaluate.py        # 评估节点
│   │   │   ├── execute.py         # 执行节点
│   │   │   ├── final_output.py    # 最终输出节点
│   │   │   ├── memory_retrieve.py # 记忆检索节点
│   │   │   └── plan.py            # 规划节点
│   │   ├── state.py               # 图状态定义
│   │   └── build_and_compile_graph.py  # 图构建与编译
│   ├── prompt/                    # 提示词模板
│   │   ├── evaluator_prompt.py
│   │   ├── executor_prompt.py
│   │   ├── memory_manager_prompt.py
│   │   ├── planner_prompt.py
│   │   └── summarizer_prompt.py
│   ├── tools/                     # 工具函数
│   │   ├── find_from_mds.py       # 从MD文档查找
│   │   ├── query_from_chromadb.py # 从ChromaDB查询
│   │   ├── write_to_mds.py        # 写入MD文档
│   │   └── write_to_vector_db.py  # 写入向量数据库
│   ├── util/                      # 工具类
│   │   ├── agent_factory.py       # 智能体工厂
│   │   ├── config_loader.py       # 配置加载器
│   │   ├── find_tools.py          # 工具查找
│   │   └── llm_factory.py         # LLM工厂
│   ├── main.py                    # 主入口
│   └── .env                       # 环境变量
│
├── backend/                       # 后端服务模块
│   ├── config/                    # 配置
│   │   └── DatabaseConfig.py      # 数据库配置
│   ├── entity/                    # 实体类
│   │   ├── pojo/                  # 数据对象
│   │   │   ├── Base.py            # 基础类
│   │   │   ├── ConversationHistory.py  # 对话历史
│   │   │   └── Session.py         # 会话
│   │   ├── request/               # 请求对象
│   │   │   ├── ChatRequest.py     # 聊天请求
│   │   │   └── SessionRequest.py  # 会话请求
│   │   ├── response/              # 响应对象
│   │   │   ├── ChatResponse.py    # 聊天响应
│   │   │   └── SessionResponse.py # 会话响应
│   │   └── Result.py              # 结果对象
│   ├── repository/                # 数据访问层
│   │   ├── ChatRepository.py      # 聊天数据访问
│   │   └── SessionRepository.py   # 会话数据访问
│   ├── router/                    # 路由
│   │   ├── ChatRouter.py          # 聊天路由
│   │   └── SessionRouter.py       # 会话路由
│   └── service/                   # 业务逻辑层
│       ├── ChatService.py         # 聊天服务
│       └── SessionService.py      # 会话服务
│
├── custom_model/                  # 自定义模型模块
│   ├── aura/                      # Aura情绪模型
│   └── styler/                    # 风格模型
│       ├── data/                  # 训练数据
│       │   ├── eval.jsonl         # 评估数据
│       │   └── train.jsonl        # 训练数据
│       ├── benchmark.py           # 基准测试
│       ├── convert_to_onnx.py     # ONNX转换
│       ├── download.py            # 模型下载
│       ├── quantize_model.py      # 模型量化
│       ├── service.py             # 模型服务
│       └── train.py               # 模型训练
│
├── test_scripts/                  # 测试脚本
│   ├── agent_test/                # 智能体测试
│   ├── backend_test/              # 后端测试
│   └── custom_model_test/         # 模型测试
│
├── unity/                         # Unity项目
│   └── My project/                # Unity工程目录
│       ├── Assets/                # 资源文件
│       ├── Packages/              # 包配置
│       └── ProjectSettings/       # 项目设置
│
├── .gitignore                     # Git忽略文件
├── requirements.txt               # Python依赖
├── ONNX_USAGE.md                  # ONNX使用说明
├── 人物记忆向量数据库 Chroma 分类体系.md  # 记忆分类体系
├── 状态、节点与边设计.md          # 图结构设计
├── 计划书.md                      # 项目计划书
└── 预测时间线规划.md              # 时间线规划
```

## 模块说明

### agent/
AI智能体核心模块，基于LangGraph实现多智能体协作架构。

### backend/
后端服务模块，提供HTTP接口服务，处理会话和聊天请求。

### custom_model/
自定义模型模块，包含情绪模型和风格模型的训练、推理和部署。

### test_scripts/
测试脚本模块，包含各模块的单元测试和集成测试。

### unity/
Unity可视化模块，实现虚拟人物的表情和动作展示。

## 技术栈

- **AI框架**: LangGraph
- **后端框架**: FastAPI
- **向量数据库**: ChromaDB
- **可视化**: Unity
- **模型格式**: ONNX
- **语言**: Python 3.13, C#