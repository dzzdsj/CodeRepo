// 行情/指数 store：管理实时行情数据，由 WebSocket 推送更新
import { create } from 'zustand'
import { quoteSocket } from '@/api/ws'
import type { Quote, IndexQuote, WsMessage, AlertItem } from '@/types'

/** Toast 通知项 */
export interface ToastItem {
  id: string
  alert: AlertItem
  createdAt: number
}

interface QuoteState {
  quotes: Record<string, Quote>
  indexes: IndexQuote[]
  // 上一帧价格，用于判断涨跌闪烁方向
  prevPrices: Record<string, number>
  connected: boolean
  // 今日告警列表
  todayAlerts: AlertItem[]
  // Toast 通知队列（实时告警弹窗）
  toasts: ToastItem[]
  applyMessage: (msg: WsMessage) => void
  setSnapshot: (quotes: Quote[], indexes: IndexQuote[]) => void
  upsertQuotes: (quotes: Quote[]) => void
  setIndexes: (indexes: IndexQuote[]) => void
  setConnected: (v: boolean) => void
  addAlert: (alert: AlertItem) => void
  setTodayAlerts: (alerts: AlertItem[]) => void
  dismissToast: (id: string) => void
  clear: () => void
}

export const useQuoteStore = create<QuoteState>((set) => ({
  quotes: {},
  indexes: [],
  prevPrices: {},
  connected: false,
  todayAlerts: [],
  toasts: [],

  applyMessage: (msg) => {
    switch (msg.type) {
      case 'snapshot':
        set((s) => {
          const prev: Record<string, number> = {}
          for (const q of msg.quotes) prev[q.code] = s.quotes[q.code]?.price ?? q.price
          const quotesMap: Record<string, Quote> = {}
          for (const q of msg.quotes) quotesMap[q.code] = q
          return { quotes: quotesMap, indexes: msg.indexes, prevPrices: prev }
        })
        break
      case 'quotes':
        useQuoteStore.getState().upsertQuotes(msg.data)
        break
      case 'indexes':
        useQuoteStore.getState().setIndexes(msg.data)
        break
      case 'alert':
        useQuoteStore.getState().addAlert(msg.data)
        break
    }
  },

  setSnapshot: (quotes, indexes) => {
    set((s) => {
      const prev: Record<string, number> = { ...s.prevPrices }
      const quotesMap = { ...s.quotes }
      for (const q of quotes) {
        prev[q.code] = s.quotes[q.code]?.price ?? q.price
        quotesMap[q.code] = q
      }
      return { quotes: quotesMap, prevPrices: prev }
    })
  },

  upsertQuotes: (incoming) => {
    set((s) => {
      const prev = { ...s.prevPrices }
      const quotesMap = { ...s.quotes }
      for (const q of incoming) {
        prev[q.code] = s.quotes[q.code]?.price ?? q.price
        quotesMap[q.code] = q
      }
      return { quotes: quotesMap, prevPrices: prev }
    })
  },

  setIndexes: (indexes) => set({ indexes }),
  setConnected: (v) => set({ connected: v }),
  addAlert: (alert) =>
    set((s) => ({
      todayAlerts: [alert, ...s.todayAlerts].slice(0, 50),
      toasts: [
        ...s.toasts,
        { id: `toast-${alert.id}`, alert, createdAt: Date.now() },
      ].slice(-5),
    })),
  setTodayAlerts: (alerts) => set({ todayAlerts: alerts }),
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
  clear: () =>
    set({ quotes: {}, indexes: [], prevPrices: {}, todayAlerts: [], toasts: [] }),
}))

// 启动 WebSocket 订阅（在 App 初始化时调用一次）
export function startQuoteStream() {
  quoteSocket.subscribe((msg) => useQuoteStore.getState().applyMessage(msg))
  quoteSocket.connect()
}
