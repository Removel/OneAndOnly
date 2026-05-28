const CORE_BASE = '/live2d/core'
const PIXI_SRC = `${CORE_BASE}/pixi.min.js`
const CUBISM_CORE_SRC = `${CORE_BASE}/live2dcubismcore.min.js`
const CUBISM4_PLUGIN_SRC = `${CORE_BASE}/cubism4.min.js`
const CUBISM2_PLUGIN_SRC = `${CORE_BASE}/cubism2.min.js`

const runtimePromises = new Map<string, Promise<void>>()

export type Live2DRuntimeVersion = 'cubism2' | 'cubism4'

export async function ensureLive2DRuntime(version: Live2DRuntimeVersion = 'cubism4') {
  await loadScript('live2d-pixi', PIXI_SRC, () => Boolean(window.PIXI))

  if (version === 'cubism4') {
    await loadScript('live2d-cubism-core', CUBISM_CORE_SRC, () =>
      Boolean(window.Live2DCubismCore),
    )
    await loadScript('live2d-cubism4-plugin', CUBISM4_PLUGIN_SRC, () =>
      Boolean(window.PIXI?.live2d?.Live2DModel),
    )
    return
  }

  await loadScript('live2d-cubism2-plugin', CUBISM2_PLUGIN_SRC, () =>
    Boolean(window.PIXI?.live2d?.Live2DModel),
  )
}

function loadScript(id: string, src: string, isReady: () => boolean) {
  if (isReady()) return Promise.resolve()
  const existing = runtimePromises.get(id)
  if (existing) return existing

  const promise = new Promise<void>((resolve, reject) => {
    const old = document.querySelector<HTMLScriptElement>(`script[data-runtime-id="${id}"]`)
    if (old) {
      old.addEventListener('load', () => resolve(), { once: true })
      old.addEventListener('error', () => reject(new Error(formatMissingRuntime(src))), {
        once: true,
      })
      return
    }

    const script = document.createElement('script')
    script.src = src
    script.async = false
    script.dataset.runtimeId = id
    script.onload = () => {
      if (isReady()) {
        resolve()
        return
      }
      reject(new Error(`Live2D 运行时已加载但未注册：${src}`))
    }
    script.onerror = () => reject(new Error(formatMissingRuntime(src)))
    document.head.appendChild(script)
  })

  runtimePromises.set(id, promise)
  promise.catch(() => runtimePromises.delete(id))
  return promise
}

function formatMissingRuntime(src: string) {
  return `缺少 Live2D 运行时文件：${src}。请按 frontend/public/live2d/README.md 放入 core 文件。`
}
