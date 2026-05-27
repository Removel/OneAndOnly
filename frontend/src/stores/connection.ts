import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ping } from '@/api/http'

/**
 * 后端连通性状态：用于在 UI 顶部显示 ConnectionBanner
 */
export const useConnectionStore = defineStore('connection', () => {
  const reachable = ref(false)
  const lastCheckAt = ref<number | null>(null)
  const checking = ref(false)

  async function check() {
    if (checking.value) return
    checking.value = true
    try {
      reachable.value = await ping()
      lastCheckAt.value = Date.now()
    } finally {
      checking.value = false
    }
  }

  return { reachable, lastCheckAt, checking, check }
})
