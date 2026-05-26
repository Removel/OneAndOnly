# 后端启动指南

## 前置要求

1. Python 3.13
2. 已安装项目依赖

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动后端

### 方法一：直接运行

```bash
python main.py
```

### 方法二：使用 uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 验证启动

启动成功后，访问以下地址验证：

- **API 根路径**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **API 文档**: http://localhost:8000/docs

## API 接口

### Session API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/session/active` | 获取活跃会话 |
| GET | `/api/session/` | 获取所有会话 |
| GET | `/api/session/{session_id}` | 获取单个会话 |
| POST | `/api/session/` | 创建会话 |
| DELETE | `/api/session/{session_id}` | 删除会话 |
| PUT | `/api/session/{session_id}` | 更新会话 |

### Chat API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/chat` | 发送聊天消息 |
| GET | `/api/session/{session_id}/history` | 获取对话历史 |
| DELETE | `/api/session/{session_id}/history` | 清空对话历史 |

## 环境变量

确保在项目根目录下有 `.env` 文件，配置必要的环境变量（如 API Key 等）。

## 数据库

后端启动时会自动初始化数据库：
- 后端数据库：`database/backend/conversation.db`
- Agent 数据库：`database/agent/checkpoints.db`
- 向量数据库：`database/agent/vector_memory.db/`