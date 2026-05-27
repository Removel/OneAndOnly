import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { BackendError, NetworkError, type Result } from '@/types/result'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const httpClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 统一解包 Result<T>：code === 200 时直接返回 data；否则抛 BackendError。
 * 网络层错误归一化为 NetworkError。
 *
 * 注意：使用此实例的调用点拿到的就是裸 T，而不是 AxiosResponse。
 */
httpClient.interceptors.response.use(
  (response: AxiosResponse<Result<unknown>>) => {
    const payload = response.data
    if (payload && typeof payload.code === 'number') {
      if (payload.code === 200) {
        return payload.data as never
      }
      throw new BackendError(payload.code, payload.msg ?? '未知错误')
    }
    return response.data as never
  },
  (error: unknown) => {
    if (axios.isAxiosError(error)) {
      const data = error.response?.data as Result<unknown> | undefined
      if (data && typeof data.code === 'number' && data.code !== 200) {
        return Promise.reject(new BackendError(data.code, data.msg ?? error.message))
      }
      return Promise.reject(new NetworkError(error.message, error))
    }
    return Promise.reject(new NetworkError('未知网络错误', error))
  },
)

/**
 * 健康检查（不走 Result<T> 包装，后端直接返回 { status: 'healthy' }）
 */
export async function ping(): Promise<boolean> {
  try {
    const res = await axios.get<{ status: string }>(`${baseURL}/health`, { timeout: 5000 })
    return res.data?.status === 'healthy'
  } catch {
    return false
  }
}
