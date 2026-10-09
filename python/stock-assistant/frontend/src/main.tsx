import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { startQuoteStream } from '@/stores/quotes'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// 启动时建立 WebSocket 实时行情订阅（单例，全局生效）
startQuoteStream()
