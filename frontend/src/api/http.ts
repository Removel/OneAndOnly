import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import JSONBig from 'json-bigint'
import { BackendError, NetworkError, type Result } from '@/types/result'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/**
 * 后端使用雪花算法生成 18 位 long ID，超出 JS Number.MAX_SAFE_INTEGER (16 位)。
 * 默认 JSON.parse 会把末位精度丢掉（如 ...712 → ...700），导致 session_id 在
 * 二次请求时找不到记录。这里改用 json-bigint，溢出的整数统一转成字符串，
 * 前端 ID 字段类型也按 string 处理；发送时字符串会被 Pydantic 自动 coerce 回 int。
 */
const jsonBig = JSONBig({ storeAsString: true })

export const httpClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  transformResponse: [
    (data: unknown) => {
      if (typeof data !== 'string' || data.length === 0) return data
      try {
        return jsonBig.parse(data)
      } catch {
        return data
      }
    },
  ],
})

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

export async function ping(): Promise<boolean> {
  try {
    const res = await axios.get<{ status: string }>(`${baseURL}/health`, { timeout: 5000 })
    return res.data?.status === 'healthy'
  } catch {
    return false
  }
}
