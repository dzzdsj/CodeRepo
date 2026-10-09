## 启动
```
cd /Users/dzzdsj/git/dzzdsj-git/github/CodeRepo/python/stock-assistant/frontend

# 1. 安装依赖（仅首次需要）
npm install

# 2. 启动开发服务器
npm run dev

启动后访问 http://localhost:5173

前置条件
后端必须先启动：前端通过 Vite 代理将 /api 请求转发到 http://127.0.0.1:8000 （vite.config.ts#L20-L29），包括 REST API 和 WebSocket
后端启动命令：cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```