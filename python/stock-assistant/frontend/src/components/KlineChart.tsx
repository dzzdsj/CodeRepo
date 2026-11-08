// K 线图组件：使用 lightweight-charts 渲染日 K 线 + 成交量 + MA 均线叠加
import { useEffect, useRef, useState } from 'react'
import { Maximize2 } from 'lucide-react'
import { api } from '@/api/rest'
import type { KlineBar } from '@/types'

interface Props {
  code: string
  /** 告警触发日期（YYYY-MM-DD），用于在图上标注 */
  alertDate?: string
  /** 外部固定天数；传入后不显示范围切换器（如告警详情页） */
  days?: number
}

// MA 均线配置：周期 + 颜色
const MA_LINES = [
  { period: 5, color: '#F0B90B' }, // MA5 - 金黄
  { period: 10, color: '#E031FF' }, // MA10 - 紫红
  { period: 20, color: '#00B7D4' }, // MA20 - 青色
]

// 时间范围档位（交易日约 250 天/年）
const RANGE_OPTIONS = [
  { label: '3月', days: 60 },
  { label: '1年', days: 250 },
  { label: '3年', days: 750 },
  { label: '全部', days: 9999 },
] as const

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

export default function KlineChart({ code, alertDate, days }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [count, setCount] = useState(0)
  const [firstDate, setFirstDate] = useState('')
  const [lastDate, setLastDate] = useState('')
  // 外部未固定天数时，使用内部可选范围（默认近 1 年）
  const [rangeDays, setRangeDays] = useState<number>(250)
  const effectiveDays = days ?? rangeDays
  // 图表实例（供“重置视图”按钮调用 fitContent）
  const chartApiRef = useRef<import('lightweight-charts').IChartApi | null>(null)

  useEffect(() => {
    let chart: import('lightweight-charts').IChartApi | null = null
    let rangeHandler:
      | ((range: import('lightweight-charts').LogicalRange | null) => void)
      | undefined
    // 竞态防护：快速切换范围档位时旧请求尚未返回，cleanup 先行触发；
    // 旧 render 在 await 恢复处检测到取消即退出，避免旧数据图表覆盖新图表
    let cancelled = false

    async function render() {
      if (!containerRef.current) return
      setLoading(true)
      setError('')

      try {
        const res = await api.getKline(code, effectiveDays)
        if (cancelled) return
        setCount(res.count)
        if (res.count === 0) {
          setError('暂无 K 线数据')
          setLoading(false)
          return
        }
        setFirstDate(res.data[0].date)
        setLastDate(res.data[res.data.length - 1].date)

        // 动态导入 lightweight-charts
        const { createChart, CandlestickSeries, HistogramSeries, LineSeries, createSeriesMarkers } =
          await import('lightweight-charts')
        if (cancelled || !containerRef.current) return

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
          // 交互：保留触控板/鼠标的全部平移与缩放能力
          // （触控板双指水平滑动=平移、垂直滑动/捏合=缩放），
          // 放大极限与滚动边界由下方 visibleLogicalRange 钳制，
          // 避免误触后 K 线被放到“巨大”或拖出数据范围。
          handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
            horzTouchDrag: true,
            vertTouchDrag: false,
          },
          handleScale: {
            mouseWheel: true,
            pinch: true,
            axisPressedMouseMove: true,
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

        // ── 可视范围钳制：限制最大放大倍数与滚动边界 ──
        // logical range 中 0≈首根K线，LEN≈末根K线；from/to 之间为可见根数。
        const LEN = res.data.length
        const MIN_BARS = 10 // 最多放大到只剩 10 根，避免“K 线巨大”
        const MAX_BARS = LEN + 30 // 缩小时至多看到全部数据 + 少量留白
        const EDGE = 15 // 首根之前/末根之后允许的留白
        let applyingRange = false
        const onVisibleRangeChange = (
          range: import('lightweight-charts').LogicalRange | null,
        ) => {
          if (!range || applyingRange || !chart) return
          let from = Math.min(range.from, range.to)
          let to = Math.max(range.from, range.to)
          const span = to - from
          if (span < MIN_BARS) {
            // 以当前视图中心为锚扩大到最小根数；
            // 中心钳制到数据区间内，避免光标在左右留白区缩放后整屏空白
            const mid = Math.min(Math.max((from + to) / 2, 0), LEN - 1)
            from = mid - MIN_BARS / 2
            to = mid + MIN_BARS / 2
          } else if (span > MAX_BARS) {
            const mid = (from + to) / 2
            from = mid - MAX_BARS / 2
            to = mid + MAX_BARS / 2
          }
          // 左右边界：不允许拖出数据两端太远
          if (from < -EDGE) {
            to += -EDGE - from
            from = -EDGE
          }
          if (to > LEN + EDGE) {
            from -= to - (LEN + EDGE)
            to = LEN + EDGE
          }
          // 边界修正后再次保证最小根数
          if (to - from < MIN_BARS) to = from + MIN_BARS
          if (
            Math.abs(from - range.from) > 1e-6 ||
            Math.abs(to - range.to) > 1e-6
          ) {
            applyingRange = true
            chart.timeScale().setVisibleLogicalRange({ from, to })
            applyingRange = false
          }
        }
        rangeHandler = onVisibleRangeChange
        chart.timeScale().subscribeVisibleLogicalRangeChange(rangeHandler)

        chartApiRef.current = chart
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

    // 兜底：拦截触摸板捏合（ctrlKey+wheel），阻止浏览器整页缩放；
    // 图表自身仍会收到该事件并按捏合缩放时间轴。
    // 注：光标悬停在图表上时，普通滚轮/双指滑动由图表接管（缩放时间轴），
    // 不会滚动页面——这是股票图表的常规交互，滚动页面请将光标移出图表。
    const onWheel = (e: WheelEvent) => {
      if (e.ctrlKey) e.preventDefault()
    }
    containerRef.current?.addEventListener('wheel', onWheel, { passive: false })

    return () => {
      cancelled = true
      resizeObserver.disconnect()
      containerRef.current?.removeEventListener('wheel', onWheel)
      if (chart && rangeHandler) {
        chart.timeScale().unsubscribeVisibleLogicalRangeChange(rangeHandler)
      }
      chartApiRef.current = null
      if (chart) {
        chart.remove()
        chart = null
      }
    }
  }, [code, effectiveDays, alertDate])

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-gray-400">
            {days !== undefined ? `日 K 线图（近 ${days} 天）` : '日 K 线图'}
          </span>
          {/* 范围切换：仅在未被外部固定天数时显示 */}
          {days === undefined && (
            <div className="flex overflow-hidden rounded-md border border-base-500">
              {RANGE_OPTIONS.map((opt) => (
                <button
                  key={opt.days}
                  onClick={() => setRangeDays(opt.days)}
                  className={`px-2 py-0.5 text-[11px] font-medium transition-colors ${
                    rangeDays === opt.days
                      ? 'bg-accent text-white'
                      : 'bg-base-800 text-gray-400 hover:text-white'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
        </div>
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
            <span className="tnum text-xs text-gray-600">
              {firstDate} ~ {lastDate} · {count} 根
            </span>
          )}
          {count > 0 && (
            <button
              type="button"
              title="重置视图（自适应全部 K 线）"
              onClick={() => chartApiRef.current?.timeScale().fitContent()}
              className="flex items-center rounded p-0.5 text-gray-500 transition-colors hover:text-white"
            >
              <Maximize2 size={13} />
            </button>
          )}
        </div>
      </div>
      <div className="relative" style={{ minHeight: 320 }}>
        {/* 图表容器（始终渲染，保持宽度）；overflow-hidden 防止 canvas 异常溢出 */}
        <div ref={containerRef} className="w-full overflow-hidden" />
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
