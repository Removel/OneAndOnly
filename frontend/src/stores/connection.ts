import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getApiBaseURL, pingWithReason } from '@/api/http'

/**
 * 后端连通性状态：用于在 UI 顶部显示 ConnectionBanner
 */
export const useConnectionStore = defineStore('connection', () => {
  const reachable = ref(false)
  const lastCheckAt = ref<number | null>(null)
  const checking = ref(false)
  const lastError = ref<string | null>(null)
  const apiBaseURL = getApiBaseURL()

  async function check() {
    if (checking.value) return
    checking.value = true
    try {
      const result = await pingWithReason()
      reachable.value = result.ok
      lastError.value = result.ok ? null : (result.error ?? '未知连接错误')
      lastCheckAt.value = Date.now()
    } finally {
      checking.value = false
    }
  }

  return { reachable, lastCheckAt, checking, lastError, apiBaseURL, check }
})
