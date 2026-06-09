/**
 * 与 backend/entity/response/MessageResponse.py 对齐
 */

export type MessageRole = 'user' | 'assistant' | 'system' | 'unknown'

export interface MessageResponseDTO {
  role: MessageRole
  content: string
  message_id?: string | null
  additional_kwargs?: Record<string, unknown> | null
  response_metadata?: Record<string, unknown> | null
}

/**
 * 与 backend/entity/response/ChatHistoryResponse.py 对齐
 */
export interface ChatHistoryResponseDTO {
  session_id: string
  messages: MessageResponseDTO[]
  total_count: number
}

export type MessageStatus = 'sent' | 'pending' | 'failed'

export interface MessageItem {
  type: 'text' | 'tool_call'
  content: string
  toolName?: string
  timestamp: number
}

/**
 * 前端 UI 层使用的消息结构（不要把后端 DTO 直接塞进列表）
 */
export interface UiMessage {
  localId: string
  role: 'user' | 'assistant'
  text: string
  status: MessageStatus
  emotionVac?: EmotionVAC
  retryTimes?: number
  errorMessage?: string | null
  createdAt: number
  items?: MessageItem[]
}

export interface EmotionVAC {
  valence: number
  arousal: number
  control: number
}

export type EmotionCategory = 'happy' | 'calm' | 'sad' | 'angry' | 'neutral'
