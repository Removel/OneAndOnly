/**
 * 与后端 backend/entity/Result.py 对齐的统一返回结构
 */
export interface Result<T> {
  code: number
  msg: string
  data: T | null
}

/**
 * 后端返回非 200 时由拦截器抛出的业务错误
 */
export class BackendError extends Error {
  code: number

  constructor(code: number, msg: string) {
    super(msg)
    this.name = 'BackendError'
    this.code = code
  }
}

/**
 * 网络层 / 超时错误
 */
export class NetworkError extends Error {
  override cause?: unknown

  constructor(message: string, cause?: unknown) {
    super(message)
    this.name = 'NetworkError'
    this.cause = cause
  }
}
