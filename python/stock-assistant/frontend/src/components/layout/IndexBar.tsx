// 顶部市场指数条：展示大盘指数实时行情
import { useQuoteStore } from '@/stores/quotes'
import { ColorText } from '@/components/ColorText'

export default function IndexBar() {
  const indexes = useQuoteStore((s) => s.indexes)

  return (
    <div className="flex items-center gap-6 overflow-x-auto border-b border-base-500 bg-base-800 px-6 py-2.5">
      {indexes.length === 0 ? (
        <span className="text-xs text-gray-500">大盘指数加载中…</span>
      ) : (
        indexes.map((idx) => (
          <div key={idx.code} className="flex shrink-0 items-baseline gap-2">
            <span className="text-xs text-gray-400">{idx.name}</span>
            <span className="tnum text-sm font-semibold text-white">
              {fmtPrice(idx.price)}
            </span>
            <ColorText value={idx.changePct} suffix="%" className="tnum text-xs" />
          </div>
        ))
      )}
    </div>
  )
}

function fmtPrice(n: number): string {
  if (!n) return '--'
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
