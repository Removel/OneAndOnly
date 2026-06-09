import { httpClient } from '@/api/http'
import type { ChatRequestDTO, ChatResponseDTO, StreamEvent } from '@/types/chat'
import type { ChatHistoryResponseDTO, EmotionVAC } from '@/types/message'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const NEUTRAL_VAC: EmotionVAC = { valence: 0, arousal: 0, control: 0 }

export async function sendChat(req: ChatRequestDTO): Promise<ChatResponseDTO> {
  const raw = (await httpClient.post('/api/chat', req)) as ChatResponseDTO
  return {
    ...raw,
    emotion_vac: normalizeVac(raw.emotion_vac),
  }
}

export function getHistory(sessionId: string): Promise<ChatHistoryResponseDTO> {
  return httpClient.get(`/api/session/${sessionId}/history`)
}

export function clearHistory(sessionId: string): Promise<boolean> {
  return httpClient.delete(`/api/session/${sessionId}/history`)
}

export async function* sendChatStream(req: ChatRequestDTO): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${baseURL}/api/chat-stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(req),
  })

  if (!response.ok) {
    const text = await response.text().catch(() => '')
    throw new Error(`流式请求失败: ${response.status} ${text}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('浏览器不支持流式读取')
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let currentEventType = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (trimmed.startsWith('event:')) {
          currentEventType = trimmed.slice(6).trim()
          continue
        }
        if (trimmed.startsWith('data:')) {
          const dataStr = trimmed.slice(5).trim()
          if (!dataStr || !currentEventType) continue

          try {
            const data = JSON.parse(dataStr) as Record<string, unknown>
            yield { type: currentEventType as StreamEvent['type'], data }
          } catch {
            continue
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}

function normalizeVac(raw: ChatResponseDTO['emotion_vac']): EmotionVAC {
  if (!raw || typeof raw !== 'object') return { ...NEUTRAL_VAC }
  const v = (raw as EmotionVAC).valence
  const a = (raw as EmotionVAC).arousal
  const c = (raw as EmotionVAC).control
  if (typeof v !== 'number' || typeof a !== 'number' || typeof c !== 'number') {
    return { ...NEUTRAL_VAC }
  }
  return { valence: v, arousal: a, control: c }
}
