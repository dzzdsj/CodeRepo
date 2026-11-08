import request from './request'

export interface KnowledgeDocItem {
  id: number
  title: string
  source: string | null
  doc_type: string
  status: string // pending / embedded / failed
  chunk_count: number
  is_enabled: boolean
  remark: string | null
  created_at: string
  updated_at: string
}

export interface KnowledgeDocDetail extends KnowledgeDocItem {
  content: string
}

export interface KnowledgeDocFormData {
  title: string
  content: string
  source?: string
  doc_type?: string
  is_enabled?: boolean
}

export interface KnowledgeSearchResult {
  doc_id: number
  doc_title: string
  chunk_index: number
  chunk_content: string
  score: number
}

export interface KnowledgeAskResult {
  answer: string
  sources: KnowledgeSearchResult[]
}

export const listKnowledgeDocs = () =>
  request.get<unknown, KnowledgeDocItem[]>('/knowledge/docs')

export const getKnowledgeDoc = (id: number) =>
  request.get<unknown, KnowledgeDocDetail>(`/knowledge/docs/${id}`)

export const createKnowledgeDoc = (data: KnowledgeDocFormData) =>
  request.post<unknown, KnowledgeDocItem>('/knowledge/docs', data)

export const updateKnowledgeDoc = (id: number, data: Partial<KnowledgeDocFormData>) =>
  request.put<unknown, KnowledgeDocItem>(`/knowledge/docs/${id}`, data)

export const deleteKnowledgeDoc = (id: number) =>
  request.delete<unknown, null>(`/knowledge/docs/${id}`)

export const embedKnowledgeDoc = (id: number) =>
  request.post<unknown, KnowledgeDocItem>(`/knowledge/docs/${id}/embed`)

export const searchKnowledge = (query: string, top_k = 5) =>
  request.post<unknown, KnowledgeSearchResult[]>('/knowledge/search', { query, top_k })

export const askKnowledge = (query: string, top_k = 5) =>
  request.post<unknown, KnowledgeAskResult>('/knowledge/ask', { query, top_k })
