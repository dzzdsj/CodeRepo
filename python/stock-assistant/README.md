# 股票助手（Stock Assistant）

面向个人 A 股投资者的**实时行情监控与智能告警平台**。后端调度器在交易时段秒级采集行情，经 WebSocket 实时推送到看板，并自动检测涨跌幅、短时涨速、成交量异动等信号，命中规则后通过微信（Server 酱 / PushPlus）第一时间推送，同时提供自选股管理、告警历史回溯、板块资金流向与 AI 告警解读。

- 盘中无需盯盘，关键异动秒级通知
- 单用户本地部署，SQLite 单文件存储，零运维
- 深色金融主题（红涨绿跌），Desktop-first 响应式界面

## 功能特性

- **实时仪表盘**：自选股最新价 / 涨跌幅 / 涨速 / 成交量，WebSocket 秒级刷新，数字闪烁动效
- **市场速览**：上证、深证、创业板、科创 50 等大盘指数实时行情
- **自选股管理**：按代码 / 名称模糊搜索添加，支持分组、备注、删除
- **个股行情图表**：自选股行内展开「分时 / 日 K」图——当日 1 分钟分时（价格 / 均价 / 昨收 / 成交量）与前复权日 K（MA5/10/20 + 成交量），日 K 支持 3 月 / 1 年 / 3 年 / 上市以来全历史查看，触控板与鼠标可平移缩放并一键复位
- **告警规则引擎**：支持四类信号
  - `change_pct` 涨跌幅阈值
  - `speed` 短时涨速异动（窗口期可配）
  - `volume` 成交量异动（量比倍数）
  - `indicator` 技术指标突破（预留）
  - 支持生效时段、推送渠道、同股同规则冷却时间
- **智能通知**：Server 酱 / PushPlus 微信推送，支持一键测试推送；前端 Toast 实时弹窗
- **告警历史**：分页 + 多条件筛选，详情含触发时刻行情快照与 K 线回溯
- **板块资金流**：行业 / 概念板块资金流向排行，个股资金流与 K 线、技术指标查询
- **AI 分析**：接入 OpenAI 兼容接口（智谱 GLM、通义千问、OpenAI、DeepSeek、自定义），对告警生成解读与操作建议

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + TypeScript + Vite 6、TailwindCSS 3、Zustand 5、React Router 7、lightweight-charts、lucide-react |
| 后端 | Python 3.11 + FastAPI + Uvicorn、APScheduler（AsyncIOScheduler）、SQLAlchemy 2.0（异步） |
| 数据源 | 腾讯财经、东方财富公开行情接口（主，免费直连）；AkShare（兜底 / 个股资金流）；Tushare（配置预留） |
| 数据库 | SQLite + aiosqlite（启动自动建表 / 补列，无需手动迁移） |
| 实时通信 | FastAPI 原生 WebSocket（行情、告警两条推送通道） |
| 其他 | requests / curl 子进程（行情采集与推送、AI 请求的 HTTP 传输，含代理环境自动回退）、cryptography（Token 加密存储）、pydantic-settings（.env 配置） |

## 项目结构

```
stock-assistant/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口：建表、种子数据、启动调度器
│   │   ├── core/               # 配置、数据库引擎、加密
│   │   ├── api/v1/             # REST API 路由（行情/自选股/规则/告警/设置/AI 等）
│   │   ├── ws/                 # WebSocket 连接管理
│   │   ├── services/           # 监控调度、检测引擎、推送、数据源、AI、种子数据
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── repositories/       # 数据访问层
│   │   └── utils/              # 交易时段等工具
│   ├── requirements.txt
│   ├── .env.example
│   └── run.sh                  # 启动脚本（激活 .venv，reload 模式）
├── frontend/                   # React 前端（Vite）
│   ├── src/
│   │   ├── pages/              # 仪表盘/自选股/板块/规则/历史/设置
│   │   ├── components/         # 布局、行情卡片、K 线、AI 卡片等
│   │   ├── stores/             # Zustand 状态
│   │   ├── api/                # REST 与 WebSocket 客户端
│   │   └── types/
│   ├── vite.config.ts          # /api 代理 → http://127.0.0.1:8010
│   └── package.json
└── README.md
```

## 快速启动

### 1. 启动后端

```bash
cd backend

# 建议使用虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 复制配置文件并按需修改（首次）
cp .env.example .env

# 启动（方式一：手动）
uvicorn app.main:app --host 0.0.0.0 --port 8010

# 启动（方式二：脚本，自动激活 .venv，带 --reload）
./run.sh
```

后端启动后：

- API 服务：http://127.0.0.1:8010
- 交互式文档（Swagger）：http://127.0.0.1:8010/docs
- 健康检查：http://127.0.0.1:8010/health
- 首次启动会自动创建 `backend/data/stock.db`，写入预置股票库、默认自选股与默认告警规则，并立即拉取一次行情填充缓存（非交易时段展示收盘数据）

### 2. 启动前端

```bash
cd frontend

# 安装依赖（仅首次）
npm install

# 启动开发服务器
npm run dev
```

启动后访问 http://localhost:5183

> **前置条件**：后端必须先启动。前端通过 Vite 代理将 `/api` 请求（含 WebSocket 升级）转发到 `http://127.0.0.1:8010`，见 [vite.config.ts](frontend/vite.config.ts)。

其他前端命令：`npm run build`（构建）、`npm run check`（TS 类型检查）、`npm run lint`（ESLint）。

## 配置说明

后端配置通过环境变量或 `backend/.env` 加载（参考 `.env.example`）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `APP_HOST` / `APP_PORT` | `127.0.0.1` / `8010` | 服务监听地址 |
| `APP_DEBUG` | `true` | 调试模式 |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/stock.db` | SQLite 数据库路径 |
| `SECRET_KEY` | 占位字符串 | Token 加解密密钥，**部署前务必修改为随机字符串** |
| `SCHEDULER_INTERVAL_SECONDS` | `5` | 行情轮询间隔（秒） |
| `SCHEDULER_SESSION_START` / `SCHEDULER_SESSION_END` | `09:30` / `15:00` | 盘中采集时段（非交易时段调度器自动跳过） |
| `DATA_SOURCE` | `akshare` | 数据源标识（历史配置项；实际采集始终腾讯 / 东财直连优先，AkShare 自动兜底） |
| `TUSHARE_TOKEN` | 空 | Tushare Token（预留，当前版本未使用） |

推送渠道（Server 酱 / PushPlus）、AI Provider 与调度参数也可在前端「设置」页中在线配置，Token 经加密后存入数据库。

## 页面路由

| 路由 | 页面 |
|---|---|
| `/` | 仪表盘（实时行情 + 今日告警 + 市场速览） |
| `/watchlist` | 自选股管理 |
| `/sectors` | 板块资金流向 |
| `/rules` | 告警规则配置 |
| `/history` | 告警历史 |
| `/settings` | 系统设置（推送 / 调度 / AI） |

## 主要 API

所有 REST 接口统一前缀 `/api`，WebSocket 同样走 `/api` 前缀：

- 行情：`GET /quotes/realtime`、`GET /quotes/kline/{code}?days=250`（前复权日K，默认近 250 根、最大 10000，超出自动分段翻页）、`GET /quotes/intraday/{code}`（当日 1 分钟分时，含昨收/均价）、`GET /quotes/indicators/{code}`、`GET /quotes/fund-flow/{code}`、`WS /quotes/ws`
- 指数：`GET /indexes/realtime`
- 自选股：`GET|POST /watchlist`、`PUT|DELETE /watchlist/{code}`
- 股票搜索：`GET /stocks/search?q=`
- 告警规则：`GET|POST /rules`、`PUT|DELETE /rules/{id}`、`POST /rules/{id}/copy`、`PATCH /rules/{id}/toggle`、`GET /rules/{id}/stats`
- 告警历史：`GET /alerts`（分页筛选）、`GET /alerts/today`、`GET /alerts/{id}`、`WS /alerts/ws`
- 板块：`GET /sectors/fund-flow`
- 系统：`GET /system/status`
- 设置：`GET|PUT /settings/push`、`POST /settings/push/test`、`GET|PUT /settings/scheduler`、`GET|PUT /settings/ai`、`POST /settings/ai/test`
- AI 分析：`GET|POST /alerts/{id}/ai`（读取缓存 / 重新生成）

完整接口定义与数据结构见 FastAPI 自动文档 `/docs`。

## 数据源说明

所有行情均来自公开免费接口，无需 Token；采集层统一在 [data_source.py](backend/app/services/data_source.py)，遵循「腾讯 / 东财直连为主、AkShare 兜底」策略，单位统一换算为**股、元**，失败自动降级：

| 数据 | 主数据源 | 兜底 | 说明 |
|---|---|---|---|
| 实时行情 | 腾讯 `qt.gtimg.cn/q=`（GBK，批量报价） | AkShare `stock_zh_a_spot_em` | 成交量手→股、成交额万元→元 |
| 大盘指数 | 腾讯 `qt.gtimg.cn/q=` | — | 指数代码由预置定义表维护 |
| 股票搜索 | 腾讯 `smartbox.gtimg.cn/s3/` | AkShare | 支持代码 / 拼音 / 名称 |
| 日 K 线 | 腾讯 `web.ifzq.gtimg.cn/.../fqkline/get`（前复权） | AkShare `stock_zh_a_hist` | 单段约 800 根，更长历史按日期分段翻页去重拼接 |
| 当日分时 | 东方财富 `push2his.eastmoney.com/.../trends2/get` | 腾讯 `.../minute/query` | 1 分钟点，含昨收、分钟均价；腾讯兜底仅保留 09:30–11:30 / 13:00–15:00 |
| 板块资金流 | 东方财富 `push2.eastmoney.com/.../clist/get` | — | 行业 `m:90+t:2`、概念 `m:90+t:3`，流入 / 流出各取一次合并 |
| 个股资金流 | AkShare `stock_individual_fund_flow`（底层为东财） | — | 主力 / 超大单 / 大单 / 中单 / 小单净流入 |

> 网络层说明：第三方库底层的 requests 在 macOS 系统代理（Clash 等）环境下可能出现 ProxyError，模块启动时会 monkeypatch `requests.Session.request`，原生请求失败后自动回退到 curl 子进程，因此运行环境无需额外配置代理。

## 工作原理

调度器在交易时段按配置频率从腾讯 / 东财行情接口（AkShare 兜底）拉取自选股行情 → 更新进程内行情缓存（环形缓冲区用于涨速 / 量比计算）→ 一路经 WebSocket 推送前端仪表盘，一路送入告警检测器执行规则匹配；命中规则后写入告警历史、推送前端 Toast，并按规则配置调用微信推送。告警冷却表在进程内维护，避免同一股票同一规则短时重复打扰。非交易时段调度器自动跳过轮询，页面展示最近一次收盘数据。
