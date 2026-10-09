// 单只股票行情卡片：深色卡片，最新价、涨跌幅、成交量、涨跌闪烁
import { useQuoteStore } from '@/stores/quotes'
import { ColorText } from '@/components/ColorText'
import type { Quote } from '@/types'

interface Props {
  quote: Quote
}

export default function QuoteCard({ quote }: Props) {
  const prevPrice = useQuoteStore((s) => s.prevPrices[quote.code])
  const direction =
    prevPrice === undefined || prevPrice === quote.price
      ? 'flat'
      : quote.price > prevPrice
        ? 'up'
        : 'down'

  return (
    <div
      className={[
        'relative overflow-hidden rounded-xl border border-base-500 bg-base-700 p-4 shadow-card transition-colors',
        'hover:border-base-400',
      ].join(' ')}
    >
      {/* 涨跌闪烁背景 */}
      {direction !== 'flat' && (
        <span
          className={[
            'pointer-events-none absolute inset-0',
            direction === 'up' ? 'animate-flash-up' : 'animate-flash-down',
          ].join(' ')}
        />
      )}

      <div className="relative flex items-start justify-between">
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-white">{quote.name}</div>
          <div className="tnum mt-0.5 text-xs text-gray-500">{quote.code}</div>
        </div>
        <ColorText value={quote.changePct} suffix="%" className="tnum text-base font-bold" />
      </div>

      <div className="relative mt-3 flex items-baseline gap-2">
        <span className="tnum text-2xl font-bold text-white">
          {fmtNum(quote.price)}
        </span>
        <ColorText
          value={quote.changeAmt}
          className="tnum text-sm"
        />
      </div>

      <div className="relative mt-3 grid grid-cols-3 gap-2 text-xs text-gray-400">
        <Metric label="成交量" value={fmtVol(quote.volume)} unit="手" />
        <Metric label="最高" value={fmtNum(quote.high)} className="text-up" />
        <Metric label="最低" value={fmtNum(quote.low)} className="text-down" />
      </div>
    </div>
  )
}

function Metric({
  label,
  value,
  unit,
  className = '',
}: {
  label: string
  value: string
  unit?: string
  className?: string
}) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] text-gray-500">{label}</span>
      <span className={`tnum ${className}`}>
        {value}
        {unit && <span className="ml-0.5 text-[10px] text-gray-600">{unit}</span>}
      </span>
    </div>
  )
}

function fmtNum(n: number): string {
  if (!n && n !== 0) return '--'
  return n.toFixed(2)
}

function fmtVol(n: number): string {
  if (!n) return '--'
  if (n >= 1e8) return (n / 1e8).toFixed(2) + '亿'
  if (n >= 1e4) return (n / 1e4).toFixed(2) + '万'
  return n.toFixed(0)
}
