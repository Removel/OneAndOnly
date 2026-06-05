/**
 * 与 backend/entity/request/ChatRequest.py / response/ChatResponse.py 对齐
 */
import type { EmotionVAC } from '@/types/message'

export interface ChatRequestDTO {
  human_input: string
  /** 字符串形式的雪花 ID，详见 types/session.ts */
  session_id: string
  clear_history?: boolean
}

export interface ChatResponseDTO {
  response: string
  /** 后端默认是 {}，前端在 api 层兜底为中性 VAC */
  emotion_vac: EmotionVAC | Record<string, never>
  retry_times: number
  error_message: string | null
  success: boolean
}

export type NodeStatus = 'idle' | 'recalling' | 'thinking' | 'answering' | 'failed' | 'tool_calling' | 'node_processing'

export interface StreamEvent {
  type: 'token' | 'done' | 'error' | 'tool_start' | 'tool_end' | 'node_start' | 'node_end'
  data: Record<string, unknown>
}

/** done 事件的 payload，与后端 chat_stream_with_agent 对齐 */
export interface StreamDoneData {
  status: string
  response_text: string
  emotion_vac: Record<string, number>
  retry_times: number
}
