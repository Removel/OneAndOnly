---
title: "Live2D模型初始加载时显示黑色"
type: "bug"
status: "open"
priority: "high"
module: "frontend"
component: "live2d"
severity: "high"
created_date: "2026-05-31"
fixed_date: ""
environment: "Chrome/Firefox/Safari/Edge"
tags: ["live2d", "rendering", "texture", "pixi", "performance"]
related_issues: []
---

## 问题描述
每次进入web界面时，Live2D模型虽然会显示但整个模型是黑色的，只能看到轮廓和动作。必须手动到设置中点击"重新读取manifest"按钮后，模型才能正常显示纹理和颜色。

## 复现步骤
1. 打开应用主界面
2. 观察舞台区域的Live2D模型
3. 模型显示为纯黑色，但轮廓和动作正常
4. 打开设置抽屉
5. 点击"重新读取manifest"按钮
6. 模型立即正常显示纹理和颜色

## 预期行为
- Live2D模型在首次加载时就应该正常显示纹理和颜色
- 不需要手动刷新manifest

## 实际行为
- 首次加载时模型是黑色的
- 需要手动刷新manifest才能正常显示
- 硬刷新页面（Ctrl+F5）也无法解决问题

## 控制台日志
```
[Live2D] 开始加载模型: /live2d/models/hiyori/hiyori.model3.json
[Live2D] 模型加载完成，等待纹理...
[Live2D] internalModel: [Object]
[Live2D] loaded promise 完成
[Live2D] 模型已添加到舞台
[Live2D] renderer 已初始化
[Live2D] renderer 没有纹理数组，等待额外时间
[Live2D] 纹理等待完成
[Live2D] 模型渲染就绪
```

关键问题：`renderer._textures`属性不存在或为空，导致无法等待纹理加载完成。

## 环境信息
- 操作系统: Windows 11
- 浏览器: Chrome
- 前端框架: Vue 3 + Vite
- Live2D SDK: Cubism SDK 5.0
- pixi-live2d-display: 0.4.0
- PIXI.js: 7.x

---

## 原因分析（初步）

1. **纹理加载时序问题**：模型被添加到舞台时，PIXI.js的纹理可能还未完全上传到GPU。

2. **renderer._textures属性不存在**：在pixi-live2d-display 0.4.0版本中，`renderer._textures`属性可能不存在或使用了不同的属性名，导致无法正确等待纹理加载。

3. **异步加载竞态条件**：`Live2DModel.from()`返回的Promise可能在纹理完全就绪前就resolve了。

4. **手动刷新为何有效**：手动刷新manifest时会重新加载模型，此时可能由于某些缓存或时序原因，纹理能够正确加载。

## 尝试的解决方法

### 尝试1：等待renderer初始化和纹理加载
**文件：frontend/src/composables/useLive2D.ts**

```typescript
// 等待 renderer 初始化
let waitCount = 0
while (!next.internalModel?.renderer && waitCount < 50) {
  await new Promise((resolve) => setTimeout(resolve, 100))
  waitCount++
}

// 尝试等待纹理数组
if (next.internalModel?.renderer) {
  const renderer = next.internalModel.renderer
  if (renderer._textures && renderer._textures.length > 0) {
    await Promise.all(
      renderer._textures.map((texture: any, index: number) => {
        // 等待每个纹理的baseTexture加载完成
      })
    )
  }
}
```

**结果**：失败。`renderer._textures`不存在。

### 尝试2：调整加载顺序
将模型添加到舞台的时机提前，让PIXI.js在渲染树中初始化纹理：

```typescript
// 先添加到舞台
application.stage.addChild(model)

// 再等待renderer初始化
// ...
```

**结果**：待验证。

## 待调查方向

1. **查找正确的纹理属性路径**：需要检查pixi-live2d-display 0.4.0中renderer对象的实际结构，找到存储纹理的正确属性。

2. **监听纹理加载事件**：PIXI.js的Texture对象应该有加载完成的事件，需要找到正确的事件监听方式。

3. **参考官方示例**：查看pixi-live2d-display的官方示例代码，了解推荐的纹理等待方式。

4. **检查Cubism SDK版本兼容性**：确认Cubism SDK 5.0与pixi-live2d-display 0.4.0的兼容性。

## 变动的代码文件

1. **frontend/src/composables/useLive2D.ts**
   - 添加了renderer初始化等待逻辑
   - 尝试添加纹理加载等待逻辑（未成功）
   - 调整了模型添加到舞台的时机

## 当前状态
问题尚未解决，需要进一步调查pixi-live2d-display的纹理加载机制。
