import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Live2DManifest, Live2DModelDescriptor } from '@/types/live2d'

const MANIFEST_URL = '/live2d/manifest.json'

export const useLive2DStore = defineStore('live2d', () => {
  const manifest = ref<Live2DManifest | null>(null)
  const currentId = ref<string | null>(null)
  const loading = ref(false)
  const ready = ref(false)
  const error = ref<string | null>(null)

  const models = computed<Live2DModelDescriptor[]>(() => manifest.value?.models ?? [])
  const current = computed<Live2DModelDescriptor | null>(() => {
    if (!currentId.value) return null
    return models.value.find((m) => m.id === currentId.value) ?? null
  })

  async function loadManifest(force = false) {
    if (manifest.value && !force) return manifest.value
    loading.value = true
    error.value = null
    try {
      const res = await fetch(MANIFEST_URL, { cache: 'no-cache' })
      if (!res.ok) throw new Error(`manifest 加载失败：HTTP ${res.status}`)
      const data = (await res.json()) as Live2DManifest
      validate(data)
      manifest.value = data
      const fallback = data.current && data.models.some((m) => m.id === data.current)
      currentId.value = fallback ? data.current : (data.models[0]?.id ?? null)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      manifest.value = null
      currentId.value = null
      throw e
    } finally {
      loading.value = false
    }
  }

  function setCurrent(id: string) {
    if (!models.value.some((m) => m.id === id)) {
      throw new Error(`未在 manifest 中找到模型 id=${id}`)
    }
    currentId.value = id
  }

  function setReady(v: boolean) {
    ready.value = v
  }

  function setError(msg: string | null) {
    error.value = msg
  }

  return {
    manifest,
    currentId,
    loading,
    ready,
    error,
    models,
    current,
    loadManifest,
    setCurrent,
    setReady,
    setError,
  }
})

function validate(data: unknown): asserts data is Live2DManifest {
  if (!data || typeof data !== 'object') throw new Error('manifest 不是合法 JSON 对象')
  const obj = data as Partial<Live2DManifest>
  if (!Array.isArray(obj.models)) throw new Error('manifest.models 不是数组')
  for (const m of obj.models) {
    if (!m || typeof m !== 'object') throw new Error('manifest.models 元素必须是对象')
    if (typeof m.id !== 'string' || !m.id) throw new Error('model.id 缺失')
    if (typeof m.name !== 'string' || !m.name) throw new Error(`model[${m.id}].name 缺失`)
    if (typeof m.entry !== 'string' || !m.entry) throw new Error(`model[${m.id}].entry 缺失`)
  }
}
