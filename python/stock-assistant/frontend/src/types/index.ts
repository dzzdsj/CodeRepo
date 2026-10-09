// 与后端 API 对齐的类型定义

/** 单只股票实时行情 */
export interface Quote {
  code: string
  name: string
  price: number
  changePct: number
  changeAmt: number
  volume: number
  amount: number
  high: number
  low: number
  open: number
  preClose: number
  timestamp: number
  speed5m?: number | null
  volRatio?: number | null
}

/** 大盘指数实时行情 */
export interface IndexQuote {
  code: string
  name: string
  price: number
  changePct: number
  changeAmt: number
  timestamp: number
}

/** 自选股条目 */
export interface WatchlistItem {
  id: number
  code: string
  name: string
  groupName: string
  note?: string | null
  sortOrder: number
}

/** 股票搜索结果 */
export interface StockSearchResult {
  code: string
  name: string
  market: string
  industry?: string
}

/** 系统状态 */
export interface SystemStatus {
  started: boolean
  watchlistCount: number
  cacheCount: number
  indexCount: number
  lastFetchAt: number
  lastFetchOk: boolean
  lastError: string
  isTradingTime: boolean
  intervalSeconds: number
  dataSource: string
  dataSourceOk: boolean
  wsClients: number
}

// ════════════════════════════════════════
//  P2: 告警规则、告警历史、系统设置
// ════════════════════════════════════════

/** 信号类型 */
export type SignalType = 'change_pct' | 'speed' | 'volume' | 'indicator'

/** 告警规则 */
export interface AlertRule {
  id: string
  name: string
  enabled: boolean
  signalType: SignalType
  params: {
    threshold: number
    windowMinutes?: number
    volMultiple?: number
    indicator?: string
    indicatorParams?: Record<string, number>
  }
  scope: { codes: string[] | null }
  sessionStart: string
  sessionEnd: string
  channels: string[]
  cooldownMinutes: number
}

/** 创建/更新规则请求 */
export interface AlertRuleCreate {
  name: string
  enabled: boolean
  signalType: SignalType
  params: AlertRule['params']
  scope: { codes: string[] | null }
  sessionStart: string
  sessionEnd: string
  channels: string[]
  cooldownMinutes: number
}

/** 告警记录 */
export interface AlertItem {
  id: string
  code: string
  ruleId: string
  ruleName?: string
  signalType: SignalType
  triggerValue: number
  threshold: number
  price: number
  snapshot?: Record<string, unknown>
  pushed: boolean
  timestamp: string
  name?: string
}

/** 告警历史分页 */
export interface AlertListResponse {
  total: number
  items: AlertItem[]
}

/** 推送配置 */
export interface PushConfig {
  provider: string
  enabled: boolean
  hasToken: boolean
}

/** 调度配置 */
export interface SchedulerConfig {
  dataSource: string
  intervalSeconds: number
  sessionStart: string
  sessionEnd: string
}

/** 推送测试结果 */
export interface PushTestResult {
  success: boolean
  message: string
}

// ════════════════════════════════════════
//  P3: AI 分析
// ════════════════════════════════════════

/** AI 分析结果 */
export interface AiAnalysis {
  alertId: string
  hasAnalysis: boolean
  analysis: { 解读: string; 建议: string; 风险: string } | null
  analyzedAt: string | null
}

/** AI 配置 */
export interface AiConfig {
  provider: string
  baseUrl: string
  model: string
  enabled: boolean
  hasApiKey: boolean
}

/** AI Provider 选项 */
export interface AiProvider {
  value: string
  label: string
  baseUrl: string
  model: string
}

/** 规则触发统计 */
export interface RuleStats {
  ruleId: string
  totalTriggers: number
  todayTriggers: number
  weekTriggers: number
  pushedCount: number
  pushRate: number
  stockCount: number
}

/** AI 连通测试结果 */
export interface AiTestResult {
  success: boolean
  message: string
}

/** K 线数据条目 */
export interface KlineBar {
  time: number
  date: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

/** K 线 API 响应 */
export interface KlineResponse {
  code: string
  days: number
  count: number
  data: KlineBar[]
}

/** 单日资金流向 */
export interface FundFlowItem {
  date: string
  close: number
  changePct: number
  mainNetInflow: number
  mainNetInflowRatio: number
  superLargeNetInflow: number
  superLargeNetInflowRatio: number
  largeNetInflow: number
  largeNetInflowRatio: number
  mediumNetInflow: number
  mediumNetInflowRatio: number
  smallNetInflow: number
  smallNetInflowRatio: number
}

/** 资金流向 API 响应 */
export interface FundFlowResponse {
  code: string
  name: string
  latest: FundFlowItem | null
  history: FundFlowItem[]
}

/** 板块资金流向项 */
export interface SectorFundFlow {
  code: string
  name: string
  price: number
  changePct: number
  mainNetInflow: number
  mainNetInflowRatio: number
  superLargeNetInflow: number
  superLargeNetInflowRatio: number
  largeNetInflow: number
  largeNetInflowRatio: number
  mediumNetInflow: number
  mediumNetInflowRatio: number
  smallNetInflow: number
  smallNetInflowRatio: number
}

/** 板块资金流向 API 响应 */
export interface SectorFundFlowResponse {
  sectorType: string
  data: SectorFundFlow[]
}

/** WebSocket 推送消息 */
export type WsMessage =
  | { type: 'snapshot'; quotes: Quote[]; indexes: IndexQuote[] }
  | { type: 'quotes'; data: Quote[] }
  | { type: 'indexes'; data: IndexQuote[] }
  | { type: 'alert'; data: AlertItem }
