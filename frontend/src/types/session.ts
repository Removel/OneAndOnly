/**
 * 与 backend/entity/response/SessionResponse.py 对齐
 * 与 backend/entity/request/SessionRequest.py 对齐
 *
 * 注意：后端 id 是雪花算法生成的 18 位 long，超出 JS 安全整数。
 * 前端统一用 string 存放（http 层用 json-bigint 把溢出整数转成字符串，
 * 发送时 Pydantic 会自动 coerce 回 int）。
 */

export type SessionStatus = 'active' | 'archived' | 'deleted' | string

export interface SessionResponseDTO {
  id: string
  status: SessionStatus
  created_at: string | null
  updated_at: string | null
  last_activity_at: string | null
}

export interface SessionUpdateDTO {
  status?: SessionStatus
  last_activity_at?: string
}
