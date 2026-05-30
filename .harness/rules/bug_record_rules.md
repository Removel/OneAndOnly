# Bug 记录规范

## Bug 反馈流程

### 1. 发现 Bug
- 详细记录复现步骤
- 截图或录屏记录或错误日志记录问题现象
- 记录出现问题的环境信息（浏览器、操作系统、软件版本等）

### 2. Bug 文档结构
每个 Bug 报告必须包含以下 YAML 头部信息：

```yaml
---
title: "Bug 标题"
type: "bug"
status: "open"          # open, closed, in-progress
priority: "medium"      # low, medium, high, critical
module: "frontend"      # frontend, backend, agent
component: "component-name"
severity: "medium"      # low, medium, high, critical
created_date: "YYYY-MM-DD"
fixed_date: ""          # 修复日期
environment: ""         # 运行环境
tags: ["tag1", "tag2"]  # 标签
related_issues: []      # 相关问题编号
---
```

### 3. 内容要求
- **问题描述**：清晰描述问题现象及影响
- **复现步骤**：详细列出复现问题的操作步骤
- **预期行为**：描述期望的正常行为
- **实际行为**：描述实际发生的问题
- **问题截图**：提供相关截图或录屏

### 4. Bug 分类标准

#### 优先级 Priority
- **low**: 对用户体验影响较小，可延后处理
- **medium**: 影响部分功能，建议处理
- **high**: 严重影响核心功能，需尽快处理
- **critical**: 导致系统崩溃或数据丢失，需立即处理

#### 严重程度 Severity
- **low**: 界面轻微问题，不影响功能使用
- **medium**: 功能部分异常，但有替代方案
- **high**: 主要功能不可用
- **critical**: 系统崩溃或安全漏洞

### 5. 状态流转
- **open**: 新提交的 Bug
- **in-progress**: 正在处理中
- **resolved**: 已修复待验证
- **closed**: 已验证关闭
- **wontfix**: 不予修复
- **duplicate**: 重复问题

### 6. 标签规范
常用标签：
- `ui`: 界面问题
- `functionality`: 功能缺陷
- `performance`: 性能问题
- `security`: 安全问题
- `compatibility`: 兼容性问题
- `crash`: 崩溃问题
- `typo`: 错别字
- `enhancement`: 功能增强

### 7. 解决回答
在解决了bug之后，需要执行以下步骤：
1. 更新对应md文档顶部yaml
2. 在对应md文档底部添加这些内容：1、原因分析 2、解决方法 3、变动的代码文件

### 8. 你必须在人工确认或者通过测试代码验证确认问题已解决之后，才能将状态改为closed，并对解决方法进行总结和记录