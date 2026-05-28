import { httpClient } from '@/api/http'
import type { ChatRequestDTO, ChatResponseDTO } from '@/types/chat'
import type { ChatHistoryResponseDTO, EmotionVAC } from '@/types/message'

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
