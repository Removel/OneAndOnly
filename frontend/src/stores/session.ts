import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { SessionResponseDTO } from '@/types/session'

export const useSessionStore = defineStore('session', () => {
  const list = ref<SessionResponseDTO[]>([])
  const currentId = ref<string | null>(null)
  const loading = ref(false)

  const current = computed(() =>
    currentId.value == null ? null : (list.value.find((s) => s.id === currentId.value) ?? null),
  )

  function setList(next: SessionResponseDTO[]) {
    list.value = next
  }

  function upsert(session: SessionResponseDTO) {
    const idx = list.value.findIndex((s) => s.id === session.id)
    if (idx >= 0) list.value[idx] = session
    else list.value.unshift(session)
  }

  function remove(id: string) {
    list.value = list.value.filter((s) => s.id !== id)
    if (currentId.value === id) currentId.value = list.value[0]?.id ?? null
  }

  function setCurrent(id: string | null) {
    currentId.value = id
  }

  return { list, currentId, loading, current, setList, upsert, remove, setCurrent }
})
