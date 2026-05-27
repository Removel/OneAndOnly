# 后端测试说明

## 测试文件说明

### 1. test_database.py
数据库测试文件，测试数据库的连接、初始化和基本操作。

**测试内容：**
- 数据库配置信息显示
- 数据库初始化
- 创建会话
- 查询会话（单个、所有、活跃）
- 更新会话状态
- 软删除会话

**运行方式：**
```bash
python test_scripts/backend_test/test_database.py
```

### 2. test_api.py
API接口测试文件，测试所有后端API接口的功能。

**测试内容：**
- API连接测试
- 健康检查接口
- 会话API（创建、查询、更新、删除）
- 聊天API（发送消息、获取历史、清空历史）
- 错误处理测试

**运行方式：**
```bash
python test_scripts/backend_test/test_api.py
```

**注意：** 运行API测试前需要先启动后端服务：
```bash
python backend/main.py
```
或
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. test_session_repository.py
SessionRepository单元测试文件，使用pytest框架。

**测试内容：**
- 创建会话
- 根据ID查询会话
- 获取活跃会话
- 获取所有会话
- 删除会话
- 更新会话
- 归档会话
- 更新最后活动时间

**运行方式：**
```bash
pytest test_scripts/backend_test/test_session_repository.py -v
```

### 4. test_main.py
测试主入口文件，提供交互式测试界面。

**功能：**
- 选择性运行测试（数据库测试、API测试、全部测试）
- 自动启动/停止后端服务
- 测试结果汇总

**运行方式：**
```bash
python test_scripts/backend_test/test_main.py
```

## 测试覆盖范围

### 数据库测试
- ✓ 数据库连接和配置
- ✓ 数据库初始化
- ✓ 会话创建
- ✓ 会话查询
- ✓ 会话更新
- ✓ 会话软删除

### API接口测试
- ✓ 根路径接口
- ✓ 健康检查接口
- ✓ 创建会话 (POST /api/session/)
- ✓ 获取所有会话 (GET /api/session/)
- ✓ 获取活跃会话 (GET /api/session/active)
- ✓ 获取单个会话 (GET /api/session/{session_id})
- ✓ 更新会话 (PUT /api/session/{session_id})
- ✓ 删除会话 (DELETE /api/session/{session_id})
- ✓ 发送聊天消息 (POST /api/chat)
- ✓ 获取对话历史 (GET /api/session/{session_id}/history)
- ✓ 清空对话历史 (DELETE /api/session/{session_id}/history)
- ✓ 错误处理

## 依赖要求

确保已安装以下依赖：
```bash
pip install requests pytest
```

## 测试结果

所有测试应该能够正常通过，如果遇到问题：

1. **数据库测试失败：**
   - 检查数据库目录权限
   - 确保没有其他进程占用数据库文件

2. **API测试失败：**
   - 确保后端服务已启动
   - 检查端口8000是否被占用
   - 查看后端服务日志

3. **单元测试失败：**
   - 确保pytest已正确安装
   - 检查Python版本兼容性

## 注意事项

1. 运行API测试时，聊天功能可能需要较长时间响应，建议设置合理的超时时间
2. 测试过程中会创建测试数据，可能会影响数据库中的实际数据
3. 建议在测试环境中运行，避免在生产环境中执行测试
4. 聊天API测试需要Agent模块正常工作，如果Agent模块未配置，聊天测试可能会失败