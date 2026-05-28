# Live2D 资源接入规范

这个目录只提交规范文件和 `manifest.json`，实际模型资源与运行时文件不入库。

## 目录结构

```text
public/live2d/
  core/
    pixi.min.js
    live2dcubismcore.min.js
    cubism4.min.js
    cubism2.min.js              # 只有 Cubism 2 模型需要
  models/
    your_model_id/
      runtime/
        your_model.model3.json
        your_model.4096/
          texture_00.png
```

## 添加 Cubism 4 模型

1. 把模型文件夹放到 `public/live2d/models/<model_id>/`。
2. 在 `public/live2d/manifest.json` 的 `models` 数组里追加配置。
3. 把 `current` 改成要默认展示的模型 id。
4. 打开设置抽屉，点击“重新读取 manifest”。

示例：

```json
{
  "id": "mao_pro",
  "name": "Mao Pro",
  "version": "cubism4",
  "entry": "/live2d/models/mao_pro/runtime/mao_pro.model3.json",
  "avatar": "/live2d/models/mao_pro/avatar.png",
  "transform": { "scale": 0.18, "x": 0, "y": -0.05 },
  "expressionsByEmotion": {
    "happy": "exp_01",
    "calm": "exp_02",
    "sad": "exp_03",
    "angry": "exp_04",
    "neutral": null
  },
  "idleMotionGroup": "Idle"
}
```

## 字段说明

- `id`：唯一标识，只用小写字母、数字、短横线或下划线。
- `name`：前端展示名称。
- `version`：`cubism4` 或 `cubism2`，不填时默认 `cubism4`。
- `entry`：模型入口，Cubism 4 指向 `.model3.json`，Cubism 2 指向 `.model.json`。
- `avatar`：设置面板缩略图，可选。
- `transform.scale`：模型缩放。模型太大就调小，太小就调大。
- `transform.x`：水平偏移，正数向右。
- `transform.y`：垂直偏移，负数向上。
- `expressionsByEmotion`：情绪到表情名的映射，表情名必须和模型 JSON 内的表达式名称一致。
- `idleMotionGroup`：待机动作分组名，没有动作可以设为 `null`。

## 常见问题

- 提示缺少 `pixi.min.js` / `live2dcubismcore.min.js` / `cubism4.min.js`：说明 `core/` 运行时没放齐。
- 提示 `entry` 404：检查 `manifest.json` 路径是否和真实文件路径一致。
- 模型显示但没有贴图：检查模型 JSON 的 `FileReferences.Textures`。开发环境会尝试自动修正常见的 `4096/2048/1024/512` 贴图子目录。
- 表情不切换：检查 `expressionsByEmotion` 的值是否等于模型 JSON 里的表达式名称。
