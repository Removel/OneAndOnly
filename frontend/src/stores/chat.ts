import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NodeStatus } from '@/types/chat'
import type { UiMessage } from '@/types/message'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<UiMessage[]>([])
  const nodeStatus = ref<NodeStatus>('idle')
  const sending = ref(false)

  function reset() {
    messages.value = []
    nodeStatus.value = 'idle'
    sending.value = false
  }

  function append(message: UiMessage) {
    messages.value.push(message)
  }

  function update(localId: string, patch: Partial<UiMessage>) {
    const idx = messages.value.findIndex((m) => m.localId === localId)
    if (idx >= 0) {
      messages.value[idx] = { ...messages.value[idx], ...patch }
    }
  }

  function setStatus(status: NodeStatus) {
    nodeStatus.value = status
  }

  function setSending(value: boolean) {
    sending.value = value
  }

  return {
    messages,
    nodeStatus,
    sending,
    reset,
    append,
    update,
    setStatus,
    setSending,
  }
})
