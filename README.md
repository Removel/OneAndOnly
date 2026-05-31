# One and Only

<div align="center">

![One and Only](https://img.shields.io/badge/One_and_only-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.13+-green)
![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688)
![License](https://img.shields.io/badge/License-MIT-yellow)

**基于多智能体架构的AI对话系统，集成Live2D虚拟角色与情绪可视化**

[功能特性](#功能特性) • [快速开始](#快速开始) • [技术架构](#技术架构) • [项目结构](#项目结构) • [开发指南](#开发指南)

</div>

---

## 📖 项目简介

One and Only 是一个创新的AI智能对话系统，采用基于 LangGraph 的多智能体协作架构，结合 Live2D 虚拟角色技术，提供沉浸式的交互体验。系统通过情绪向量驱动虚拟角色的表情和动作，实现更加自然和富有表现力的人机对话。

### 核心亮点

- 🤖 **多智能体协作**: 基于 LangGraph 构建的复杂智能体网络，支持记忆管理、计划执行等功能
- 🎭 **Live2D 虚拟角色**: 集成 Live2D Cubism 4 运行时，提供流畅的2D角色动画
- 💭 **情绪可视化**: 通过 VAC (Valence/Arousal/Control) 三维情绪向量驱动角色表情和氛围
- 🎨 **现代化前端**: Vue 3 + TypeScript + Naive UI 构建的响应式界面
- ⚡ **高性能后端**: FastAPI 异步架构，支持流式响应和实时通信
- 🧠 **向量记忆**: 基于 ChromaDB 的长期记忆系统，支持上下文理解

---

## ✨ 功能特性

### 对话系统
- 智能对话生成与上下文理解
- 会话历史管理与持久化
- 流式响应支持
- 多轮对话状态追踪

### 虚拟角色
- Live2D 模型渲染与动画
- 表情与动作实时驱动
- 氛围色动态变化
- 模型热替换支持

### 情绪系统
- 三维情绪向量 (VAC) 分析
- 情绪状态可视化
- 基于情绪的响应风格调整
- 情绪历史记录

### 用户界面
- 响应式设计（桌面/平板/手机）
- 暗色/亮色主题切换
- 会话管理面板
- 实时连接状态监控

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.13+
- **Node.js**: 20.0+
- **pnpm**: 9.0+

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/Removel/OneAndOnly.git
cd OneAndOnly
```

#### 2. 后端设置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（根据需要修改 .env.example 文件，并重命名为 .env）
cp .env.example .env
```

#### 3. 前端设置

```bash
cd frontend

# 安装依赖
pnpm install

# 配置环境变量
cp .env.development.example .env.development
cp .env.production.example .env.production
```

#### 4. 启动服务

**启动后端服务**:

```bash
# 在项目根目录
python -m backend.main
```

后端服务将在 `http://localhost:8000` 启动

**启动前端开发服务器**:

```bash
# 在 frontend 目录
pnpm dev
```

前端服务将在 `http://localhost:5173` 启动

#### 5. 访问应用

打开浏览器访问 `http://localhost:5173` 即可开始使用 One and Only。

---

## 🏗️ 技术架构

### 后端技术栈

- **框架**: FastAPI 0.136+
- **AI框架**: LangGraph 1.2+ + LangChain 1.3+
- **数据库**: SQLAlchemy 2.0+ + ChromaDB 1.5+
- **向量存储**: ChromaDB
- **模型**: PyTorch 2.11+ + Transformers 4.57+
- **ASGI服务器**: Uvicorn

### 前端技术栈

- **框架**: Vue 3.5+ (Composition API)
- **语言**: TypeScript 5.6+
- **构建工具**: Vite 6.0+
- **UI组件**: Naive UI 2.40+
- **状态管理**: Pinia 2.2+
- **路由**: Vue Router 4.4+
- **HTTP客户端**: Axios 1.7+
- **样式**: UnoCSS 0.65+
- **Live2D**: pixi.js 6.5+ + pixi-live2d-display 0.4.0

### AI智能体架构

- **多智能体系统**: 基于 LangGraph 的图结构
- **记忆管理**: 向量数据库 + 检索增强生成
- **工具系统**: 可扩展的工具函数库
- **状态管理**: 基于检查点的状态持久化

---

## 📁 项目结构

```
one-and-only/
├── agent/                      # AI智能体核心模块
│   ├── config/                 # 智能体配置
│   ├── graph/                  # LangGraph图结构
│   │   ├── edge/              # 边逻辑
│   │   └── node/              # 节点实现
│   ├── hooks/                 # 中间件钩子
│   ├── prompt/                # 提示词模板
│   ├── tools/                 # 工具函数
│   └── util/                  # 工具类
│
├── backend/                    # 后端服务模块
│   ├── config/                # 配置管理
│   ├── entity/                # 实体类
│   ├── exception/             # 异常处理
│   ├── repository/            # 数据访问层
│   ├── router/                # 路由层
│   ├── service/               # 业务逻辑层
│   └── util/                  # 工具类
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/              # API接口
│   │   ├── components/       # Vue组件
│   │   ├── composables/      # 组合式函数
│   │   ├── router/           # 路由配置
│   │   ├── services/         # 业务服务
│   │   ├── stores/           # Pinia状态管理
│   │   ├── styles/           # 样式文件
│   │   ├── types/            # TypeScript类型
│   │   └── views/            # 页面视图
│   ├── dist/                 # 构建输出
│   └── package.json          # 前端依赖
│
├── custom_model/              # 自定义模型模块
│   ├── aura/                 # 情绪模型
│   └── styler/               # 风格模型
│
├── database/                  # 数据库存储
│   ├── agent/                # Agent相关数据库
│   └── backend/              # 后端数据库
│
├── test_scripts/             # 测试脚本
│   ├── agent_test/          # 智能体测试
│   ├── backend_test/        # 后端测试
│   └── custom_model_test/   # 模型测试
│
├── unity/                    # Unity可视化模块
│   └── My project/          # Unity工程
│
├── .harness/                 # 配置与文档
├── requirements.txt          # Python依赖
├── AGENTS.md                 # AI智能体架构文档
└── README.md                 # 项目说明
```

---

## 🛠️ 开发指南

### 后端开发

#### 运行测试

```bash
# 运行所有测试
python -m pytest test_scripts/

# 运行特定模块测试
python -m pytest test_scripts/backend_test/
```

#### 代码规范

项目遵循以下编码规范：
- 遵循 PEP 8 Python编码规范
- 使用类型注解
- 异步编程优先
- 分层架构（Router-Service-Repository）

详细规范请参考 `.harness/rules/`

### 前端开发

#### 开发命令

```bash
# 开发模式
pnpm dev

# 类型检查
pnpm typecheck

# 代码检查
pnpm lint

# 代码格式化
pnpm format

# 构建生产版本
pnpm build
```

#### 组件开发

- 使用 `<script setup>` 语法
- 遵循 Composition API 最佳实践
- 使用 TypeScript 进行类型检查
- 组件命名使用 PascalCase

详细设计规范请参考 `.harness/doc/Web前端设计书.md`

### Live2D 模型配置

Live2D 模型文件放置在 `frontend/dist/live2d/models/` 目录下。

支持的模型格式：
- Cubism 4.0 (.moc3, .model3.json)
- 包含动作、表情、物理配置

模型配置示例：
```json
{
  "model": "path/to/model.model3.json",
  "motions": {
    "idle": ["path/to/motion1.motion3.json"],
    "tap": ["path/to/motion2.motion3.json"]
  }
}
```

---

## 🔧 配置说明

### 后端配置

主要配置文件：
- `.env` - 环境变量配置
- `backend/config/` - 应用配置
- `agent/config/` - 智能体配置
- 前端页面网页配置（启动后在浏览器上根据指引设置）

关键配置项：
```env
# API配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./database/backend/app.db

# AI模型配置
多个智能体配置可根据自身需求进行配置。

# 向量数据库配置
CHROMA_PERSIST_DIR=./database/agent/vector_memory.db
```

### 前端配置

主要配置文件：
- `frontend/.env.development` - 开发环境配置
- `frontend/.env.production` - 生产环境配置

关键配置项：
```env
# API地址
VITE_API_BASE_URL=http://localhost:8000

# Live2D配置
VITE_LIVE2D_MODEL_PATH=/live2d/models/
```

---

## 📊 API文档

启动后端服务后，访问以下地址查看API文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 主要API端点

- `POST /api/chat` - 发送聊天消息
- `GET /api/chat/history/{session_id}` - 获取对话历史
- `POST /api/session` - 创建新会话
- `GET /api/session` - 获取所有会话
- `DELETE /api/session/{session_id}` - 删除会话
- `GET /health` - 健康检查

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码贡献规范

- 遵循项目的代码风格指南
- 添加必要的测试
- 更新相关文档
- 确保所有测试通过

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📮 联系方式

- 项目主页: [https://github.com/Removel/OneAndOnly](https://github.com/Removel/OneAndOnly)
- 问题反馈: [Issues](https://github.com/Removel/OneAndOnly/issues)
- 邮箱: removel0202@163.com

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star**

Made with ❤️ by One and Only Team

</div>