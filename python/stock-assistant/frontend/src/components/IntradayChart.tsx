// 分时图组件：当日 1 分钟价格线 + 均价线 + 昨收基准 + 成交量子图
import { useEffect, useRef, useState } from 'react'
import { api } from '@/api/rest'
import type { IntradayPoint } from '@/types'

interface Props {
  code: string
}

// A 股配色约定：红涨绿跌（与境外市场相反，修改前务必确认）
const UP = '#F6465D' // 上涨：红
const DOWN = '#16C784' // 下跌：绿
const AVG_COLOR = '#F0B90B' // 均价线：金黄
const PRE_COLOR = '#848E9C' // 昨收线：灰色虚线

export default function IntradayChart({ code }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState<{
    count: number
    last: IntradayPoint | null
    preClose: number
  }>({ count: 0, last: null, preClose: 0 })

  useEffect(() => {
    let chart: import('lightweight-charts').IChartApi | null = null

    async function render() {
      if (!containerRef.current) return
      setLoading(true)
      setError('')

      try {
        const res = await api.getIntraday(code)
        setMeta({ count: res.count, last: res.data.at(-1) ?? null, preClose: res.preClose })
        if (res.count === 0) {
          setError('暂无分时数据（非交易时段且当日无成交）')
          setLoading(false)
          return
        }

        const { createChart, AreaSeries, LineSeries, HistogramSeries } =
          await import('lightweight-charts')

        // 时间戳 → HH:MM，强制按行情所属的北京时间显示刻度，
        // 不受浏览器所在时区影响
        const timeLabels = new Map<number, string>(
          res.data.map((p) => [p.timestamp, p.time]),
        )

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
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 2,
            tickMarkFormatter: (t: number) => timeLabels.get(Number(t)) ?? '',
          },
          rightPriceScale: {
            borderColor: '#2B3138',
          },
          crosshair: {
            mode: 0,
          },
          localization: {
            // 十字光标悬浮时间同样强制北京时间 HH:MM
            timeFormatter: (t: number) => timeLabels.get(Number(t)) ?? '',
          },
          // 当日分时无需平移/缩放，全部锁定，避免触摸板误触后图形异常放大
          handleScroll: false,
          handleScale: false,
        })

        const lastPrice = res.data[res.data.length - 1].price
        const isUp = res.preClose > 0 ? lastPrice >= res.preClose : true
        const priceColor = isUp ? UP : DOWN

        // 价格主图（面积线）
        const priceSeries = chart.addSeries(AreaSeries, {
          lineColor: priceColor,
          lineWidth: 2,
          topColor: isUp ? 'rgba(246,70,93,0.25)' : 'rgba(22,199,132,0.25)',
          bottomColor: 'rgba(14,18,23,0)',
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerRadius: 3,
        })
        priceSeries.setData(
          res.data.map((p) => ({
            time: p.timestamp as import('lightweight-charts').UTCTimestamp,
            value: p.price,
          })),
        )

        // 均价线
        const avgSeries = chart.addSeries(LineSeries, {
          color: AVG_COLOR,
          lineWidth: 1,
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: false,
        })
        avgSeries.setData(
          res.data
            .filter((p) => p.avg > 0)
            .map((p) => ({
              time: p.timestamp as import('lightweight-charts').UTCTimestamp,
              value: p.avg,
            })),
        )

        // 昨收基准线
        if (res.preClose > 0) {
          const preSeries = chart.addSeries(LineSeries, {
            color: PRE_COLOR,
            lineWidth: 1,
            lineStyle: 2, // 虚线
            priceLineVisible: false,
            lastValueVisible: false,
            crosshairMarkerVisible: false,
          })
          preSeries.setData(
            res.data.map((p) => ({
              time: p.timestamp as import('lightweight-charts').UTCTimestamp,
              value: res.preClose,
            })),
          )
        }

        // 成交量子图
        const volumeSeries = chart.addSeries(HistogramSeries, {
          priceFormat: { type: 'volume' },
          priceScaleId: 'vol',
        })
        chart.priceScale('vol').applyOptions({
          scaleMargins: { top: 0.8, bottom: 0 },
        })
        volumeSeries.setData(
          res.data.map((p, i) => {
            const prev = i > 0 ? res.data[i - 1].price : res.preClose
            const up = p.price >= prev
            return {
              time: p.timestamp as import('lightweight-charts').UTCTimestamp,
              value: p.volume,
              color: up ? 'rgba(246,70,93,0.4)' : 'rgba(22,199,132,0.4)',
            }
          }),
        )

        chart.timeScale().fitContent()
        setLoading(false)
      } catch (e) {
        setError((e as Error).message)
        setLoading(false)
      }
    }

    render()

    const resizeObserver = new ResizeObserver(() => {
      if (chart && containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth })
      }
    })
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current)
    }

    // 兜底：拦截触摸板捏合（ctrlKey+wheel）触发的浏览器页面缩放
    const onWheel = (e: WheelEvent) => {
      if (e.ctrlKey) e.preventDefault()
    }
    containerRef.current?.addEventListener('wheel', onWheel, { passive: false })

    return () => {
      resizeObserver.disconnect()
      containerRef.current?.removeEventListener('wheel', onWheel)
      if (chart) {
        chart.remove()
        chart = null
      }
    }
  }, [code])

  const changePct =
    meta.preClose > 0 && meta.last
      ? ((meta.last.price - meta.preClose) / meta.preClose) * 100
      : null

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-gray-400">分时图（当日 1 分钟）</span>
        <div className="flex items-center gap-3 text-[10px] text-gray-500">
          <span className="flex items-center gap-1">
            <span className="inline-block h-0.5 w-3 rounded bg-[#F6465D]" />
            价格
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-0.5 w-3 rounded" style={{ backgroundColor: AVG_COLOR }} />
            均价
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-0.5 w-3 rounded border-t border-dashed" style={{ borderColor: PRE_COLOR }} />
            昨收{meta.preClose ? ` ${meta.preClose.toFixed(2)}` : ''}
          </span>
          {meta.last && changePct !== null && (
            <span className={changePct >= 0 ? 'text-[#F6465D]' : 'text-[#16C784]'}>
              {meta.last.price.toFixed(2)} ({changePct >= 0 ? '+' : ''}
              {changePct.toFixed(2)}%)
            </span>
          )}
          {meta.count > 0 && <span className="text-gray-600">{meta.count} 点</span>}
        </div>
      </div>
      <div className="relative" style={{ minHeight: 320 }}>
        <div ref={containerRef} className="w-full overflow-hidden" />
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-500">
            加载分时数据中…
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
