// WebSocket 客户端：连接 /api/quotes/ws，自动重连，分发消息到 store

import type { WsMessage } from '@/types'

type Handler = (msg: WsMessage) => void

class QuoteSocket {
  private ws: WebSocket | null = null
  private handlers = new Set<Handler>()
  private reconnectTimer: number | null = null
  private reconnectDelay = 2000
  private manualClose = false

  connect() {
    if (this.ws && this.ws.readyState <= WebSocket.OPEN) return
    this.manualClose = false
    const url = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/api/quotes/ws`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectDelay = 2000
    }

    this.ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as WsMessage
        this.handlers.forEach((h) => h(msg))
      } catch (err) {
        // 忽略非 JSON 消息
        console.warn('[ws] 解析消息失败', err)
      }
    }

    this.ws.onclose = () => {
      this.ws = null
      if (!this.manualClose) {
        this.scheduleReconnect()
      }
    }

    this.ws.onerror = () => {
      this.ws?.close()
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
      // 指数退避，上限 30s
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000)
    }, this.reconnectDelay)
  }

  disconnect() {
    this.manualClose = true
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.ws?.close()
    this.ws = null
  }

  subscribe(handler: Handler): () => void {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }
}

export const quoteSocket = new QuoteSocket()
