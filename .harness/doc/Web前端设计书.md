# One and Only · Web 前端设计书

> 版本：v0.3
> 日期：2026-05-27
> 适用范围：`frontend/` 模块全部前端工程

## 一、定位与目标

### 1.1 模块定位
Web 前端是 One and Only 的**独立可视化与交互模块**，与 `unity/` 模块**地位平等**：

- 二者面向同一套后端 API（`backend/`），共享同一套 Agent 心智层（`agent/`）。
- 二者不是替代关系，而是**两条并行的客户端**：Web 端面向桌面浏览器与移动浏览器，Unity 端面向独立桌面运行时。
- Web 端长期维护，作为项目的主要展示窗口与日常迭代载体；Unity 端在其技能成熟后承担更重的 3D / 沉浸式表现职责。

### 1.2 设计目标
- **独立可交付**：仅依赖后端 HTTP API，无需 Unity 在场即可完整运行。
- **L2D 优先**：必须在前端页面内渲染 Live2D 模型，模型可通过配置热替换，不需要改源码。
- **情绪可视化**：以 Agent 输出的 VAC（Valence / Arousal / Control）三维情绪向量驱动 L2D 表情、氛围色与状态指示器。
- **响应式**：桌面（≥1280px）、平板（≥768px）、手机（≥360px）三档断点全部可用。
- **二次元 / 清新 / 暖色**：整体氛围向暖色与高饱和清新色靠拢，禁用纯黑、深蓝、冷灰为主色。
- **现代工程规范**：TypeScript、ESLint、Prettier、模块化、按职责分层，与后端 `backend_coding_rules.md` 的工程严肃度对齐。

### 1.3 非目标
- 不做账号 / 登录 / 多用户隔离（个人项目，单用户使用）。
- 不做 SSR、PWA、桌面壳（Tauri / Electron）。
- 本期不实现语音输入与 TTS，但**预留入口与占位 UI**。
- 本期不实现风格 / LoRA 切换，但**在设置面板预留入口**。

---

## 二、技术选型

| 维度 | 选型 | 理由 |
|------|------|------|
| 框架 | **Vue 3 + `<script setup>` + Composition API** | 渐进、文档完整、个人开发友好 |
| 语言 | **TypeScript** | 与后端 DTO 强对齐，编辑器智能提示 |
| 构建 | **Vite** | 启动与 HMR 极快 |
| 路由 | **Vue Router 4** | 主路由仅 2~3 条 |
| 状态管理 | **Pinia** | 会话、消息流、情绪、L2D 状态跨组件共享 |
| HTTP | **Axios** | 拦截器统一解包后端 `Result<T>` |
| UI 组件库 | **Naive UI** | 主题系统灵活，可整体定制为暖色二次元，不像 Element Plus 那么“企业风” |
| 样式方案 | **UnoCSS** + CSS 变量主题 | 原子类做布局，主题色 / 氛围色用 CSS 变量动态驱动 |
| 字体 | 系统中文圆体（`HarmonyOS Sans / 阿里巴巴普惠体 / 站酷快乐体` 任一）+ Web Font 兜底 | 与二次元清新调性匹配 |
| L2D 渲染 | **pixi.js v7 + pixi-live2d-display**（Cubism 4 运行时） | 浏览器侧最成熟的 Live2D 方案，支持 motion / expression / 物理 |
| 动画 | **@vueuse/motion** + CSS keyframes | 卡片浮入、气泡弹出、氛围色过渡 |
| 图标 | **iconify**（多套二次元风可选） | 不绑死单一图标库 |
| 包管理 | **pnpm** | 工作区与依赖锁更稳 |
| 工具链 | ESLint + Prettier + Stylelint + simple-git-hooks + lint-staged | 现代工程标配 |
| 单测（可选） | Vitest + Vue Test Utils | 仅对 composables 与 service 做轻量测试 |

> 选型原则：每个槽位主选唯一，避免多 UI 库混用造成视觉漂移。

---

## 三、整体架构

### 3.1 在系统中的位置
```
┌─────────────────────────┐    ┌─────────────────────────┐
│   frontend/  (Vue3)     │    │   unity/   (Unity)      │
│   桌面 / 移动浏览器      │    │   桌面运行时             │
└────────────┬────────────┘    └────────────┬────────────┘
             │ HTTP / JSON                  │ HTTP / JSON
             └─────────────┬────────────────┘
                           ▼
              ┌──────────────────────────┐
              │   backend/  (FastAPI)    │
              │   /api/session/*         │
              │   /api/chat              │
              └────────────┬─────────────┘
                           ▼
              ┌──────────────────────────┐
              │   agent/  (LangGraph)    │
              │   MemoryRetrieve →       │
              │   PlanExecute →          │
              │   Evaluate → FinalOutput │
              └──────────────────────────┘
```

### 3.2 前端内部分层
```
 View   (页面 / 组件)        ←  仅展示与交互
   ↓
 Store  (Pinia)               ←  跨组件共享状态
   ↓
 Service (业务编排)            ←  组合多次 API、状态切换
   ↓
 Api    (协议层 + Result 解包) ←  axios 实例 + 拦截器
   ↓
 Backend (FastAPI)
```

- View 不直接调 axios；只读 Store 或调用 Service。
- Service 不持状态，只编排。
- Api 不含业务，只做协议翻译与错误归一化。
- Store 是状态唯一来源（消息流、会话、情绪、L2D 状态、UI 偏好）。

---

## 四、目录结构

约定：Web 前端代码直接位于仓库根的 `frontend/` 目录下，与 `backend/`、`unity/`、`agent/` 平级。

```
frontend/
├── index.html
├── package.json
├── pnpm-lock.yaml
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── uno.config.ts
├── .eslintrc.cjs
├── .prettierrc
├── .stylelintrc.cjs
├── .env.development
├── .env.production
├── public/
│   ├── favicon.svg
│   └── live2d/                          # L2D 模型资源根目录（可热替换）
│       ├── manifest.json                # 模型清单（详见 §7.3）
│       └── <model_name>/
│           ├── <model_name>.model3.json
│           ├── textures/
│           ├── motions/
│           └── expressions/
└── src/
    ├── main.ts
    ├── App.vue
    ├── router/
    │   └── index.ts
    ├── api/
    │   ├── http.ts                      # axios 实例 + Result 拦截器
    │   ├── session.ts
    │   └── chat.ts
    ├── types/
    │   ├── result.ts
    │   ├── session.ts
    │   ├── chat.ts
    │   ├── message.ts
    │   └── live2d.ts
    ├── stores/
    │   ├── session.ts                   # 会话列表 / 当前会话
    │   ├── chat.ts                      # 消息流 + 节点执行状态
    │   ├── emotion.ts                   # VAC 与派生表情
    │   ├── live2d.ts                    # 当前模型、加载状态
    │   └── ui.ts                        # 主题、抽屉开关、移动端态
    ├── services/
    │   ├── chatService.ts
    │   ├── sessionService.ts
    │   └── live2dService.ts             # 模型清单加载 / 切换
    ├── composables/
    │   ├── useEmotionDriver.ts          # VAC → 表情 / 氛围色
    │   ├── useResponsive.ts             # 断点 hook
    │   ├── useAutoScroll.ts
    │   └── useNodeStatus.ts             # “回忆中 / 思考中 / 回答中”状态机
    ├── components/
    │   ├── layout/
    │   │   ├── AppTopBanner.vue         # 顶部 banner（设置/对话列表/帮助/介绍）
    │   │   ├── ChatPanel.vue            # 右侧对话面板容器
    │   │   ├── StagePanel.vue           # 左侧 L2D 舞台容器
    │   │   └── MobileDrawer.vue         # 移动端抽屉（承载会话列表 / 设置）
    │   ├── stage/
    │   │   ├── Live2DCanvas.vue         # pixi + live2d 渲染
    │   │   ├── StageBackground.vue      # 背景图层（含氛围色）
    │   │   └── EmotionAura.vue          # 角色周围光晕，由 VAC 驱动
    │   ├── chat/
    │   │   ├── ChatActionBar.vue        # 对话操作 banner（新建/清空/导出）
    │   │   ├── MessageList.vue
    │   │   ├── MessageBubble.vue
    │   │   ├── TimestampDivider.vue
    │   │   ├── NodeStatusBar.vue        # 回忆中 / 思考中 / 回答中
    │   │   ├── ChatInput.vue            # 多行输入 + 滑动
    │   │   └── ChatToolbar.vue          # 输入框下方按钮区（含语音占位、表情、附件预留）
    │   ├── session/
    │   │   ├── SessionListPanel.vue
    │   │   └── SessionItem.vue
    │   ├── settings/
    │   │   ├── SettingsDrawer.vue
    │   │   ├── ModelSwitcher.vue        # L2D 模型切换
    │   │   └── DebugPanel.vue           # 显示 VAC / retry_times
    │   └── feedback/
    │       ├── ConnectionBanner.vue     # 后端不可达提示
    │       └── EmotionBadge.vue
    ├── views/
    │   ├── HomeView.vue                 # 主页面（主体即 §六 布局）
    │   └── HelpView.vue                 # 帮助 / 介绍
    ├── styles/
    │   ├── theme.css                    # 暖色二次元主题变量
    │   ├── tokens.css                   # 间距 / 圆角 / 阴影 token
    │   └── reset.css
    └── assets/
        ├── images/
        └── icons/
```

---

## 五、UI 风格规范

### 5.1 整体调性
- **二次元、清新、暖色**：整体走“奶油 + 樱粉 + 蜜橙 + 薄荷点缀”的暖色清新组合；禁用纯黑、深蓝、冷灰作为主色。
- 视觉关键词：圆角、柔和阴影、轻微毛玻璃、微动效、低饱和暖色背景配高饱和点缀色。
- 不使用强烈对比的“暗色模式”作为主题，仅作为可选项保留接口（默认不启用）。

### 5.2 颜色 Token（写入 `styles/theme.css` 作为 CSS 变量）

```css
:root {
  /* 背景层（由浅到深，全部偏暖） */
  --color-bg-base:    #FFF8F1;   /* 奶油底 */
  --color-bg-soft:    #FFEFE2;   /* 浅蜜橙 */
  --color-bg-card:    #FFFFFFEE; /* 卡片背景，半透明白 */
  --color-bg-elevated:#FFE4D6;   /* 侧栏 / 抽屉 */

  /* 主色（樱粉系） */
  --color-primary:        #FF8FA3;
  --color-primary-soft:   #FFC2CE;
  --color-primary-strong: #F46A86;

  /* 辅助色 */
  --color-accent-peach: #FFB089;   /* 蜜橙 */
  --color-accent-cream: #FFD9A8;   /* 暖奶黄 */
  --color-accent-mint:  #B8E0C2;   /* 薄荷点缀 */
  --color-accent-lilac: #E5C8F0;   /* 淡紫点缀 */

  /* 文本 */
  --color-text-primary:  #5A3E36;  /* 暖棕，作为主要文字色，避免冷黑 */
  --color-text-secondary:#8A6A5E;
  --color-text-inverse:  #FFFFFF;

  /* 状态色 */
  --color-success: #7DC592;
  --color-warning: #F2B65C;
  --color-danger:  #E97A7A;

  /* 圆角 / 阴影 */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 22px;
  --radius-pill: 999px;
  --shadow-card: 0 6px 18px rgba(244, 106, 134, 0.10);
  --shadow-float: 0 12px 32px rgba(244, 106, 134, 0.16);

  /* 情绪驱动变量（默认中性，运行时被 useEmotionDriver 改写） */
  --aura-h: 18;     /* 色相，0~360 */
  --aura-s: 70%;    /* 饱和度 */
  --aura-l: 80%;    /* 亮度 */
  --aura-a: 0.35;   /* 透明度 */
}
```

### 5.3 排版与组件细节
- **字体**：默认 `"HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei", system-ui`，正文 14~15px，标题加重；对话气泡使用 16px、行高 1.6。
- **气泡**：用户气泡为 `--color-primary-soft` → `--color-accent-peach` 渐变 + 右上突起；AI 气泡为 `--color-bg-card` + 极浅 mint 描边 + 左上突起；圆角 `--radius-lg`。
- **按钮**：默认填充 `--color-primary`，hover 提升 `--color-primary-strong`，禁用态降饱和。
- **图标**：圆润风格优先（`carbon` / `solar` / `mingcute`）。
- **动效**：消息进入 0.25s 弹性上浮；状态切换氛围色 0.6s ease；L2D 表情切换 0.3s 过渡。

---

## 六、UI 布局（按主页面示意图）

### 6.1 桌面布局（≥1280px）
完全对应 `.harness/doc/主页面示意图.png`：

```
┌────────────────────────────────────────────────────────────────────────────┐
│  AppTopBanner    Logo    标题    [设置] [对话列表] [帮助] [介绍]           │
├──────────────────────────────────────────────┬─────────────────────────────┤
│                                              │  ChatActionBar              │
│                                              │  [新建对话] [清空记录] [导出]│
│                                              ├─────────────────────────────┤
│                                              │                             │
│                                              │   MessageList               │
│                                              │   ┌──────────────┐          │
│                                              │   │ AI 气泡       │          │
│            StagePanel                        │   └──────────────┘          │
│  ┌─────────────────────────────────────┐     │           ┌──────────────┐  │
│  │  StageBackground (暖色渐变 + 氛围色) │     │           │ User 气泡     │  │
│  │                                     │     │           └──────────────┘  │
│  │      Live2DCanvas (角色立绘)         │     │                             │
│  │                                     │     │   ...                       │
│  │           EmotionAura(光晕)          │     │                             │
│  └─────────────────────────────────────┘     ├─────────────────────────────┤
│                                              │  NodeStatusBar              │
│                                              │  [回忆中 / 思考中 / 回答中] │
│                                              ├─────────────────────────────┤
│                                              │  ChatInput (多行 / 可滑动)   │
│                                              │  ┌────────────────────────┐ │
│                                              │  │ 在这里输入对话...      │ │
│                                              │  └────────────────────────┘ │
│                                              │  ChatToolbar                │
│                                              │  [🎤 语音(占位)] [😊][📎] [发送]│
└──────────────────────────────────────────────┴─────────────────────────────┘
```

约束：
- 顶部 `AppTopBanner` 高度 56~64px，固定。
- 左侧 `StagePanel` 占比约 60%（最小 720px），右侧 `ChatPanel` 固定宽度 420~480px。
- L2D 舞台带背景层，背景图与角色分离，便于以后单独换背景。
- 对话区域内部上下结构固定为：操作 banner / 消息流（自适应高度）/ 节点状态条 / 输入区。
- 右下角 `ChatToolbar` 预留：语音输入按钮（禁用 + tooltip “即将上线”）、表情、附件、发送。

### 6.2 平板布局（768px ~ 1279px）
- 顶栏不变。
- L2D 舞台与对话面板上下排列：舞台收缩为顶部 40vh 的横屏区域；对话面板撑满下方。
- “对话列表”入口移入顶栏菜单；点击后从右侧滑出 `MobileDrawer`。

### 6.3 手机布局（360px ~ 767px）
- L2D 角色作为**背景层**（半透明遮罩 + 暖色叠加），对话面板浮于其上，整体高度铺满视口。
- 顶栏精简为 logo + 汉堡菜单；菜单内含设置、对话列表、帮助、介绍。
- 输入框与工具栏吸底，气泡列表占满中间区域，节点状态条作为输入框上方一行小标签。
- L2D 关键互动（点击触发动作）依然可用，但 motion 数量自动降级为基础集，避免移动端性能问题。

### 6.4 顶部 banner（AppTopBanner）
按照示意图右上的注释，必须包含 4 个入口：

| 入口 | 行为 |
|------|------|
| 设置 | 打开 `SettingsDrawer`，含 L2D 模型切换（本期）+ 风格切换（本期仅占位入口） |
| 对话列表 | 打开 `SessionListPanel`，桌面右侧滑入抽屉，移动端全屏 |
| 帮助 | 跳转 `HelpView`，介绍交互方式 |
| 介绍 | 跳转 `HelpView` 的“关于本项目”分页 |

### 6.5 对话操作 banner（ChatActionBar）
- 新建对话：调用 `createSession` → 自动切换。
- 清空记录：二次确认后调用 `DELETE /api/session/{id}/history`。
- 导出对话：将当前消息流导出为 Markdown / JSON 文件（前端本地下载，无后端依赖）。

### 6.6 消息气泡（MessageBubble）
组成：角色头像 + 气泡 + 时间戳。
- 用户头像：默认占位，预留替换接口。
- AI 头像：与 L2D 模型同源（取模型清单 `avatar` 字段）。
- 时间戳：相对时间（“刚刚 / 3 分钟前 / 今天 14:21”），由前端格式化。
- 长按 / 右键：复制、重发、删除（删除仅前端，不调后端）。

### 6.7 节点状态条（NodeStatusBar）
对应示意图“显示当前对话模型执行状态”：
- 状态枚举：`idle / recalling(回忆中) / thinking(思考中) / answering(回答中) / failed`。
- 状态来源：发送消息后由 `chatService` 在 axios 请求生命周期中切换；当前后端是同步返回，状态在前端按顺序模拟（idle → recalling → thinking → answering → idle），单段时长可配置。
- 后续若后端改为 SSE / WS，节点状态由后端真实事件驱动，不改 UI 形态。

---

## 七、Live2D 模块设计

### 7.1 渲染栈
- `pixi.js` 作为渲染上下文。
- `pixi-live2d-display` 加载 Cubism 4（`.model3.json`）模型。
- Live2D Cubism Core 运行时通过 CDN 或本地 `public/live2d/core/` 引入。
- `Live2DCanvas.vue` 内部接管 canvas 生命周期，挂载 / 销毁 / resize 全部跟随组件。

### 7.2 渲染目标
- 角色稳居 `StagePanel` 中央，相对画布的缩放与位移由模型清单中的 `transform` 决定。
- 支持鼠标 / 触控点击触发动作；支持鼠标跟随（眼神追踪），移动端关闭跟随、保留点击。
- 与 `EmotionAura.vue` 同步，光晕颜色 / 强度由 VAC 驱动（详见 §8）。
- 性能保护：移动端默认关闭物理高频更新，FPS 上限 30；桌面 60。

### 7.3 模型来源与热替换
**目标**：不改源码即可替换 L2D 模型；新增模型时，只需把模型文件夹放进 `public/live2d/<name>/` 并更新 `manifest.json`。

**模型来源策略（v0.3 确定）**：
- 项目自身**不内置任何 L2D 模型资源**到 git 仓库（避免版权与体积问题）。
- 仓库内仅保留 `public/live2d/manifest.json`（可空 `models: []`）+ 一个 `public/live2d/.gitkeep`，并在 `.gitignore` 中忽略具体模型目录。
- 首次启动时，前端默认使用一个**开源 demo 模型**（如 Shizuku / Hiyori，由用户按 README 指引自行下载放入 `public/live2d/<name>/`）。
- 后续走**用户导入**路径：用户把模型目录放入 `public/live2d/<name>/`，并在 manifest 中添加一项；或在运行时通过设置抽屉的"导入模型"按钮，选择本地文件夹（基于 `showDirectoryPicker`，仅在支持 File System Access API 的浏览器可用），由前端读取后注册进 manifest（写入 `localStorage` 覆盖层，与静态 manifest 合并）。
- 模型路径、名称、表情 / motion 索引完全由 manifest 描述，前端不做硬编码。

**manifest.json 示例**：

```jsonc
// public/live2d/manifest.json
{
  "default": "shizuku",
  "models": [
    {
      "id": "shizuku",
      "name": "Shizuku",
      "entry": "/live2d/shizuku/shizuku.model3.json",
      "avatar": "/live2d/shizuku/avatar.png",
      "transform": { "scale": 0.32, "x": 0, "y": 60 },
      "expressions": {
        "happy":   "exp_happy",
        "calm":    "exp_calm",
        "sad":     "exp_sad",
        "angry":   "exp_angry",
        "neutral": "exp_neutral"
      },
      "motions": {
        "idle":     ["motion/idle_01", "motion/idle_02"],
        "recall":   ["motion/recall_01"],
        "thinking": ["motion/think_01"],
        "answer":   ["motion/talk_01", "motion/talk_02"]
      }
    }
  ]
}
```

- `live2dService` 启动时 `fetch('/live2d/manifest.json')`，与 `localStorage` 中的用户导入覆盖层合并，缓存到 `live2d store`。
- `SettingsDrawer` 的 `ModelSwitcher` 列出所有模型，包含一个"导入模型"按钮触发用户导入流程；选中模型后立即热切换，不刷新页面。
- 当某个模型缺失某种 expression / motion 时，回退到上一可用项；前端不报错，仅 console warn。
- manifest 中标识为 demo 的模型可附 `source` 字段记录来源链接，写入 README 提示用户自行下载，规避仓库内分发。

### 7.4 表情与动作驱动
- **离散表情**：由 `useEmotionDriver` 输出当前情绪类别（happy / calm / sad / angry / neutral），匹配 manifest 中的 `expressions` 键，调用 `model.expression(...)`。
- **节点状态动作**：`NodeStatusBar` 状态切换时同步播放 `motions.recall / thinking / answer / idle` 中的随机条目。
- **空闲呼吸 / 眨眼**：使用 Live2D 自带的呼吸 / 眨眼参数，组件层面只在长时间无交互时增加随机闲置 motion。

---

## 八、情绪可视化设计（VAC 驱动）

### 8.1 输入
每次 `POST /api/chat` 成功后，后端返回 `emotion_vac: { valence, arousal, control }`，写入 `emotion store`。

### 8.2 三维 → 表情类别（离散）
`useEmotionDriver` 内的默认阈值（v0.2，可调）：

| Valence | Arousal | Control | 类别 |
|---------|---------|---------|------|
| > 0.3 | > 0.3 | * | happy |
| > 0.3 | ≤ 0.3 | * | calm |
| < -0.3 | > 0.3 | * | angry |
| < -0.3 | ≤ 0.3 | * | sad |
| 其它 | 其它 | * | neutral |

> `control` 暂不参与离散分桶，仅参与下方连续氛围色与动作强度。后续若“VAC → 自训练小模型 → 动作参数”落地，整段离散映射可被替换为模型推理调用，调用面不变。

### 8.3 三维 → 连续氛围色 / UI 表征
氛围色由 CSS 变量驱动，整体仍保持暖色基调，**仅在暖色色相区间内偏移**，不进入冷色域：

- **valence (-1 → 1)** 影响色相 `--aura-h` 在 `[350°, 40°]` 范围内偏移（樱粉 ↔ 蜜橙），并在 valence 极正时点亮 `--color-accent-mint` 作为高光点缀；valence 极负时降低饱和度并轻微下移亮度，不切换为冷色。
- **arousal (-1 → 1)** 影响 `--aura-s` 饱和度（25% ~ 90%）与角色光晕的呼吸频率（慢 ~ 快）。
- **control (-1 → 1)** 影响 `--aura-a` 透明度（0.15 ~ 0.55）与光晕扩散半径，体现“收敛 / 张扬”的气场感。

派生效果：
- `EmotionAura.vue` 是覆盖在 L2D 角色后方的径向渐变 + 模糊层，所有变量改动通过 `transition` 平滑过渡。
- `MessageBubble`（AI）的描边色与背景渐变跟随 `--aura-*` 微弱偏移，让对话氛围与角色情绪一致。
- `StageBackground.vue` 的暖色渐变方向跟随 valence 缓慢倾斜。

### 8.4 数值面板（调试用）
`SettingsDrawer → DebugPanel` 中可开启“显示情绪向量”，UI 顶角浮出一个小卡片显示 `V/A/C` 实时数值与当前类别，方便答辩演示。

---

## 九、与后端 API 的契约

### 9.1 统一响应解包
后端响应一律包在 `Result<T>`：

```ts
interface Result<T> {
  code: number;   // 200 表示成功
  msg: string;
  data: T | null;
}
```

`api/http.ts` 拦截器：
- `code === 200` → 直接返回 `data` 给调用方。
- 其它 code → 抛出 `BackendError(code, msg)`。
- 网络异常 / 超时 → 抛出 `NetworkError`，触发 `ConnectionBanner`。

### 9.2 接口映射表

| 后端路由 | 前端 API | 调用方 |
|----------|----------|--------|
| `GET /api/session/active` | `listActiveSessions()` | 启动 / 抽屉刷新 |
| `GET /api/session/` | `listAllSessions()` | 历史会话面板 |
| `GET /api/session/{id}` | `getSession(id)` | 切换会话 |
| `POST /api/session/` | `createSession()` | 新建对话 |
| `DELETE /api/session/{id}` | `deleteSession(id)` | 删除会话 |
| `PUT /api/session/{id}` | `updateSession(id, patch)` | 归档 / 改状态 |
| `POST /api/chat` | `sendChat(req)` | 发送消息 |
| `GET /api/session/{id}/history` | `getHistory(id)` | 切换会话后加载 |
| `DELETE /api/session/{id}/history` | `clearHistory(id)` | 清空对话记录 |

### 9.3 关键 DTO

```ts
// types/chat.ts
export interface EmotionVAC {
  valence: number;
  arousal: number;
  control: number;
}

export interface ChatRequestDTO {
  human_input: string;
  session_id: number;
  clear_history?: boolean;
}

export interface ChatResponseDTO {
  response: string;
  emotion_vac: EmotionVAC | Record<string, never>; // 后端默认 {}
  retry_times: number;
  error_message: string | null;
  success: boolean;
}

export interface MessageResponseDTO {
  role: 'user' | 'assistant' | 'system' | 'unknown';
  content: string;
  message_id?: string;
  additional_kwargs?: Record<string, any>;
  response_metadata?: Record<string, any>;
}

export interface ChatHistoryResponseDTO {
  session_id: number;
  messages: MessageResponseDTO[];
  total_count: number;
}
```

> `emotion_vac` 缺省视为 `{ valence: 0, arousal: 0, control: 0 }`（中性），在 Api 层完成兜底。

### 9.4 历史消息字段
`GET /api/session/{id}/history` 返回 `ChatHistoryResponse`，包含严格定义的消息schema：

```ts
interface ChatHistoryResponse {
  session_id: number;
  messages: MessageResponse[];
  total_count: number;
}

interface MessageResponse {
  role: 'user' | 'assistant' | 'system' | 'unknown';
  content: string;
  message_id?: string;
  additional_kwargs?: Record<string, any>;
  response_metadata?: Record<string, any>;
}
```

前端约定：
- 仅渲染 `role ∈ {user, assistant}` 的项。
- 缺字段降级，不抛错。
- 加载历史不触发 L2D 表情动画与氛围色更新（避免一次性触发大量切换）。

**后端实现说明**：
- `MessageResponse.role` 字段由后端根据 LangChain 消息类型自动映射：
  - `HumanMessage` → `user`
  - `AIMessage` → `assistant`
  - `SystemMessage` → `system`
  - 其他类型 → `unknown`
- 消息按时间顺序排列，`total_count` 表示总消息数

---

## 十、状态模型

```ts
// stores/chat.ts
type MessageStatus = 'sent' | 'pending' | 'failed';

interface UiMessage {
  localId: string;
  role: 'user' | 'assistant';
  text: string;
  status: MessageStatus;
  emotionVac?: EmotionVAC;
  retryTimes?: number;
  errorMessage?: string | null;
  createdAt: number;
}

interface ChatState {
  messages: UiMessage[];
  nodeStatus: 'idle' | 'recalling' | 'thinking' | 'answering' | 'failed';
  sending: boolean;
}
```

```ts
// stores/session.ts
interface SessionState {
  list: SessionResponseDTO[];
  currentId: number | null;
  loading: boolean;
}

// stores/emotion.ts
interface EmotionState {
  vac: EmotionVAC;
  category: 'happy' | 'calm' | 'sad' | 'angry' | 'neutral';
  history: { vac: EmotionVAC; at: number }[];   // 最近 N 条用于轨迹绘制（可选）
}

// stores/live2d.ts
interface Live2DState {
  manifest: Live2DManifest | null;
  currentModelId: string | null;
  loaded: boolean;
  error?: string;
}

// stores/ui.ts
interface UiState {
  drawer: 'none' | 'settings' | 'sessions' | 'help';
  isMobile: boolean;
  showDebug: boolean;
}
```

---

## 十一、关键流程

### 11.1 应用启动
1. 加载 `manifest.json`，初始化 `live2d store`。
2. 初始化 axios，拉一次 `/health`；失败则展示 `ConnectionBanner`。
3. `listActiveSessions()`；若空则 `createSession()` 自动建一个；选中并 `getHistory`。
4. 默认模型加载到 `Live2DCanvas`，进入 idle 动作。

### 11.2 发送消息
1. 用户输入 → `chatService.sendMessage`。
2. 立即在 `chat store` 推一条 user 消息和一条 assistant 占位消息（`status=pending`）。
3. `nodeStatus = recalling` → 轻微动作 + 提示文字。
4. 调 `POST /api/chat`；前端按时间片自动切到 `thinking` → `answering`（同步等待期间用于撑起视觉节奏）。
5. 成功：替换占位消息文本，写入 `emotion_vac` → 更新 `emotion store` → 触发 L2D 表情 + 氛围色过渡。
6. 失败：占位消息置 `failed` 状态并展示重试；情绪不变；`nodeStatus = failed` 短暂闪烁后回到 idle。

> **当前后端尚未实现 SSE / WebSocket**，节点状态由前端 `useNodeStatus` 按时间片模拟。这是把对话流程封装在 `chatService + useNodeStatus` 这一层、而不是直接写在组件里的根本原因——后端落地推送通道后，仅替换 `chatService.sendMessage` 内部的传输实现（POST → SSE 或 WS），把前端模拟切换替换为后端事件驱动即可，`UiMessage` / `nodeStatus` / 组件全部不动。预期改动面：仅 `api/chat.ts`、`services/chatService.ts`、`composables/useNodeStatus.ts` 三个文件。

### 11.3 切换会话
- 清空 `chat.messages` 与 `nodeStatus`。
- 调 `getHistory(id)` 一次性渲染。
- 不重置情绪状态（保持上一次最终情绪），避免每次切换都把光晕拉回中性。

### 11.4 切换 L2D 模型
- 设置抽屉中点击模型 → `live2dService.switch(id)` → 销毁旧 model → 加载新 model → 自动播放 idle motion。
- 期间 `Live2DCanvas` 显示一个简约的 loading 占位（暖色 spinner）。

---

## 十二、移动端策略要点

- **断点**：`sm 360`、`md 768`、`lg 1280`、`xl 1536`。
- **响应式 hook**：`useResponsive` 暴露 `isMobile / isTablet / isDesktop`，`ui store` 同步。
- **触控**：所有按钮的最小可点击区域 ≥ 40px × 40px。
- **L2D 性能**：手机 FPS 30、关闭眼神跟随、使用基础 motion 子集。
- **键盘弹起**：聚焦输入框时，自动滚动到最新消息；不使用 `100vh`，使用 `100dvh` 防 iOS 顶栏遮挡。
- **手势**：左滑会话项可调出删除按钮（替代右键菜单）。
- **抽屉**：会话列表 / 设置 / 帮助统一走 `MobileDrawer`，从右侧或底部滑入。

---

## 十三、错误与边界

| 场景 | 行为 |
|------|------|
| 后端不可达 | 顶部 `ConnectionBanner`；发送按钮禁用；每 5s 静默轮询 `/health`，恢复后自动解除。 |
| `Result.code !== 200` | toast 展示 `msg`；发送场景下气泡置 `failed`。 |
| `ChatResponse.success === false` | 用 `error_message` 渲染气泡内容，不更新情绪，不触发动作。 |
| `retry_times >= 3` | 与正常成功一致渲染，调试模式额外标注“重试上限”。 |
| `emotion_vac` 为空对象 | 视为 `{0,0,0}`，UI 走中性。 |
| L2D 加载失败 | 舞台显示静态立绘 PNG（与模型同目录的 `fallback.png`）+ 一行小字提示，UI 不阻断使用。 |
| 历史接口字段缺失 | 缺什么降级什么，不抛错。 |

---

## 十四、预留功能 UI

本期不实现但需要在 UI 留位：

- **语音输入**：`ChatToolbar` 左侧第一个按钮为 🎤，常态禁用，hover 显示 tooltip “语音输入即将上线”。点击不报错，仅轻量提示。
- **风格 / LoRA 切换**：`SettingsDrawer` 内的“风格”分区折叠展示，描述文案“暂未开放”，不暴露任何参数控件。
- **附件 / 图片**：`ChatToolbar` 中保留一个 📎 占位，行为同语音。
- **表情面板**：`ChatToolbar` 中保留一个 😊 占位（输入表情符号到对话框，本地行为可在本期顺手实现，也可仅占位）。
- **对话导出**：在示意图“对话操作 banner”中已包含，本期实现为前端本地导出 Markdown / JSON。
- **多模型 / 多角色**：`ModelSwitcher` 是真功能；同一抽屉中的“多角色编排”仅占位。

---

## 十五、工程规范

- **TS 严格模式**：`strict: true`，禁止 `any` 漏出 Service / Api。
- **命名**：组件 PascalCase；store / composable / service kebab/小驼峰；type 用 `XxxDTO` 表示后端原始 DTO，`Ui*` / `*State` 表示前端态。
- **样式**：UnoCSS 原子类做布局；色彩 / 圆角 / 间距走 CSS 变量；禁止在组件中写死十六进制颜色（除 token 文件外）。
- **提交**：commit message 与后端一致风格 `<type>(<scope>): <subject>`。
- **代码评审清单**：是否引入冷色硬编码、是否绕过 `Result` 解包、是否在 View 层直接调 axios、是否破坏移动端断点。

---

## 十六、迭代里程碑

> 本设计书不再绑定项目时间表（旧计划书已废弃）。以下为相对里程碑，作为开发顺序参考。

| 顺序 | 里程碑 | 关键产出 |
|------|--------|----------|
| 1 | 工程骨架 | Vite + Vue3 + TS + Pinia + Router + UnoCSS + Naive UI 主题；`/health` 通；ESLint / Prettier / Stylelint 接入 |
| 2 | 主页面布局 | 按 §6 实现桌面三段式（顶栏 + 舞台 + 对话），暖色主题完成 |
| 3 | 会话与对话 | 会话 CRUD + 消息流 + 节点状态条 + 错误回退 |
| 4 | L2D 渲染 | `Live2DCanvas` + manifest 加载 + 默认模型 idle 动画 |
| 5 | 情绪可视化 | `useEmotionDriver` + `EmotionAura` + 表情/动作切换 |
| 6 | 响应式与移动端 | 三档断点、抽屉、性能降级 |
| 7 | 设置与预留 | 设置抽屉、模型切换、调试面板、语音/风格占位 |
| 8 | 打磨 | 微动效、空状态、加载态、文案 |

---

## 十七、未决与后续

- **后端 SSE / WebSocket**：当前后端为同步返回，节点状态由前端模拟。等后端推送通道落地后，按 §11.2 的范围替换 `chatService` 与 `useNodeStatus` 的实现，再回到本设计书把"模拟"改为"事件驱动"。
- **L2D 模型分发**：仓库不内置模型，首启用开源 demo 模型由用户按 README 自行下载放入 `public/live2d/<name>/`；运行时支持用户导入，覆盖层写入 `localStorage`。
- **暖色"夜间档"**：是否在后续提供低亮度的暖色保底主题（仍维持暖棕基调，不切冷色），等真实使用反馈再决定。
- **MessageResponse.created_at**：后端 `MessageResponse` 当前未带时间戳，气泡上的相对时间由前端按拉取顺序近似生成；如果后续后端补上，前端切换到真实字段即可。