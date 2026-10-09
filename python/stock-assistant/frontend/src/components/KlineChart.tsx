// K 线图组件：使用 lightweight-charts 渲染日 K 线 + 成交量 + MA 均线叠加
import { useEffect, useRef, useState } from 'react'
import { api } from '@/api/rest'
import type { KlineBar } from '@/types'

interface Props {
  code: string
  /** 告警触发日期（YYYY-MM-DD），用于在图上标注 */
  alertDate?: string
  days?: number
}

// MA 均线配置：周期 + 颜色
const MA_LINES = [
  { period: 5, color: '#F0B90B' }, // MA5 - 金黄
  { period: 10, color: '#E031FF' }, // MA10 - 紫红
  { period: 20, color: '#00B7D4' }, // MA20 - 青色
]

/** 计算简单移动平均线 */
function calcMA(data: KlineBar[], period: number) {
  const result: { time: string; value: number }[] = []
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    result.push({ time: data[i].date, value: sum / period })
  }
  return result
}

export default function KlineChart({ code, alertDate, days = 60 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [count, setCount] = useState(0)

  useEffect(() => {
    let chart: import('lightweight-charts').IChartApi | null = null

    async function render() {
      if (!containerRef.current) return
      setLoading(true)
      setError('')

      try {
        const res = await api.getKline(code, days)
        setCount(res.count)
        if (res.count === 0) {
          setError('暂无 K 线数据')
          setLoading(false)
          return
        }

        // 动态导入 lightweight-charts
        const { createChart, CandlestickSeries, HistogramSeries, LineSeries, createSeriesMarkers } =
          await import('lightweight-charts')

        // 清空容器
        containerRef.current!.innerHTML = ''

        chart = createChart(containerRef.current!, {
          width: containerRef.current!.clientWidth,
          height: 320,
          layout: {
            background: { color: '#0E1217' },
            textColor: '#848E9C',
            fontSize: 11,
          },
          grid: {
            vertLines: { color: '#1E2329' },
            horzLines: { color: '#1E2329' },
          },
          timeScale: {
            borderColor: '#2B3138',
            timeVisible: false,
          },
          rightPriceScale: {
            borderColor: '#2B3138',
          },
          crosshair: {
            mode: 0,
          },
        })

        // K 线主图
        const candleSeries = chart.addSeries(CandlestickSeries, {
          upColor: '#F6465D',
          downColor: '#16C784',
          borderUpColor: '#F6465D',
          borderDownColor: '#16C784',
          wickUpColor: '#F6465D',
          wickDownColor: '#16C784',
        })

        const candleData = res.data.map((b: KlineBar) => ({
          time: b.date as string,
          open: b.open,
          high: b.high,
          low: b.low,
          close: b.close,
        }))
        candleSeries.setData(candleData)

        // MA 均线叠加
        for (const ma of MA_LINES) {
          if (res.data.length >= ma.period) {
            const maData = calcMA(res.data, ma.period)
            const maSeries = chart.addSeries(LineSeries, {
              color: ma.color,
              lineWidth: 1,
              priceLineVisible: false,
              lastValueVisible: false,
              crosshairMarkerVisible: false,
            })
            maSeries.setData(maData)
          }
        }

        // 成交量子图
        const volumeSeries = chart.addSeries(HistogramSeries, {
          priceFormat: { type: 'volume' },
          priceScaleId: 'vol',
        })
        chart.priceScale('vol').applyOptions({
          scaleMargins: { top: 0.8, bottom: 0 },
        })

        const volData = res.data.map((b: KlineBar) => ({
          time: b.date as string,
          value: b.volume,
          color: b.close >= b.open ? 'rgba(246,70,93,0.4)' : 'rgba(22,199,132,0.4)',
        }))
        volumeSeries.setData(volData)

        // 标注告警触发日（v5 使用 createSeriesMarkers）
        if (alertDate) {
          const markerIdx = candleData.findIndex(
            (d) => d.time === alertDate,
          )
          if (markerIdx >= 0) {
            createSeriesMarkers(candleSeries, [
              {
                time: alertDate,
                position: 'aboveBar',
                color: '#F0B90B',
                shape: 'circle',
                text: '告警',
              },
            ])
          }
        }

        chart.timeScale().fitContent()
        setLoading(false)
      } catch (e) {
        setError((e as Error).message)
        setLoading(false)
      }
    }

    render()

    // 响应式：监听容器宽度变化
    const resizeObserver = new ResizeObserver(() => {
      if (chart && containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    })
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current)
    }

    return () => {
      resizeObserver.disconnect()
      if (chart) {
        chart.remove()
        chart = null
      }
    }
  }, [code, days, alertDate])

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-400">
          日 K 线图（近 {days} 天）
        </span>
        <div className="flex items-center gap-3">
          {/* MA 图例 */}
          {MA_LINES.map((ma) => (
            <span key={ma.period} className="flex items-center gap-1 text-[10px] text-gray-500">
              <span
                className="inline-block h-0.5 w-3 rounded"
                style={{ backgroundColor: ma.color }}
              />
              MA{ma.period}
            </span>
          ))}
          {count > 0 && (
            <span className="text-xs text-gray-600">{count} 根</span>
          )}
        </div>
      </div>
      <div className="relative" style={{ minHeight: 320 }}>
        {/* 图表容器（始终渲染，保持宽度） */}
        <div ref={containerRef} />
        {/* 加载/错误遮罩 */}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-500">
            加载 K 线数据中…
          </div>
        )}
        {error && !loading && (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-600">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}
