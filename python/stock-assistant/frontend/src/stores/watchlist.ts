// 自选股 store
import { create } from 'zustand'
import { api } from '@/api/rest'
import type { WatchlistItem, StockSearchResult } from '@/types'

interface WatchlistState {
  items: WatchlistItem[]
  loading: boolean
  error: string
  fetch: () => Promise<void>
  add: (code: string, groupName?: string, note?: string) => Promise<void>
  remove: (code: string) => Promise<void>
  update: (code: string, data: { groupName?: string; note?: string }) => Promise<void>
  search: (q: string) => Promise<StockSearchResult[]>
}

export const useWatchlistStore = create<WatchlistState>((set, get) => ({
  items: [],
  loading: false,
  error: '',

  fetch: async () => {
    set({ loading: true, error: '' })
    try {
      const items = await api.getWatchlist()
      set({ items, loading: false })
    } catch (e) {
      set({ loading: false, error: (e as Error).message })
    }
  },

  add: async (code, groupName = '默认', note) => {
    const item = await api.addWatchlist(code, groupName, note)
    set({ items: [...get().items, item] })
  },

  remove: async (code) => {
    await api.deleteWatchlist(code)
    set({ items: get().items.filter((i) => i.code !== code) })
  },

  update: async (code, data) => {
    const updated = await api.updateWatchlist(code, data)
    set({
      items: get().items.map((i) => (i.code === code ? updated : i)),
    })
  },

  search: async (q) => {
    if (!q.trim()) return []
    return api.searchStocks(q)
  },
}))
