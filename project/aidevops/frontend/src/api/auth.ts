import request from './request'

export interface RoleBrief {
  id: number
  name: string
  code: string
}

export interface UserInfo {
  id: number
  username: string
  email: string | null
  is_active: boolean
  is_superuser: boolean
  role: RoleBrief | null
  permissions: string[]
  created_at: string
  updated_at: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  user: UserInfo
}

export const login = (username: string, password: string) =>
  request.post<unknown, LoginResult>('/auth/login', { username, password })

export const register = (username: string, password: string, email?: string) =>
  request.post<unknown, UserInfo>('/auth/register', { username, password, email })

export const fetchMe = () => request.get<unknown, UserInfo>('/auth/me')
