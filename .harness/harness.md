# One and Only 项目 - Harness 导航文档

## 📁 本文档用途

本文件夹包含项目的核心文档和规范，本文档作为导航索引，帮助 AI Agent 快速定位所需信息。

## 🎯 快速定位信息

### 项目基础信息
- **项目结构**: 查看 [doc/项目结构.md](./doc/项目结构.md)
- **后端启动**: 查看 [doc/后端启动说明.md](./doc/后端启动说明.md)
- **测试说明**: 查看 [doc/后端测试文件使用说明.md](./doc/后端测试文件使用说明.md)

### 架构设计
- **LangGraph 架构**: 查看 [doc/状态、节点与边设计.md](./doc/状态、节点与边设计.md)
- **记忆系统设计**: 查看 [doc/人物记忆向量数据库 Chroma 分类体系.md](./doc/人物记忆向量数据库 Chroma 分类体系.md)

### 核心规则
1. 所有代码都**必须符合**项目目前的架构设计和相关规范。
2. 你**不能随意添加**抽象层和项目结构
3. 如果有新功能需要添加，你需要先在架构设计中进行修改，然后在代码中实现。
4. 在每次进行代码修改后，你需要在progress文件夹下更新进度文档，记录下当前的开发进度。
5. 你应当在完成某些有价值的任务后，在skills文件夹下添加一个md文档，记录下这个任务的技能点。
6. 你应当在完成某些有价值的任务后，在tools文件夹下添加一个md文档，记录下这个任务的工具点。
7. 每次进行开发时，你需要遵循：**设计-实现-反思-迭代**流程。

### 开发规范
- **后端代码规范**: 查看 [rules/backend_coding_rules.md](./rules/backend_coding_rules.md)
- **Web 前端设计**: 查看 [doc/Web前端设计书.md](./doc/Web前端设计书.md)
- **智能体设计**: 查看 [doc/状态、节点与边设计.md](./doc/状态、节点与边设计.md)
- **记忆系统设计**: 查看 [doc/人物记忆向量数据库 Chroma 分类体系设计.md](./doc/人物记忆向量数据库 Chroma 分类体系设计.md)
- **Bug 记录规范**: 查看 [rules/bug_record_rules.md](./rules/bug_record_rules.md)

## 🏗️ 项目概览

**One and Only** - 基于 LangGraph 的 AI 智能体对话系统

**核心技术栈**: LangGraph, FastAPI, Chroma, Unity + Live2D, LoRA, VAC 情绪模型

**核心流程**: MemoryRetrieve → PlanExecute → Evaluate → FinalOutput

## 🔧 任务介绍

### bug体现与修复
- bug 体现: 有两个文件夹，一个是bug_report_images，一个是issue。bug_report_images文件夹下包含bug的截图，issue文件夹下包含bug的详细描述。

### 进度
- 项目进度: 查看当前文件夹下的progress文件夹，其中包含一个md文档，记录了项目的开发进度。

### 工具
- 该文件夹下的tools文件夹，会包含一些工具脚本，用于辅助开发。（注：目前还没有工具，日期2026-05-30）

### 技能
- 该文件夹下的skills文件夹，会包含一些技能文档，用于记录项目的技能点。
- 你应当在完成某些有价值的任务后，在skills文件夹下添加一个md文档，记录下这个任务的有价值的地方。命名格式应当为：yyyy-MM-dd_技能总结描述.md

## 📂 文档目录结构

```
.harness/
├── harness.md                          # 本导航文档
├── doc/                                # 详细文档目录
├── rules/                              # 代码规范目录
├── skills/                             # 技能文档存储目录
├── tools/                              # 工具文档存储目录
├── progress/                           # 项目进度文档目录
└── bugs/                               # Bug报告存储目录
    ├── bug_report_images/              # Bug截图存储目录
    └── issue/                          # Bug详细描述文档目录
```

---

**使用建议**: AI Agent 在执行任务前，先根据本文档定位到相关详细文档，获取完整信息后再开始工作。