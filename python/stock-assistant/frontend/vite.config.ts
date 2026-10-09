import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

// https://vite.dev/config/
export default defineConfig({
  build: {
    sourcemap: 'hidden',
  },
  plugins: [
    react({
      babel: {
        plugins: [
          'react-dev-locator',
        ],
      },
    }),
    tsconfigPaths(),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // REST API 代理到后端 FastAPI
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // WebSocket 升级支持（/api/quotes/ws）
        ws: true,
      },
    },
  },
})
