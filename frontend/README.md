# One and Only · Frontend

Web 前端工程骨架（Vite + Vue 3 + TypeScript + Pinia + Vue Router + UnoCSS + Naive UI）。

## 启动

```bash
pnpm install
pnpm dev          # http://localhost:5173
pnpm build
pnpm typecheck
pnpm lint
```

## 后端联调

默认通过环境变量 `VITE_API_BASE_URL` 指向后端，开发模式下默认 `http://localhost:8000`。
后端启动方式见 `.harness/doc/后端启动说明.md`。

## Live2D 资源

- 模型与 Cubism Core 运行时**不入库**（许可与体积原因）。
- 自行下载开源模型放入 `public/live2d/<model_name>/`，并在 `public/live2d/manifest.json` 的 `models` 中追加描述。
- Cubism Core 运行时（`live2dcubismcore.min.js`）放入 `public/live2d/core/`。

## 设计书

详见 `.harness/doc/Web前端设计书.md`。
