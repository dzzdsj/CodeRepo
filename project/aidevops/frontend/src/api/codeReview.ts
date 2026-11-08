import request from './request'

export interface CodeReviewIssue {
  severity: string // high / medium / low
  category: string // bug / security / style / performance / other
  line: number | null
  description: string
  suggestion: string | null
}

export interface CodeReviewSuggestions {
  summary: string
  score: number | null
  issues: CodeReviewIssue[]
  error?: string
}

export interface CodeReviewItem {
  id: number
  repo: string
  branch: string | null
  commit: string | null
  title: string | null
  language: string
  status: string // pending / completed / failed
  score: number | null
  ai_suggestions: CodeReviewSuggestions | null
  created_at: string
  updated_at: string
}

export interface CodeReviewDetail extends CodeReviewItem {
  code_content: string
}

export interface CodeReviewFormData {
  repo: string
  code_content: string
  branch?: string
  commit?: string
  title?: string
  language?: string
}

export const listCodeReviews = () => request.get<unknown, CodeReviewItem[]>('/code-reviews')

export const getCodeReview = (id: number) =>
  request.get<unknown, CodeReviewDetail>(`/code-reviews/${id}`)

export const createCodeReview = (data: CodeReviewFormData) =>
  request.post<unknown, CodeReviewItem>('/code-reviews', data)

export const deleteCodeReview = (id: number) =>
  request.delete<unknown, null>(`/code-reviews/${id}`)

export const runCodeReview = (id: number) =>
  request.post<unknown, CodeReviewItem>(`/code-reviews/${id}/review`)
