/**
 * Live2D 渲染：把 manifest 选定的模型挂到一个 canvas 上。
 *
 * 使用全局加载的 PIXI.js 和 pixi-live2d-display（通过 index.html script 标签）
 */
import { onBeforeUnmount, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useLive2DStore } from '@/stores/live2d'
import { useEmotionStore } from '@/stores/emotion'
import { DEFAULT_TRANSFORM, type Live2DModelDescriptor } from '@/types/live2d'
import { ensureLive2DRuntime } from '@/composables/useLive2DRuntime'

export function useLive2D() {
  const store = useLive2DStore()
  const emotion = useEmotionStore()
  const { current } = storeToRefs(store)
  const { category } = storeToRefs(emotion)

  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const containerRef = ref<HTMLElement | null>(null)

  let app: PixiApplicationInstance | null = null
  let model: PixiLive2DModelInstance | null = null
  let resizeObserver: ResizeObserver | null = null

  async function ensureApp(desc: Live2DModelDescriptor): Promise<PixiApplicationInstance | null> {
    if (app) return app
    if (!canvasRef.value || !containerRef.value) return null

    await ensureLive2DRuntime(desc.version ?? 'cubism4')

    const { clientWidth, clientHeight } = containerRef.value
    const pixi = window.PIXI
    if (!pixi) {
      store.setError('缺少 PIXI.js 运行时')
      return null
    }

    app = new pixi.Application({
      view: canvasRef.value,
      width: Math.max(clientWidth, 1),
      height: Math.max(clientHeight, 1),
      backgroundAlpha: 0,
      antialias: true,
      autoDensity: true,
      resolution: window.devicePixelRatio || 1,
      powerPreference: 'high-performance',
    })

    bindResize()
    return app
  }

  function bindResize() {
    if (!containerRef.value || resizeObserver) return
    resizeObserver = new ResizeObserver(() => {
      if (!app || !containerRef.value) return
      const { clientWidth, clientHeight } = containerRef.value
      app.renderer.resize(Math.max(clientWidth, 1), Math.max(clientHeight, 1))
      placeModel()
    })
    resizeObserver.observe(containerRef.value)
  }

  function placeModel() {
    if (!app || !model) return
    const t = { ...DEFAULT_TRANSFORM, ...(current.value?.transform ?? {}) }
    const w = app.renderer.width / (app.renderer.resolution || 1)
    const h = app.renderer.height / (app.renderer.resolution || 1)

    // 获取模型尺寸
    const modelWidth = model.internalModel?.width || model.width || 1
    const modelHeight = model.internalModel?.height || model.height || 1
    const baseScale = Math.min(w / modelWidth, h / modelHeight)
    const fitScale = Math.min(w / modelWidth, h / modelHeight) * 0.9
    const targetScale = Math.min(baseScale * t.scale * 10, fitScale)

    model.scale.set(targetScale)
    model.anchor.set(0.5, 0.5)
    model.x = w * (0.5 + t.x)
    model.y = h * (0.5 + t.y)
  }

  async function loadCurrent() {
    const desc = current.value
    if (!desc) return

    store.setReady(false)
    store.setError(null)

    try {
      const application = await ensureApp(desc)
      if (!application) return

      console.log('[Live2D] 开始加载模型:', desc.entry)

      // 检查 Live2DModel 是否可用
      if (!window.PIXI?.live2d?.Live2DModel) {
        throw new Error('pixi-live2d-display 未正确加载')
      }

      // 使用 window.PIXI.live2d.Live2DModel（参考 EchoBot 实现）
      const next = await window.PIXI.live2d.Live2DModel.from(desc.entry, {
        autoInteract: false,
      })

      console.log('[Live2D] 模型加载完成，等待纹理...')
      console.log('[Live2D] internalModel:', next.internalModel)
/*
      // 关键修复：等待纹理完全加载
      // pixi-live2d-display 0.4.0 的 from() 不会等待纹理，需要手动等待
      const textures = next.internalModel?.textures
      if (textures && textures.length > 0) {
        console.log('[Live2D] 等待', textures.length, '个纹理加载...')
        await Promise.all(
          textures.map((texture, index) => {
            return new Promise<void>((resolve) => {
              if (texture?.baseTexture) {
                if (texture.baseTexture.valid) {
                  console.log(`[Live2D] 纹理 ${index} 已就绪`)
                  resolve()
                } else {
                  console.log(`[Live2D] 等待纹理 ${index} 加载...`)
                  texture.baseTexture.once('loaded', () => {
                    console.log(`[Live2D] 纹理 ${index} 加载完成`)
                    resolve()
                  })
                  texture.baseTexture.once('error', (err: any) => {
                    console.error(`[Live2D] 纹理 ${index} 加载失败:`, err)
                    resolve() // 即使失败也继续
                  })
                  // 超时保护
                  setTimeout(() => {
                    console.warn(`[Live2D] 纹理 ${index} 加载超时`)
                    resolve()
                  }, 10000)
                }
              } else {
                console.warn(`[Live2D] 纹理 ${index} 无效`)
                resolve()
              }
            })
          }),
        )
        console.log('[Live2D] 所有纹理加载完成')
      } else {
        console.warn('[Live2D] 没有找到纹理数组，可能加载失败')
      }
*/
      await (next as any).loaded;
      // 销毁旧模型
      destroyModel()

      // 存储新模型
      model = next

      // 添加到舞台
      application.stage.addChild(model)
      console.log('[Live2D] 模型已添加到舞台')

      // 设置模型属性（参考 EchoBot）
      model.anchor.set(0.5, 0.5)
      model.interactive = true
      model.cursor = 'grab'

      // 调整位置和缩放
      placeModel()

      // 应用表情
      applyExpression(desc, category.value)

      store.setReady(true)
      console.log('[Live2D] 模型渲染就绪')
    } catch (e) {
      const msg = formatLive2DError(e)
      console.error('[Live2D] 加载失败:', e)
      store.setError(`加载模型失败：${msg}`)
      destroyModel()
    }
  }

  function applyExpression(desc: Live2DModelDescriptor, cat: string) {
    if (!model) return
    const map = desc.expressionsByEmotion ?? {}
    const name = map[cat as keyof typeof map]
    if (typeof name === 'string' && name.length > 0) {
      try {
        model.expression(name)
      } catch {
        /* 表情不存在就静默忽略 */
      }
    }
  }

  function destroyModel() {
    if (model) {
      // 从舞台移除
      if (app?.stage) {
        app.stage.removeChild(model)
      }
      // 销毁模型
      model.destroy({ children: true, texture: true, baseTexture: true })
      model = null
    }
  }

  function destroyApp() {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    destroyModel()
    if (app) {
      app.destroy(false, { children: true, texture: true, baseTexture: true })
      app = null
    }
  }

  watch(current, () => {
    if (!current.value) return
    void loadCurrent()
  })

  watch(category, (cat) => {
    if (current.value) applyExpression(current.value, cat)
  })

  onBeforeUnmount(() => {
    destroyApp()
  })

  return {
    canvasRef,
    containerRef,
    bootstrap: loadCurrent,
  }
}

function formatLive2DError(error: unknown) {
  if (error instanceof Error) {
    const cause = (error as Error & { cause?: unknown }).cause
    const causeText = cause == null ? '' : `；cause=${String(cause)}`
    return `${error.message || error.name || 'Unknown error'}${causeText}`
  }
  if (typeof error === 'object' && error !== null) {
    try {
      return JSON.stringify(error)
    } catch {
      return Object.prototype.toString.call(error)
    }
  }
  return String(error)
}
