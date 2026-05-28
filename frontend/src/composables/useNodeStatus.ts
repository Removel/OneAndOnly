import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import type { NodeStatus } from '@/types/chat'

const LABELS: Record<NodeStatus, string> = {
  idle: '待命中',
  recalling: '回忆中',
  thinking: '思考中',
  answering: '回答中',
  failed: '出了一点问题',
}

const TONES: Record<NodeStatus, 'default' | 'info' | 'warning' | 'success' | 'error'> = {
  idle: 'default',
  recalling: 'info',
  thinking: 'info',
  answering: 'success',
  failed: 'error',
}

export function useNodeStatus() {
  const chat = useChatStore()
  const status = computed(() => chat.nodeStatus)
  const label = computed(() => LABELS[chat.nodeStatus])
  const tone = computed(() => TONES[chat.nodeStatus])
  const active = computed(() => chat.nodeStatus !== 'idle')
  return { status, label, tone, active }
}
