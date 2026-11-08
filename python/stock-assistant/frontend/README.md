# 股票助手 · 前端

React 18 + TypeScript + Vite 6 单页应用，深色金融主题（A 股红涨绿跌）。
项目整体说明、启动步骤与接口文档见上级目录的 [../README.md](../README.md)。

## 常用命令

```bash
npm install      # 安装依赖
npm run dev      # 开发服务器（http://localhost:5183，/api 代理到后端 8010）
npm run build    # 生产构建
npm run check    # TypeScript 类型检查
npm run lint     # ESLint
```

## 目录结构

```
src/
├── api/          # rest.ts 统一封装 REST 调用；ws.ts 管理 WebSocket（自动重连）
├── components/   # 通用组件
│   ├── layout/   # 侧边栏、顶部指数条、整体布局
│   ├── quote/    # 行情卡片
│   ├── KlineChart.tsx      # 日 K：蜡烛 + MA5/10/20 + 成交量，支持范围切换与触控板缩放
│   ├── IntradayChart.tsx   # 分时：价格/均价/昨收线 + 成交量子图
│   └── StockChartCard.tsx  # 分时 / 日 K 切换容器
├── pages/        # 路由页面：仪表盘/自选股/板块/规则/历史/设置
├── stores/       # Zustand：quotes（实时行情）、watchlist（自选股）
└── types/        # 与后端 API 对齐的 TS 类型
```

## 关键约定

- **路径别名**：`@/` 指向 `src/`（见 `vite.config.ts` 与 `tsconfig.json`）
- **实时数据**：`stores/quotes.ts` 在应用启动时建立 WebSocket，推送直接更新 store，组件订阅渲染
- **K 线图库**：lightweight-charts v5（使用 `chart.addSeries(...)` 新 API）；交互边界
  （最大放大倍数、滚动留白）在 `KlineChart.tsx` 内通过 `subscribeVisibleLogicalRangeChange` 钳制
- **配色**：上涨 `#F6465D`（红）、下跌 `#16C784`（绿），定义于各图表组件，勿按境外习惯反转
