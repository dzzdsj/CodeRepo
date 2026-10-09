// REST API 客户端：封装 fetch，统一错误处理
import type {
  Quote,
  IndexQuote,
  WatchlistItem,
  StockSearchResult,
  SystemStatus,
  AlertRule,
  AlertRuleCreate,
  AlertItem,
  AlertListResponse,
  PushConfig,
  SchedulerConfig,
  PushTestResult,
  AiAnalysis,
  AiConfig,
  AiProvider,
  AiTestResult,
  KlineResponse,
  FundFlowResponse,
  SectorFundFlowResponse,
} from '@/types'

const BASE = '/api'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // ignore
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) {
    return undefined as T
  }
  return res.json() as Promise<T>
}

export const api = {
  // 行情
  getRealtimeQuotes: () => request<Quote[]>(`/quotes/realtime`),
  getRealtimeIndexes: () => request<IndexQuote[]>(`/indexes/realtime`),
  getKline: (code: string, days = 60) =>
    request<KlineResponse>(`/quotes/kline/${code}?days=${days}`),
  getFundFlow: (code: string, days = 30) =>
    request<FundFlowResponse>(`/quotes/fund-flow/${code}?days=${days}`),
  getSectorFundFlow: (sectorType: 'industry' | 'concept' = 'industry', limit = 50) =>
    request<SectorFundFlowResponse>(
      `/sectors/fund-flow?sector_type=${sectorType}&limit=${limit}`,
    ),
  // 自选股
  getWatchlist: () => request<WatchlistItem[]>(`/watchlist`),
  addWatchlist: (code: string, groupName = '默认', note?: string) =>
    request<WatchlistItem>(`/watchlist`, {
      method: 'POST',
      body: JSON.stringify({ code, groupName, note }),
    }),
  updateWatchlist: (code: string, data: { groupName?: string; note?: string }) =>
    request<WatchlistItem>(`/watchlist/${code}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  deleteWatchlist: (code: string) =>
    request<void>(`/watchlist/${code}`, { method: 'DELETE' }),
  // 股票搜索
  searchStocks: (q: string) =>
    request<StockSearchResult[]>(`/stocks/search?q=${encodeURIComponent(q)}`),
  // 系统
  getSystemStatus: () => request<SystemStatus>(`/system/status`),

  // 告警规则
  getRules: () => request<AlertRule[]>(`/rules`),
  createRule: (data: AlertRuleCreate) =>
    request<AlertRule>(`/rules`, { method: 'POST', body: JSON.stringify(data) }),
  updateRule: (id: string, data: Partial<AlertRuleCreate>) =>
    request<AlertRule>(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteRule: (id: string) =>
    request<void>(`/rules/${id}`, { method: 'DELETE' }),
  toggleRule: (id: string) =>
    request<AlertRule>(`/rules/${id}/toggle`, { method: 'PATCH' }),
  copyRule: (id: string) =>
    request<AlertRule>(`/rules/${id}/copy`, { method: 'POST' }),
  getRuleStats: (id: string) =>
    request<{
      ruleId: string
      totalTriggers: number
      todayTriggers: number
      weekTriggers: number
      pushedCount: number
      pushRate: number
      stockCount: number
    }>(`/rules/${id}/stats`),

  // 告警历史
  getAlerts: (params?: {
    code?: string
    signalType?: string
    days?: number
    page?: number
    pageSize?: number
  }) => {
    const qs = new URLSearchParams()
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null) qs.set(k, String(v))
      }
    }
    return request<AlertListResponse>(`/alerts?${qs.toString()}`)
  },
  getTodayAlerts: () => request<AlertItem[]>(`/alerts/today`),
  getAlertDetail: (id: string) => request<AlertItem>(`/alerts/${id}`),

  // 设置 - 推送
  getPushConfig: () => request<PushConfig>(`/settings/push`),
  updatePushConfig: (data: { provider: string; token: string; enabled: boolean }) =>
    request<PushConfig>(`/settings/push`, { method: 'PUT', body: JSON.stringify(data) }),
  testPush: (token: string, provider: string) =>
    request<PushTestResult>(
      `/settings/push/test?token=${encodeURIComponent(token)}&provider=${encodeURIComponent(provider)}`,
      { method: 'POST' },
    ),

  // 设置 - 调度
  getSchedulerConfig: () => request<SchedulerConfig>(`/settings/scheduler`),
  updateSchedulerConfig: (data: Partial<SchedulerConfig>) =>
    request<SchedulerConfig>(`/settings/scheduler`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // AI 分析
  getAiAnalysis: (alertId: string) =>
    request<AiAnalysis>(`/alerts/${alertId}/ai`),
  triggerAiAnalysis: (alertId: string, force = false) =>
    request<AiAnalysis>(`/alerts/${alertId}/ai`, {
      method: 'POST',
      body: JSON.stringify({ force }),
    }),

  // AI 配置
  getAiConfig: () => request<AiConfig>(`/settings/ai`),
  updateAiConfig: (data: {
    provider: string
    apiKey: string
    baseUrl: string
    model: string
    enabled: boolean
  }) =>
    request<AiConfig>(`/settings/ai`, { method: 'PUT', body: JSON.stringify(data) }),
  testAiConnection: (provider: string, apiKey: string, baseUrl: string, model: string) =>
    request<AiTestResult>(
      `/settings/ai/test?provider=${encodeURIComponent(provider)}&apiKey=${encodeURIComponent(apiKey)}&baseUrl=${encodeURIComponent(baseUrl)}&model=${encodeURIComponent(model)}`,
      { method: 'POST' },
    ),
  getAiProviders: () => request<AiProvider[]>(`/settings/ai/providers`),
}
