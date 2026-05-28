/**
 * Live2D manifest 与模型描述类型
 *
 * manifest.json 放在 public/live2d/，前端运行时通过 fetch('/live2d/manifest.json') 拉取，
 * 然后据此加载选定模型。新增模型只需要：
 *   1. 把模型文件夹拖进 public/live2d/<model_id>/
 *   2. 在 manifest.models 数组里追加一条记录
 *   3. （可选）把 manifest.current 改成新模型的 id
 */

import type { EmotionCategory } from '@/types/message'

export interface Live2DTransform {
  /** 整体缩放，相对 canvas 的短边 */
  scale: number
  /** 水平偏移（-0.5 ~ 0.5），0 表示居中 */
  x: number
  /** 垂直偏移（-0.5 ~ 0.5），负数向上 */
  y: number
}

export interface Live2DModelDescriptor {
  id: string
  name: string
  /**
   * 模型入口（.model3.json 或 Cubism 2 的 .model.json），需为 public 下绝对路径，
   * 形如 "/live2d/<model_id>/.../xxx.model3.json"
   */
  entry: string
  /** 模型版本；model3.json 使用 cubism4，旧 model.json 使用 cubism2 */
  version?: 'cubism2' | 'cubism4'
  /** 列表项预览图，可选 */
  avatar?: string
  /** 摆放位置与缩放，可选；缺省走 useLive2D 内部默认值 */
  transform?: Partial<Live2DTransform>
  /**
   * 情绪 → 表情名映射；表情名要与模型 model3.json 的 Expressions[].Name 一致。
   * 留空或映射成 null/undefined 表示该情绪不切换表情。
   */
  expressionsByEmotion?: Partial<Record<EmotionCategory, string | null>>
  /** Idle 动作所在 group，默认 "Idle"；模型若无 idle 动作可设为 null */
  idleMotionGroup?: string | null
}

export interface Live2DManifest {
  current?: string
  models: Live2DModelDescriptor[]
}

export const DEFAULT_TRANSFORM: Live2DTransform = {
  scale: 0.08,
  x: 0,
  y: 0.02,
}
