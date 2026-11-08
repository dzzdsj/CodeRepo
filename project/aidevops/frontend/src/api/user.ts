import request from './request'
import type { RoleBrief } from './auth'

export interface UserItem {
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

export interface UserListData {
  total: number
  list: UserItem[]
}

export interface UserFormData {
  username: string
  password: string
  email?: string
  is_active: boolean
  is_superuser: boolean
  role_id: number | null
}

export const listUsers = (params: { page: number; page_size: number; keyword?: string }) =>
  request.get<unknown, UserListData>('/users', { params })

export const createUser = (data: UserFormData) =>
  request.post<unknown, UserItem>('/users', data)

export const updateUser = (id: number, data: Partial<UserFormData>) =>
  request.put<unknown, UserItem>(`/users/${id}`, data)

export const deleteUser = (id: number) => request.delete<unknown, null>(`/users/${id}`)
