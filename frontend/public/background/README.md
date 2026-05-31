# Live2D 背景切换功能

## 功能说明

用户可以在设置面板中切换Live2D模型的背景图片，支持默认渐变背景和自定义图片背景。

## 文件结构

```
public/background/
  ├── manifest.json          # 背景配置文件
  ├── bg1.jpg               # 背景图片1
  ├── bg1_thumb.jpg         # 背景图片1缩略图
  ├── bg2.jpg               # 背景图片2
  ├── bg2_thumb.jpg         # 背景图片2缩略图
  └── bg3.jpg               # 背景图片3
```

## 配置说明

### manifest.json 格式

```json
{
  "backgrounds": [
    {
      "id": "bg1",
      "name": "星空背景",
      "path": "/background/bg1.jpg",
      "thumbnail": "/background/bg1_thumb.jpg"
    },
    {
      "id": "bg2", 
      "name": "森林背景",
      "path": "/background/bg2.jpg",
      "thumbnail": "/background/bg2_thumb.jpg"
    }
  ]
}
```

### 字段说明

- `id`: 背景唯一标识符
- `name`: 背景显示名称
- `path`: 背景图片路径（相对于public目录）
- `thumbnail`: 缩略图路径（可选，如果不提供则使用完整图片）

## 使用方法

### 1. 添加背景图片

1. 将背景图片放入 `public/background/` 文件夹
2. 可选：创建缩略图（建议尺寸：200x200px）
3. 在 `manifest.json` 中添加配置

### 2. 切换背景

1. 打开设置面板
2. 找到"背景设置"折叠面板
3. 点击想要使用的背景
4. 背景会立即切换到Live2D舞台

### 3. 重新加载配置

如果修改了 `manifest.json`，点击"重新读取"按钮刷新背景列表。

## 技术实现

### Store层

使用 `useBackgroundStore` 管理背景状态：

```typescript
import { useBackgroundStore } from '@/stores/background'

const background = useBackgroundStore()
background.setCurrent('bg1')  // 切换到指定背景
```

### 组件集成

**StagePanel.vue** - 显示背景：
```vue
<div class="stage-bg" :style="backgroundStyle" />
```

**SettingsDrawer.vue** - 背景选择界面：
- 自动加载 `manifest.json`
- 显示背景列表和缩略图
- 支持点击切换背景

## 注意事项

1. **图片格式**：建议使用 JPG 或 PNG 格式
2. **图片尺寸**：建议 1920x1080 或更高分辨率
3. **文件大小**：建议单个图片不超过 2MB
4. **路径格式**：必须以 `/` 开头，如 `/background/bg1.jpg`
5. **默认背景**：系统内置"默认渐变"背景，无需配置

## 故障排除

### 背景不显示

1. 检查图片路径是否正确
2. 确认图片文件存在
3. 检查浏览器控制台是否有加载错误
4. 尝试点击"重新读取"按钮

### 缩略图不显示

1. 检查缩略图路径是否正确
2. 如果没有缩略图，系统会使用完整图片
3. 确认缩略图文件存在

### 配置加载失败

1. 检查 `manifest.json` 语法是否正确
2. 确认 JSON 格式有效
3. 查看浏览器控制台错误信息

## 扩展功能

### 动态背景

可以通过修改 `StagePanel.vue` 的 `backgroundStyle` 计算属性实现更复杂的背景效果：

```typescript
const backgroundStyle = computed(() => {
  if (currentBackground.value?.path) {
    return {
      backgroundImage: `url(${currentBackground.value.path})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      transition: 'background-image 0.5s ease',  // 添加过渡效果
    }
  }
  return {}
})
```

### 背景动画

可以结合 CSS 动画实现背景切换效果：

```css
.stage-bg {
  transition: background-image 0.5s ease-in-out;
}
```

## 更新日志

- **v1.0.0** (2026-05-31)
  - 初始版本
  - 支持背景图片切换
  - 支持缩略图显示
  - 集成到设置面板
