// 告警历史：筛选 + 分页列表 + 行情快照详情展开
import { Fragment, useEffect, useState, useCallback } from 'react'
import { api } from '@/api/rest'
import type { AlertItem, AlertListResponse, SignalType } from '@/types'
import AiAnalysisCard from '@/components/AiAnalysisCard'
import KlineChart from '@/components/KlineChart'
import {
  History as HistoryIcon,
  Filter,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Bell,
  BellOff,
  Search,
  Sparkles,
  X,
} from 'lucide-react'

const PAGE_SIZE = 20

// 信号类型标签配置：颜色 / 文案
const SIGNAL_TAG: Record<
  SignalType,
  { label: string; className: string }
> = {
  change_pct: {
    label: '涨跌幅',
    className: 'border-up/30 bg-up/10 text-up',
  },
  speed: {
    label: '涨速',
    className: 'border-orange-500/30 bg-orange-500/10 text-orange-400',
  },
  volume: {
    label: '量比',
    className: 'border-purple-500/30 bg-purple-500/10 text-purple-400',
  },
  indicator: {
    label: '指标',
    className: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
  },
}

const SIGNAL_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: '全部信号' },
  { value: 'change_pct', label: '涨跌幅' },
  { value: 'speed', label: '涨速' },
  { value: 'volume', label: '量比' },
  { value: 'indicator', label: '指标' },
]

const DAYS_OPTIONS = [7, 30, 90]

export default function History() {
  // 筛选条件（apply 后才触发请求）
  const [code, setCode] = useState('')
  const [signalType, setSignalType] = useState('')
  const [days, setDays] = useState(7)
  const [page, setPage] = useState(1)

  // 输入缓冲（输入框中编辑，点查询/回车才提交）
  const [codeInput, setCodeInput] = useState('')

  const [data, setData] = useState<AlertListResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  // AI 解读展开行（独立于快照展开，控制 AiAnalysisCard 显隐）
  const [expandedAiId, setExpandedAiId] = useState<string | null>(null)
  // 展开行的快照详情（异步加载详情）
  const [detailCache, setDetailCache] = useState<Record<string, AlertItem>>({})
  const [detailLoading, setDetailLoading] = useState<string | null>(null)

  const fetchAlerts = useCallback(() => {
    setLoading(true)
    setError('')
    api
      .getAlerts({
        code: code.trim() || undefined,
        signalType: signalType || undefined,
        days,
        page,
        pageSize: PAGE_SIZE,
      })
      .then((res) => setData(res))
      .catch((e) => {
        setError((e as Error).message)
        setData(null)
      })
      .finally(() => setLoading(false))
  }, [code, signalType, days, page])

  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  // 切换筛选条件时回到第一页
  const onApplyFilter = () => {
    setCode(codeInput.trim())
    setPage(1)
  }

  const onResetFilter = () => {
    setCodeInput('')
    setCode('')
    setSignalType('')
    setDays(7)
    setPage(1)
  }

  const onCodeKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') onApplyFilter()
  }

  const onToggleRow = (item: AlertItem) => {
    if (expandedId === item.id) {
      setExpandedId(null)
      return
    }
    setExpandedId(item.id)
    // 优先用列表项已有的 snapshot；若无则拉取详情
    if (item.snapshot && Object.keys(item.snapshot).length > 0) {
      setDetailCache((c) => ({ ...c, [item.id]: item }))
      return
    }
    if (detailCache[item.id]) return
    setDetailLoading(item.id)
    api
      .getAlertDetail(item.id)
      .then((d) => setDetailCache((c) => ({ ...c, [item.id]: d })))
      .catch(() => {
        // 失败则用列表项本身兜底
        setDetailCache((c) => ({ ...c, [item.id]: item }))
      })
      .finally(() => setDetailLoading(null))
  }

  const total = data?.total ?? 0
  const items = data?.items ?? []
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const pageStart = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1
  const pageEnd = Math.min(page * PAGE_SIZE, total)

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center gap-2">
        <HistoryIcon size={20} className="text-accent" />
        <div>
          <h1 className="text-xl font-bold text-white">告警历史</h1>
          <p className="mt-1 text-xs text-gray-500">
            查询历史触发的告警记录，点击行可展开查看行情快照
          </p>
        </div>
      </div>

      {/* 筛选栏 */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Filter size={14} />
            <span>筛选</span>
          </div>

          {/* 股票代码输入 */}
          <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2 focus-within:border-accent">
            <Search size={14} className="text-gray-500" />
            <input
              value={codeInput}
              onChange={(e) => setCodeInput(e.target.value)}
              onKeyDown={onCodeKey}
              placeholder="股票代码，如 600519"
              className="w-44 bg-transparent text-sm text-white placeholder:text-gray-600 focus:outline-none"
            />
          </div>

          {/* 信号类型下拉 */}
          <select
            value={signalType}
            onChange={(e) => {
              setSignalType(e.target.value)
              setPage(1)
            }}
            className="rounded-lg border border-base-500 bg-base-700 px-3 py-2 text-sm text-white focus:border-accent focus:outline-none"
          >
            {SIGNAL_OPTIONS.map((o) => (
              <option key={o.value} value={o.value} className="bg-base-800">
                {o.label}
              </option>
            ))}
          </select>

          {/* 时间范围 */}
          <div className="flex items-center overflow-hidden rounded-lg border border-base-500 bg-base-700">
            {DAYS_OPTIONS.map((d) => (
              <button
                key={d}
                onClick={() => {
                  setDays(d)
                  setPage(1)
                }}
                className={`px-3 py-2 text-xs transition-colors ${
                  days === d
                    ? 'bg-accent/15 text-accent'
                    : 'text-gray-400 hover:bg-base-600 hover:text-white'
                }`}
              >
                {d}天
              </button>
            ))}
          </div>

          <button
            onClick={onApplyFilter}
            className="rounded-lg bg-accent px-4 py-2 text-xs font-medium text-base-900 hover:bg-accent-hover"
          >
            查询
          </button>
          <button
            onClick={onResetFilter}
            className="rounded-lg border border-base-500 px-3 py-2 text-xs text-gray-400 hover:bg-base-700 hover:text-white"
          >
            重置
          </button>

          {(code || signalType) && (
            <span className="text-xs text-gray-600">
              已筛选：
              {code && <span className="tnum text-gray-400"> {code}</span>}
              {code && signalType && <span className="text-gray-600"> ·</span>}
              {signalType && (
                <span className="text-gray-400">
                  {' '}
                  {SIGNAL_TAG[signalType as SignalType].label}
                </span>
              )}
            </span>
          )}
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="flex items-center justify-between rounded-lg border border-up/40 bg-up/10 px-3 py-2 text-xs text-up">
          <span>加载失败：{error}</span>
          <button onClick={fetchAlerts} className="underline">
            重试
          </button>
        </div>
      )}

      {/* 双栏：左侧时间轴 + 右侧详情 */}
      <div className="flex gap-4">
        {/* 左侧时间轴 */}
        <div className="w-80 shrink-0 overflow-hidden rounded-xl border border-base-500 bg-base-800 lg:w-96">
          <div className="border-b border-base-500 px-4 py-2.5 text-xs text-gray-400">
            告警时间轴
          </div>
          <div className="max-h-[70vh] overflow-y-auto">
            {loading && items.length === 0 ? (
              <div className="px-4 py-10 text-center text-xs text-gray-500">
                加载中…
              </div>
            ) : items.length === 0 ? (
              <div className="px-4 py-10 text-center text-xs text-gray-500">
                {error ? '加载失败，请重试' : '暂无告警记录'}
              </div>
            ) : (
              <ul className="relative">
                {/* 时间轴竖线 */}
                <div className="absolute left-[27px] top-2 bottom-2 w-px bg-base-600" />
                {items.map((it) => {
                  const active = expandedId === it.id
                  return (
                    <li
                      key={it.id}
                      onClick={() => onToggleRow(it)}
                      className={`relative cursor-pointer px-4 py-3 transition-colors ${
                        active
                          ? 'bg-base-700'
                          : 'hover:bg-base-700/50'
                      }`}
                    >
                      {/* 时间轴节点 */}
                      <span
                        className={`absolute left-[18px] top-4 z-10 flex h-4 w-4 items-center justify-center rounded-full border-2 ${
                          active
                            ? 'border-accent bg-accent'
                            : 'border-base-500 bg-base-800'
                        }`}
                      />
                      <div className="ml-8">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-sm font-medium text-white">
                            {it.name || it.ruleName || it.code}
                          </span>
                          {it.pushed ? (
                            <Bell size={12} className="shrink-0 text-down" />
                          ) : (
                            <BellOff size={12} className="shrink-0 text-gray-600" />
                          )}
                        </div>
                        <div className="mt-1 flex flex-wrap items-center gap-1.5">
                          <SignalTag type={it.signalType} />
                          <span className="tnum text-[11px] text-gray-400">
                            {fmtTime(it.timestamp)}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-3 text-[11px] text-gray-500">
                          <span className="tnum">{it.code}</span>
                          <span className="tnum">
                            触发 {fmtNum(it.triggerValue)} / 阈值{' '}
                            {fmtNum(it.threshold)}
                          </span>
                        </div>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </div>

        {/* 右侧详情 */}
        <div className="min-w-0 flex-1">
          {expandedId ? (
            (() => {
              const it = items.find((x) => x.id === expandedId)
              if (!it) return null
              const detail = detailCache[it.id] ?? it
              const snapshot = detail.snapshot
              return (
                <div className="space-y-4 rounded-xl border border-base-500 bg-base-800 p-4">
                  {/* 详情头 */}
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-base font-semibold text-white">
                        {it.name || it.ruleName || it.code}
                      </h3>
                      <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-gray-400">
                        <span className="tnum">{it.code}</span>
                        <span className="tnum">{fmtTime(it.timestamp)}</span>
                        <SignalTag type={it.signalType} />
                      </div>
                    </div>
                    <button
                      onClick={() => setExpandedId(null)}
                      className="rounded p-1 text-gray-500 hover:bg-base-700 hover:text-white"
                    >
                      <X size={16} />
                    </button>
                  </div>

                  {/* 关键指标 */}
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <DetailMetric label="触发值" value={fmtNum(it.triggerValue)} />
                    <DetailMetric label="阈值" value={fmtNum(it.threshold)} />
                    <DetailMetric
                      label="价格"
                      value={it.price ? it.price.toFixed(2) : '--'}
                    />
                    <DetailMetric
                      label="推送状态"
                      value={it.pushed ? '已推送' : '未推送'}
                      valueClass={it.pushed ? 'text-down' : 'text-gray-500'}
                    />
                  </div>

                  {/* 行情快照 */}
                  <div className="border-t border-base-500/50 pt-3">
                    <SnapshotView
                      snapshot={snapshot}
                      loading={detailLoading === it.id}
                    />
                  </div>

                  {/* K 线图 */}
                  <div className="border-t border-base-500/50 pt-3">
                    <KlineChart
                      code={it.code}
                      alertDate={fmtDate(it.timestamp)}
                      days={60}
                    />
                  </div>

                  {/* AI 解读入口 */}
                  <div className="border-t border-base-500/50 pt-3">
                    <button
                      onClick={() =>
                        setExpandedAiId((cur) =>
                          cur === it.id ? null : it.id,
                        )
                      }
                      className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs transition-colors ${
                        expandedAiId === it.id
                          ? 'bg-accent/20 text-accent'
                          : 'border border-base-500 text-gray-400 hover:bg-base-700 hover:text-white'
                      }`}
                    >
                      <Sparkles size={12} />
                      {expandedAiId === it.id ? '收起 AI 解读' : 'AI 解读'}
                    </button>
                    {expandedAiId === it.id && (
                      <div className="mt-2 rounded-lg border border-base-500/50 bg-base-800/60">
                        <AiAnalysisCard alertId={it.id} />
                      </div>
                    )}
                  </div>
                </div>
              )
            })()
          ) : (
            <div className="flex h-64 items-center justify-center rounded-xl border border-base-500 bg-base-800 text-xs text-gray-500">
              点击左侧告警查看详情
            </div>
          )}
        </div>
      </div>

      {/* 分页 */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          共 <span className="tnum text-gray-300">{total}</span> 条 ·
          当前第 <span className="tnum text-gray-300">{page}</span>/
          <span className="tnum text-gray-300">{totalPages}</span> 页
          {total > 0 && (
            <span className="ml-1 text-gray-600">
              （{pageStart}-{pageEnd}）
            </span>
          )}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1 || loading}
            className="flex items-center gap-1 rounded-lg border border-base-500 px-3 py-1.5 text-xs text-gray-400 enabled:hover:bg-base-700 enabled:hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft size={14} />
            上一页
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages || loading}
            className="flex items-center gap-1 rounded-lg border border-base-500 px-3 py-1.5 text-xs text-gray-400 enabled:hover:bg-base-700 enabled:hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            下一页
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

/** 详情指标卡 */
function DetailMetric({
  label,
  value,
  valueClass = '',
}: {
  label: string
  value: string
  valueClass?: string
}) {
  return (
    <div className="rounded-lg border border-base-500 bg-base-700 px-3 py-2">
      <div className="text-[10px] text-gray-500">{label}</div>
      <div className={`tnum mt-0.5 text-sm font-medium text-white ${valueClass}`}>
        {value}
      </div>
    </div>
  )
}

/** 信号类型标签 */
function SignalTag({ type }: { type: SignalType }) {
  const tag = SIGNAL_TAG[type]
  return (
    <span
      className={`inline-block rounded border px-2 py-0.5 text-[11px] ${tag.className}`}
    >
      {tag.label}
    </span>
  )
}

/** 行情快照详情：把 snapshot 渲染为 key/value 表格 */
function SnapshotView({
  snapshot,
  loading,
}: {
  snapshot?: Record<string, unknown>
  loading: boolean
}) {
  if (loading) {
    return <div className="text-xs text-gray-500">加载快照中…</div>
  }
  if (!snapshot || Object.keys(snapshot).length === 0) {
    return <div className="text-xs text-gray-600">该告警未保存行情快照</div>
  }

  const entries = Object.entries(snapshot)
  return (
    <div>
      <div className="mb-2 text-xs font-medium text-gray-400">行情快照</div>
      <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 sm:grid-cols-3 lg:grid-cols-4">
        {entries.map(([k, v]) => (
          <div key={k} className="flex items-center justify-between text-xs">
            <span className="text-gray-500">{fmtSnapKey(k)}</span>
            <span className="tnum ml-2 text-right text-gray-300">
              {fmtSnapValue(v)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

/** 时间格式化：MM-DD HH:mm:ss */
function fmtTime(ts: string | number): string {
  const d = new Date(ts)
  if (isNaN(d.getTime())) return String(ts)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(
    d.getMinutes(),
  )}:${p(d.getSeconds())}`
}

/** 日期格式化：YYYY-MM-DD（用于 K 线图标注） */
function fmtDate(ts: string | number): string {
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ''
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

/** 数值格式化：保留 2 位小数；过大时压缩 */
function fmtNum(n: number | null | undefined): string {
  if (n === null || n === undefined || isNaN(n)) return '--'
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + '亿'
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + '万'
  return n.toFixed(2)
}

/** snapshot 字段名翻译 */
function fmtSnapKey(k: string): string {
  const map: Record<string, string> = {
    code: '代码',
    name: '名称',
    price: '最新价',
    changePct: '涨跌幅',
    changeAmt: '涨跌额',
    volume: '成交量',
    amount: '成交额',
    high: '最高',
    low: '最低',
    open: '今开',
    preClose: '昨收',
    speed5m: '5分钟涨速',
    volRatio: '量比',
    timestamp: '时间',
  }
  return map[k] ?? k
}

/** snapshot 值格式化 */
function fmtSnapValue(v: unknown): string {
  if (v === null || v === undefined) return '--'
  if (typeof v === 'number') {
    if (Math.abs(v) >= 1e8) return (v / 1e8).toFixed(2) + '亿'
    if (Math.abs(v) >= 1e4) return (v / 1e4).toFixed(2) + '万'
    // 涨跌幅等百分比字段
    return v.toFixed(2)
  }
  if (typeof v === 'string') {
    // 时间戳数字字符串
    if (/^\d{10,13}$/.test(v)) return fmtTime(Number(v))
    return v
  }
  return JSON.stringify(v)
}
