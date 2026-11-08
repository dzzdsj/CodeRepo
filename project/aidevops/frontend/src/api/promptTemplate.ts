import request from './request'

export interface PromptTemplateItem {
  id: number
  name: string
  description: string | null
  content: string
  variables: string[]
  version: number
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface PromptTemplateFormData {
  name: string
  description?: string
  content: string
  is_enabled: boolean
}

export const listPromptTemplates = () =>
  request.get<unknown, PromptTemplateItem[]>('/prompt-templates')

export const createPromptTemplate = (data: PromptTemplateFormData) =>
  request.post<unknown, PromptTemplateItem>('/prompt-templates', data)

export const updatePromptTemplate = (
  id: number,
  data: Partial<PromptTemplateFormData>
) => request.put<unknown, PromptTemplateItem>(`/prompt-templates/${id}`, data)

export const deletePromptTemplate = (id: number) =>
  request.delete<unknown, null>(`/prompt-templates/${id}`)

export const renderPromptTemplate = (id: number, values: Record<string, string>) =>
  request.post<unknown, { rendered: string }>(`/prompt-templates/${id}/render`, {
    values
  })
