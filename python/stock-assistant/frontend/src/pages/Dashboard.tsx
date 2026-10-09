// 仪表盘：市场速览 + 实时行情卡片栅格 + 系统状态 + 今日告警
import { useEffect } from 'react'
import { useQuoteStore } from '@/stores/quotes'
import { useWatchlistStore } from '@/stores/watchlist'
import { api } from '@/api/rest'
import QuoteCard from '@/components/quote/QuoteCard'
import AiAnalysisCard from '@/components/AiAnalysisCard'
import { ColorText } from '@/components/ColorText'
import { AlertCircle, Clock, Activity, Wifi, Bell, Sparkles, TrendingUp, TrendingDown } from 'lucide-react'
import { useState } from 'react'
import type { SystemStatus, AlertItem, IndexQuote } from '@/types'

const SIGNAL_LABELS: Record<string, string> = {
  change_pct: '涨跌幅',
  speed: '涨速',
  volume: '量比',
  indicator: '指标',
}

export default function Dashboard() {
  const quotes = useQuoteStore((s) => s.quotes)
  const indexes = useQuoteStore((s) => s.indexes)
  const setIndexes = useQuoteStore((s) => s.setIndexes)
  const items = useWatchlistStore((s) => s.items)
  const todayAlerts = useQuoteStore((s) => s.todayAlerts)
  const setTodayAlerts = useQuoteStore((s) => s.setTodayAlerts)
  const fetchWatchlist = useWatchlistStore((s) => s.fetch)
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  useEffect(() => {
    fetchWatchlist()
    api.getTodayAlerts().then(setTodayAlerts).catch(() => {})
    // 初始拉取指数数据（兜底 WS 尚未连接的场景）
    api.getRealtimeIndexes().then(setIndexes).catch(() => {})
    const t = setInterval(() => {
      api.getSystemStatus().then(setStatus).catch(() => {})
    }, 5000)
    api.getSystemStatus().then(setStatus).catch(() => {})
    return () => clearInterval(t)
  }, [fetchWatchlist, setTodayAlerts, setIndexes])

  const quoteList = Object.values(quotes)

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">仪表盘</h1>
          <p className="mt-1 text-xs text-gray-500">
            实时监控 {items.length} 只自选股 · 盘中行情秒级刷新
          </p>
        </div>
        {status && <StatusBadge status={status} />}
      </div>

      {/* 市场速览：大盘指数横向条 */}
      <section>
        <SectionTitle icon={<Activity size={16} />} title="市场速览" count={indexes.length} />
        {indexes.length === 0 ? (
          <EmptyState text="暂无指数数据，交易时段将自动刷新" />
        ) : (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-6">
            {indexes.map((idx) => (
              <IndexCard key={idx.code} index={idx} />
            ))}
          </div>
        )}
      </section>

      {/* 行情卡片栅格 */}
      <section>
        <SectionTitle icon={<Activity size={16} />} title="自选股行情" count={quoteList.length} />
        {quoteList.length === 0 ? (
          <EmptyState text="暂无行情数据，交易时段将自动刷新" />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {quoteList.map((q) => (
              <QuoteCard key={q.code} quote={q} />
            ))}
          </div>
        )}
      </section>

      {/* 今日告警 */}
      <section>
        <SectionTitle icon={<Bell size={16} />} title="今日告警" count={todayAlerts.length} />
        {todayAlerts.length === 0 ? (
          <EmptyState text="暂无告警，交易时段内触发规则时将实时推送" />
        ) : (
          <div className="overflow-hidden rounded-xl border border-base-500 bg-base-800">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-base-500 text-xs text-gray-500">
                  <th className="px-4 py-2.5 text-left font-medium">时间</th>
                  <th className="px-4 py-2.5 text-left font-medium">代码</th>
                  <th className="px-4 py-2.5 text-left font-medium">信号</th>
                  <th className="px-4 py-2.5 text-right font-medium">触发值</th>
                  <th className="px-4 py-2.5 text-right font-medium">价格</th>
                  <th className="px-4 py-2.5 text-center font-medium">推送</th>
                  <th className="px-4 py-2.5 text-center font-medium">AI 解读</th>
                </tr>
              </thead>
              <tbody>
                {todayAlerts.slice(0, 10).map((a) => (
                  <AlertRow
                    key={a.id}
                    alert={a}
                    expanded={expandedId === a.id}
                    onToggle={() =>
                      setExpandedId((cur) => (cur === a.id ? null : a.id))
                    }
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

/** 大盘指数卡片 */
function IndexCard({ index }: { index: IndexQuote }) {
  const isUp = index.changePct >= 0
  return (
    <div className="flex items-center justify-between rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 transition-colors hover:border-base-400">
      <div className="min-w-0">
        <div className="truncate text-xs text-gray-400">{index.name}</div>
        <div className="tnum mt-0.5 text-sm font-bold text-white">
          {fmtIndexNum(index.price)}
        </div>
      </div>
      <div className={`flex flex-col items-end ${isUp ? 'text-up' : 'text-down'}`}>
        <div className="flex items-center gap-0.5 text-sm font-medium">
          {isUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
          {index.changePct >= 0 ? '+' : ''}
          {index.changePct.toFixed(2)}%
        </div>
        <div className="tnum mt-0.5 text-[11px]">
          {index.changeAmt >= 0 ? '+' : ''}
          {fmtIndexNum(index.changeAmt)}
        </div>
      </div>
    </div>
  )
}

/** 指数数字格式化 */
function fmtIndexNum(n: number): string {
  if (n === null || n === undefined || isNaN(n)) return '--'
  if (Math.abs(n) >= 1e4) return n.toFixed(2)
  return n.toFixed(2)
}

function AlertRow({
  alert,
  expanded,
  onToggle,
}: {
  alert: AlertItem
  expanded: boolean
  onToggle: () => void
}) {
  const time = new Date(alert.timestamp)
  const timeStr = `${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}:${String(time.getSeconds()).padStart(2, '0')}`
  return (
    <>
      <tr className="border-b border-base-500/50 last:border-0 hover:bg-base-700">
        <td className="tnum px-4 py-2.5 text-xs text-gray-400">{timeStr}</td>
        <td className="tnum px-4 py-2.5 text-xs text-gray-400">{alert.code}</td>
        <td className="px-4 py-2.5">
          <span className="rounded bg-base-600 px-1.5 py-0.5 text-xs text-gray-300">
            {SIGNAL_LABELS[alert.signalType] || alert.signalType}
          </span>
        </td>
        <td className="tnum px-4 py-2.5 text-right">
          <ColorText value={alert.triggerValue} />
        </td>
        <td className="tnum px-4 py-2.5 text-right text-white">{alert.price.toFixed(2)}</td>
        <td className="px-4 py-2.5 text-center">
          <span className={alert.pushed ? 'text-up' : 'text-gray-600'}>
            {alert.pushed ? '已推' : '未推'}
          </span>
        </td>
        <td className="px-4 py-2.5 text-center">
          <button
            onClick={onToggle}
            className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors ${
              expanded
                ? 'bg-accent/20 text-accent'
                : 'text-gray-400 hover:bg-base-600 hover:text-white'
            }`}
            title={expanded ? '收起 AI 解读' : '展开 AI 解读'}
          >
            <Sparkles size={12} />
            {expanded ? '收起' : 'AI 解读'}
          </button>
        </td>
      </tr>
      {expanded && (
        <tr className="border-b border-base-500/50 last:border-0 bg-base-700/40">
          <td colSpan={7} className="p-0">
            <AiAnalysisCard alertId={alert.id} />
          </td>
        </tr>
      )}
    </>
  )
}

function SectionTitle({
  icon,
  title,
  count,
}: {
  icon: React.ReactNode
  title: string
  count?: number
}) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <span className="text-accent">{icon}</span>
      <h2 className="text-sm font-semibold text-white">{title}</h2>
      {count !== undefined && (
        <span className="ml-1 rounded bg-base-700 px-1.5 py-0.5 text-xs text-gray-400">
          {count}
        </span>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: SystemStatus }) {
  const ok = status.started && status.dataSourceOk
  const trading = status.isTradingTime
  return (
    <div className="flex items-center gap-3 text-xs">
      <span className="flex items-center gap-1.5">
        <Wifi size={14} className={ok ? 'text-down' : 'text-gray-500'} />
        <span className="text-gray-400">数据源{ok ? '正常' : '异常'}</span>
      </span>
      <span className="flex items-center gap-1.5">
        <Clock size={14} className={trading ? 'text-up' : 'text-gray-500'} />
        <span className="text-gray-400">{trading ? '交易中' : '非交易时段'}</span>
      </span>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-xl border border-dashed border-base-500 bg-base-800 p-8 text-center text-xs text-gray-500">
      {text}
    </div>
  )
}
