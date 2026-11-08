import request from './request'

export interface LlmModelItem {
  id: number
  name: string
  provider: string
  base_url: string
  api_key: string
  model: string
  is_default: boolean
  is_enabled: boolean
  remark: string | null
  created_at: string
  updated_at: string
}

export interface LlmModelFormData {
  name: string
  provider: string
  base_url: string
  api_key: string
  model: string
  is_default: boolean
  is_enabled: boolean
  remark?: string
}

export interface LlmModelTestResult {
  ok: boolean
  latency_ms: number
  message: string
}

export const listLlmModels = () => request.get<unknown, LlmModelItem[]>('/llm-models')

export const createLlmModel = (data: LlmModelFormData) =>
  request.post<unknown, LlmModelItem>('/llm-models', data)

export const updateLlmModel = (id: number, data: Partial<LlmModelFormData>) =>
  request.put<unknown, LlmModelItem>(`/llm-models/${id}`, data)

export const deleteLlmModel = (id: number) =>
  request.delete<unknown, null>(`/llm-models/${id}`)

export const testLlmModel = (id: number) =>
  request.post<unknown, LlmModelTestResult>(`/llm-models/${id}/test`)

export const testLlmModelConfig = (data: {
  base_url: string
  api_key: string
  model: string
}) => request.post<unknown, LlmModelTestResult>('/llm-models/test', data)
