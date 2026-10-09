import { useEffect, useMemo, useState } from 'react'
import { TrendingUp, TrendingDown, RefreshCw, Layers } from 'lucide-react'
import { api } from '@/api/rest'
import type { SectorFundFlow } from '@/types'

const REFRESH_INTERVAL = 30_000

function fmtYuan(v: number): string {
  if (v == null || Number.isNaN(v)) return '--'
  const abs = Math.abs(v)
  if (abs >= 1e8) return `${(v / 1e8).toFixed(2)}亿`
  if (abs >= 1e4) return `${(v / 1e4).toFixed(1)}万`
  return v.toFixed(0)
}

function fmtPct(v: number): string {
  if (v == null || Number.isNaN(v)) return '--'
  return `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`
}

type SectorType = 'industry' | 'concept'

export default function SectorFundFlowPage() {
  const [sectorType, setSectorType] = useState<SectorType>('industry')
  const [data, setData] = useState<SectorFundFlow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<string>('')

  const fetchData = async (type: SectorType) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.getSectorFundFlow(type, 100)
      setData(res.data)
      setLastUpdate(new Date().toLocaleTimeString('zh-CN'))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '获取数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData(sectorType)
    const timer = setInterval(() => fetchData(sectorType), REFRESH_INTERVAL)
    return () => clearInterval(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sectorType])

  // 按主力净流入排序：流入榜和流出榜
  const { topInflow, topOutflow } = useMemo(() => {
    const sorted = [...data].sort((a, b) => b.mainNetInflow - a.mainNetInflow)
    return {
      topInflow: sorted.slice(0, 10),
      topOutflow: sorted.slice(-10).reverse(),
    }
  }, [data])

  return (
    <div className="space-y-4">
      {/* 头部 */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-bold text-white">
            <Layers className="text-accent" size={22} />
            板块资金流向
          </h1>
          <p className="mt-1 text-xs text-gray-500">
            实时追踪行业/概念板块主力资金流入流出排名
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex overflow-hidden rounded-lg border border-base-500">
            <button
              onClick={() => setSectorType('industry')}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                sectorType === 'industry'
                  ? 'bg-accent text-white'
                  : 'bg-base-800 text-gray-400 hover:text-white'
              }`}
            >
              行业板块
            </button>
            <button
              onClick={() => setSectorType('concept')}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                sectorType === 'concept'
                  ? 'bg-accent text-white'
                  : 'bg-base-800 text-gray-400 hover:text-white'
              }`}
            >
              概念板块
            </button>
          </div>
          <button
            onClick={() => fetchData(sectorType)}
            disabled={loading}
            className="flex items-center gap-1 rounded-lg border border-base-500 px-3 py-1.5 text-xs text-gray-300 hover:text-white disabled:opacity-50"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            刷新
          </button>
          {lastUpdate && (
            <span className="text-xs text-gray-500">更新于 {lastUpdate}</span>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading && data.length === 0 && (
        <div className="flex h-64 items-center justify-center text-gray-500">
          <RefreshCw className="animate-spin" size={20} />
          <span className="ml-2">加载中...</span>
        </div>
      )}

      {data.length > 0 && (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          {/* 资金流入榜 */}
          <div className="rounded-lg border border-base-500 bg-base-800">
            <div className="flex items-center gap-2 border-b border-base-500 px-4 py-3">
              <TrendingUp className="text-red-500" size={18} />
              <h2 className="text-sm font-semibold text-white">主力资金流入 TOP 10</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-500">
                    <th className="px-3 py-2 text-left">排名</th>
                    <th className="px-3 py-2 text-left">板块</th>
                    <th className="px-3 py-2 text-right">涨跌幅</th>
                    <th className="px-3 py-2 text-right">主力净流入</th>
                    <th className="px-3 py-2 text-right">占比</th>
                  </tr>
                </thead>
                <tbody>
                  {topInflow.map((s, i) => (
                    <tr
                      key={s.code}
                      className="border-t border-base-500 hover:bg-base-700/50"
                    >
                      <td className="px-3 py-2">
                        <span
                          className={`inline-flex h-5 w-5 items-center justify-center rounded text-xs font-bold ${
                            i < 3 ? 'bg-red-500 text-white' : 'bg-base-600 text-gray-300'
                          }`}
                        >
                          {i + 1}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-medium text-white">{s.name}</td>
                      <td
                        className={`px-3 py-2 text-right ${
                          s.changePct >= 0 ? 'text-red-400' : 'text-green-400'
                        }`}
                      >
                        {fmtPct(s.changePct)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-red-400">
                        {fmtYuan(s.mainNetInflow)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-red-400">
                        {fmtPct(s.mainNetInflowRatio)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* 资金流出榜 */}
          <div className="rounded-lg border border-base-500 bg-base-800">
            <div className="flex items-center gap-2 border-b border-base-500 px-4 py-3">
              <TrendingDown className="text-green-500" size={18} />
              <h2 className="text-sm font-semibold text-white">主力资金流出 TOP 10</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-500">
                    <th className="px-3 py-2 text-left">排名</th>
                    <th className="px-3 py-2 text-left">板块</th>
                    <th className="px-3 py-2 text-right">涨跌幅</th>
                    <th className="px-3 py-2 text-right">主力净流出</th>
                    <th className="px-3 py-2 text-right">占比</th>
                  </tr>
                </thead>
                <tbody>
                  {topOutflow.map((s, i) => (
                    <tr
                      key={s.code}
                      className="border-t border-base-500 hover:bg-base-700/50"
                    >
                      <td className="px-3 py-2">
                        <span
                          className={`inline-flex h-5 w-5 items-center justify-center rounded text-xs font-bold ${
                            i < 3 ? 'bg-green-500 text-white' : 'bg-base-600 text-gray-300'
                          }`}
                        >
                          {i + 1}
                        </span>
                      </td>
                      <td className="px-3 py-2 font-medium text-white">{s.name}</td>
                      <td
                        className={`px-3 py-2 text-right ${
                          s.changePct >= 0 ? 'text-red-400' : 'text-green-400'
                        }`}
                      >
                        {fmtPct(s.changePct)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-green-400">
                        {fmtYuan(s.mainNetInflow)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-green-400">
                        {fmtPct(s.mainNetInflowRatio)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 完整列表 */}
      {data.length > 0 && (
        <div className="rounded-lg border border-base-500 bg-base-800">
          <div className="border-b border-base-500 px-4 py-3">
            <h2 className="text-sm font-semibold text-white">
              全部板块 ({data.length})
            </h2>
          </div>
          <div className="max-h-[480px] overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-base-800">
                <tr className="text-xs text-gray-500">
                  <th className="px-3 py-2 text-left">板块</th>
                  <th className="px-3 py-2 text-right">涨跌幅</th>
                  <th className="px-3 py-2 text-right">主力净流入</th>
                  <th className="px-3 py-2 text-right">占比</th>
                  <th className="px-3 py-2 text-right">超大单</th>
                  <th className="px-3 py-2 text-right">大单</th>
                  <th className="px-3 py-2 text-right">中单</th>
                  <th className="px-3 py-2 text-right">小单</th>
                </tr>
              </thead>
              <tbody>
                {data.map((s) => (
                  <tr
                    key={s.code}
                    className="border-t border-base-500 hover:bg-base-700/50"
                  >
                    <td className="px-3 py-2 font-medium text-white">{s.name}</td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.changePct >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtPct(s.changePct)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.mainNetInflow >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtYuan(s.mainNetInflow)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.mainNetInflowRatio >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtPct(s.mainNetInflowRatio)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.superLargeNetInflow >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtYuan(s.superLargeNetInflow)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.largeNetInflow >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtYuan(s.largeNetInflow)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.mediumNetInflow >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtYuan(s.mediumNetInflow)}
                    </td>
                    <td
                      className={`px-3 py-2 text-right font-mono ${
                        s.smallNetInflow >= 0 ? 'text-red-400' : 'text-green-400'
                      }`}
                    >
                      {fmtYuan(s.smallNetInflow)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
