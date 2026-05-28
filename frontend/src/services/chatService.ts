import * as chatApi from '@/api/chat'
import { useChatStore } from '@/stores/chat'
import { useEmotionStore } from '@/stores/emotion'
import type { UiMessage, EmotionVAC } from '@/types/message'
import type { MessageResponseDTO } from '@/types/message'

const NODE_TIMINGS: Record<'recalling' | 'thinking', number> = {
  recalling: 600,
  thinking: 800,
}

function localId(): string {
  return `m_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`
}

function pickRenderableHistory(messages: MessageResponseDTO[]): UiMessage[] {
  const now = Date.now()
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .map((m, idx) => ({
      localId: `h_${idx}_${m.message_id ?? Math.random().toString(36).slice(2, 8)}`,
      role: m.role as 'user' | 'assistant',
      text: m.content,
      status: 'sent' as const,
      createdAt: now - (messages.length - idx) * 1000,
    }))
}

export const chatService = {
  async loadHistory(sessionId: string) {
    const chat = useChatStore()
    const history = await chatApi.getHistory(sessionId)
    chat.reset()
    chat.messages.splice(0, chat.messages.length, ...pickRenderableHistory(history.messages))
  },

  async clearHistory(sessionId: string) {
    await chatApi.clearHistory(sessionId)
    const chat = useChatStore()
    chat.reset()
  },

  async sendMessage(sessionId: string, text: string) {
    const trimmed = text.trim()
    if (!trimmed) return
    const chat = useChatStore()
    const emotion = useEmotionStore()

    const userMsg: UiMessage = {
      localId: localId(),
      role: 'user',
      text: trimmed,
      status: 'sent',
      createdAt: Date.now(),
    }
    const assistantMsg: UiMessage = {
      localId: localId(),
      role: 'assistant',
      text: '',
      status: 'pending',
      createdAt: Date.now(),
    }
    chat.append(userMsg)
    chat.append(assistantMsg)
    chat.setSending(true)
    chat.setStatus('recalling')

    const recallTimer = window.setTimeout(() => {
      if (chat.nodeStatus === 'recalling') chat.setStatus('thinking')
    }, NODE_TIMINGS.recalling)
    const thinkTimer = window.setTimeout(() => {
      if (chat.nodeStatus === 'thinking') chat.setStatus('answering')
    }, NODE_TIMINGS.recalling + NODE_TIMINGS.thinking)

    try {
      const res = await chatApi.sendChat({ human_input: trimmed, session_id: sessionId })
      window.clearTimeout(recallTimer)
      window.clearTimeout(thinkTimer)

      if (!res.success) {
        chat.update(assistantMsg.localId, {
          status: 'failed',
          text: res.error_message ?? '回复失败，请重试',
          retryTimes: res.retry_times,
          errorMessage: res.error_message,
        })
        chat.setStatus('failed')
        window.setTimeout(() => chat.setStatus('idle'), 1500)
        return
      }

      chat.update(assistantMsg.localId, {
        status: 'sent',
        text: res.response,
        retryTimes: res.retry_times,
        emotionVac: res.emotion_vac as UiMessage['emotionVac'],
      })
      const vac = res.emotion_vac as Partial<EmotionVAC>
      if (
        typeof vac.valence === 'number' &&
        typeof vac.arousal === 'number' &&
        typeof vac.control === 'number'
      ) {
        emotion.setVac(vac as EmotionVAC)
      }
      chat.setStatus('idle')
    } catch (err) {
      window.clearTimeout(recallTimer)
      window.clearTimeout(thinkTimer)
      const message = err instanceof Error ? err.message : '请求失败'
      chat.update(assistantMsg.localId, {
        status: 'failed',
        text: message,
        errorMessage: message,
      })
      chat.setStatus('failed')
      window.setTimeout(() => chat.setStatus('idle'), 1500)
      throw err
    } finally {
      chat.setSending(false)
    }
  },
}
