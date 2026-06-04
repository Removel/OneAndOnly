# 后端层代码设计规范：

## 一、分层职责

### 1. Repository / Mapper 层
- 只负责数据库交互
- 如果service需要的是抽象实体，则repository/mapper层必须返回**抽象实体（Entity）**
- 如果service需要的是基础类型，则repository/mapper层必须返回**基础类型**
- 不允许返回 dict / map / 单个数字 / 普通字符串
- **更新、增加、删除等操作**对应的函数应当**无返回值**，如果出现问题则应当抛出异常由全局异常处理器处理
- 空对象和不存在对象的返回状态应该分开
- 不处理业务异常，数据库异常直接向上抛出

### 2. Service 层
- 所有业务逻辑写在这里
- 只接收：
  - 抽象实体（Entity）
  - 或关键基础类型参数（如 id、email）
- 必须进行参数验证（格式、存在性、权限等）
- 业务逻辑处理有异常时直接抛出明确的业务异常（如 ValidationException、NotFoundException），应当定义好业务异常对应的常见错误码和业务错误的异常错误信息
- 返回类型只能是：抽象实体（Entity）或基础类型
- 不允许返回 Response / Result 等响应包装类
- service在非业务流程设定要使用try-catch异常的时候不可以使用try语句捕获异常并处理
- 事务边界由 Service 层注解控制

### 3. Controller / Router 层
- 只负责协议转换
- 接收多种 Request 类
- 将 Request 参数**拆解、转换**成 Service 需要的抽象实体或关键参数
- 调用 Service
- 将 Service 返回的抽象实体**封装成 Response 类**返回
- 不允许包含任何业务逻辑
- 不允许做参数校验（校验是 Service 的事）
- 不允许出现 try-except
- 如果整个业务流程都正常，返回的响应应当是定义好的Result类，其中data字段为业务流程类封装成的Response类。

## 二、异常处理（统一规范）

- 代码中**禁止写 try-except 除非有明确的补偿逻辑**（如回滚后发消息）
- 业务异常直接在 Service 层抛出
- 所有未捕获的异常由**全局异常处理器**统一处理
- 全局异常处理器根据异常类型返回不同的错误码和错误信息，在本次请求直接返回响应，不走业务后面的流程
- Repository 层的数据库异常（如唯一键冲突、连接失败）直接抛出，由全局异常处理器处理

## 三、空值处理

- 数据库查询不存在和空时要分开，即is None 和is empty要分开。防止两种情况竞态
- Service 层遇到 None / null → 按业务决定：抛 NotFoundException 或正常处理
- Controller 层不允许将 None 转成空对象再返回

## 四、禁止事项（违反即视为错误代码）

- ❌ 禁止在 Repository 返回 dict / map / 普通数字
- ❌ 禁止 Service 返回 Response / Result 对象
- ❌ 禁止 Controller 做业务校验
- ❌ 禁止任何地方无意义或者随意地 try-except
- ❌ 禁止查询为空和不存在返回情况混用

