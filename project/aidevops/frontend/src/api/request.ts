import axios, { AxiosError } from 'axios'

const TOKEN_KEY = 'aidevops_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token: string) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

// 请求拦截：自动携带 JWT
request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：解包统一响应体 {code, msg, data}
request.interceptors.response.use(
  (response) => {
    const body = response.data
    // 非统一格式（如健康检查）直接返回
    if (body === null || typeof body !== 'object' || !('code' in body)) {
      return body
    }
    if (body.code === 0) {
      return body.data
    }
    return Promise.reject(new Error(body.msg || '请求失败'))
  },
  (error: AxiosError<{ msg?: string }>) => {
    if (error.response?.status === 401) {
      clearToken()
      // 避免在登录页重复跳转
      if (!location.pathname.startsWith('/login')) {
        location.href = '/login'
      }
    }
    const msg = error.response?.data?.msg ?? error.message ?? '网络异常'
    return Promise.reject(new Error(msg))
  }
)

export default request
