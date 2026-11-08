import request from './request'

export interface RoleItem {
  id: number
  name: string
  code: string
  description: string | null
  is_default: boolean
  permissions: string[]
  created_at: string
  updated_at: string
}

export interface RoleFormData {
  name: string
  code: string
  description?: string
  permissions: string[]
}

export const listRoles = () => request.get<unknown, RoleItem[]>('/roles')

export const createRole = (data: RoleFormData) =>
  request.post<unknown, RoleItem>('/roles', data)

export const updateRole = (id: number, data: Partial<RoleFormData>) =>
  request.put<unknown, RoleItem>(`/roles/${id}`, data)

export const deleteRole = (id: number) => request.delete<unknown, null>(`/roles/${id}`)
