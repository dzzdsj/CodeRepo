// 个股图表卡片：分时图 / 日K 线切换
import { useState } from 'react'
import { CandlestickChart } from 'lucide-react'
import IntradayChart from './IntradayChart'
import KlineChart from './KlineChart'

/** StockChartCard 组件入参 */
interface Props {
  /** 股票代码，如 600519 */
  code: string
  /** 股票名称，用于卡片标题展示 */
  name?: string
}

type Tab = 'intraday' | 'kline'

export default function StockChartCard({ code, name }: Props) {
  const [tab, setTab] = useState<Tab>('intraday')

  return (
    <div className="space-y-3">
      {/* 标题 + Tab */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CandlestickChart size={16} className="text-accent" />
          <span className="text-sm font-medium text-white">
            行情图表{name ? ` - ${name}` : ''}
          </span>
          <span className="tnum text-xs text-gray-500">{code}</span>
        </div>
        <div className="flex overflow-hidden rounded-lg border border-base-500">
          <button
            onClick={() => setTab('intraday')}
            className={`px-3 py-1 text-xs font-medium transition-colors ${
              tab === 'intraday'
                ? 'bg-accent text-white'
                : 'bg-base-800 text-gray-400 hover:text-white'
            }`}
          >
            分时
          </button>
          <button
            onClick={() => setTab('kline')}
            className={`px-3 py-1 text-xs font-medium transition-colors ${
              tab === 'kline'
                ? 'bg-accent text-white'
                : 'bg-base-800 text-gray-400 hover:text-white'
            }`}
          >
            日 K
          </button>
        </div>
      </div>

      {/* 图表主体：切换时卸载重挂载，避免重复渲染 */}
      {tab === 'intraday' ? (
        <IntradayChart key={`in-${code}`} code={code} />
      ) : (
        <KlineChart key={`kl-${code}`} code={code} />
      )}
    </div>
  )
}
