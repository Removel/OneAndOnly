import { httpClient } from '@/api/http'
import type { SessionResponseDTO, SessionUpdateDTO } from '@/types/session'

const BASE = '/api/session'

export function listActiveSessions(): Promise<SessionResponseDTO[]> {
  return httpClient.get(`${BASE}/active`)
}

export function listAllSessions(): Promise<SessionResponseDTO[]> {
  return httpClient.get(`${BASE}/`)
}

export function getSession(id: string): Promise<SessionResponseDTO> {
  return httpClient.get(`${BASE}/${id}`)
}

export function createSession(): Promise<SessionResponseDTO> {
  return httpClient.post(`${BASE}/`)
}

export function deleteSession(id: string): Promise<boolean> {
  return httpClient.delete(`${BASE}/${id}`)
}

export function updateSession(id: string, patch: SessionUpdateDTO): Promise<SessionResponseDTO> {
  return httpClient.put(`${BASE}/${id}`, patch)
}
