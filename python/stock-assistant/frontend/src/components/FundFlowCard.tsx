// 资金流向卡片：展示个股主力/超大单/大单/中单/小单净流入 + 近期趋势
import { useEffect, useState } from 'react'
import { api } from '@/api/rest'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'
import type { FundFlowItem, FundFlowResponse } from '@/types'

interface Props {
  code: string
  name?: string
  days?: number
}

export default function FundFlowCard({ code, name, days = 30 }: Props) {
  const [data, setData] = useState<FundFlowResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api
      .getFundFlow(code, days)
      .then((res) => {
        if (!cancelled) setData(res)
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [code, days])

  if (loading) {
    return (
      <div className="flex items-center justify-center rounded-xl border border-base-500 bg-base-700 p-8 text-xs text-gray-500">
        加载资金流向数据…
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-base-500 bg-base-700 p-4 text-xs text-up">
        资金流向加载失败：{error}
      </div>
    )
  }

  if (!data || !data.latest) {
    return (
      <div className="rounded-xl border border-base-500 bg-base-700 p-4 text-xs text-gray-500">
        暂无资金流向数据
      </div>
    )
  }

  const latest = data.latest
  const recent = data.history.slice(-10) // 最近 10 天

  return (
    <div className="space-y-4">
      {/* 标题 */}
      <div className="flex items-center gap-2">
        <Activity size={16} className="text-accent" />
        <span className="text-sm font-medium text-white">
          资金流向 - {data.name || name || code}
        </span>
        <span className="text-xs text-gray-500">{latest.date}</span>
      </div>

      {/* 主力净流入概览 */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-4">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">主力净流入</span>
          <div className="flex items-center gap-2">
            <span className={`tnum text-lg font-bold ${latest.mainNetInflow >= 0 ? 'text-up' : 'text-down'}`}>
              {fmtAmount(latest.mainNetInflow)}
            </span>
            <span className={`flex items-center text-xs ${latest.mainNetInflow >= 0 ? 'text-up' : 'text-down'}`}>
              {latest.mainNetInflow >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              {latest.mainNetInflowRatio >= 0 ? '+' : ''}
              {latest.mainNetInflowRatio.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* 四类资金明细 */}
      <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
        <FlowCell label="超大单" net={latest.superLargeNetInflow} ratio={latest.superLargeNetInflowRatio} />
        <FlowCell label="大单" net={latest.largeNetInflow} ratio={latest.largeNetInflowRatio} />
        <FlowCell label="中单" net={latest.mediumNetInflow} ratio={latest.mediumNetInflowRatio} />
        <FlowCell label="小单" net={latest.smallNetInflow} ratio={latest.smallNetInflowRatio} />
      </div>

      {/* 近期主力净流入趋势 */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-xs text-gray-400">近 {recent.length} 个交易日主力净流入</span>
          <span className="text-[10px] text-gray-600">单位：亿</span>
        </div>
        <div className="flex h-24 items-end gap-1">
          {recent.map((item) => {
            const max = Math.max(...recent.map((r) => Math.abs(r.mainNetInflow)), 1)
            const height = Math.abs(item.mainNetInflow) / max
            const isUp = item.mainNetInflow >= 0
            return (
              <div key={item.date} className="flex flex-1 flex-col items-center gap-1">
                <div className="flex w-full flex-1 items-end">
                  <div
                    className={`w-full rounded-sm ${isUp ? 'bg-up/70' : 'bg-down/70'}`}
                    style={{ height: `${height * 100}%`, minHeight: '2px' }}
                    title={`${item.date}: ${fmtAmount(item.mainNetInflow)}`}
                  />
                </div>
                <span className="text-[8px] text-gray-600">{item.date.slice(5)}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

/** 单类资金净流入单元格 */
function FlowCell({ label, net, ratio }: { label: string; net: number; ratio: number }) {
  const isUp = net >= 0
  return (
    <div className="rounded-lg border border-base-500 bg-base-800 p-3">
      <div className="text-xs text-gray-400">{label}</div>
      <div className={`tnum mt-1 text-sm font-medium ${isUp ? 'text-up' : 'text-down'}`}>
        {fmtAmount(net)}
      </div>
      <div className={`tnum text-[10px] ${isUp ? 'text-up/70' : 'text-down/70'}`}>
        {ratio >= 0 ? '+' : ''}
        {ratio.toFixed(2)}%
      </div>
    </div>
  )
}

/** 金额格式化：元 → 万/亿 */
function fmtAmount(n: number): string {
  if (!n && n !== 0) return '--'
  const sign = n >= 0 ? '+' : '-'
  const abs = Math.abs(n)
  if (abs >= 1e8) return `${sign}${(abs / 1e8).toFixed(2)}亿`
  if (abs >= 1e4) return `${sign}${(abs / 1e4).toFixed(2)}万`
  return `${sign}${abs.toFixed(0)}`
}
