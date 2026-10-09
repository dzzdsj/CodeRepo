// 告警 Toast 通知容器：实时告警从右侧滑入，自动消失
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuoteStore } from '@/stores/quotes'
import { ColorText } from '@/components/ColorText'
import { X, Bell } from 'lucide-react'

const SIGNAL_LABELS: Record<string, string> = {
  change_pct: '涨跌幅',
  speed: '涨速',
  volume: '量比',
  indicator: '指标',
}

const AUTO_DISMISS_MS = 8000

export default function ToastContainer() {
  const toasts = useQuoteStore((s) => s.toasts)
  const dismiss = useQuoteStore((s) => s.dismissToast)
  const navigate = useNavigate()

  return (
    <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-80 flex-col gap-2">
      {toasts.map((t) => (
        <ToastCard
          key={t.id}
          toastId={t.id}
          alert={t.alert}
          onDismiss={() => dismiss(t.id)}
          onClick={() => {
            dismiss(t.id)
            navigate('/history')
          }}
        />
      ))}
    </div>
  )
}

function ToastCard({
  toastId,
  alert,
  onDismiss,
  onClick,
}: {
  toastId: string
  alert: import('@/types').AlertItem
  onDismiss: () => void
  onClick: () => void
}) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, AUTO_DISMISS_MS)
    return () => clearTimeout(timer)
  }, [toastId, onDismiss])

  const time = new Date(alert.timestamp)
  const timeStr = `${String(time.getHours()).padStart(2, '0')}:${String(
    time.getMinutes(),
  ).padStart(2, '0')}:${String(time.getSeconds()).padStart(2, '0')}`

  const signalLabel = SIGNAL_LABELS[alert.signalType] || alert.signalType
  const isUp = alert.triggerValue > 0

  return (
    <div
      className={`pointer-events-auto animate-slide-in-right cursor-pointer overflow-hidden rounded-lg border shadow-card transition-opacity hover:opacity-90 ${
        isUp
          ? 'border-up/40 bg-base-700'
          : 'border-down/40 bg-base-700'
      }`}
      onClick={onClick}
    >
      {/* 顶部色条 */}
      <div
        className={`h-1 ${isUp ? 'bg-up' : 'bg-down'}`}
      />

      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <Bell size={14} className={isUp ? 'text-up' : 'text-down'} />
            <span className="text-xs font-medium text-white">
              {alert.name || alert.code}
            </span>
            <span className="tnum text-xs text-gray-500">{alert.code}</span>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDismiss()
            }}
            className="text-gray-500 transition-colors hover:text-white"
          >
            <X size={14} />
          </button>
        </div>

        <div className="mt-2 flex items-center justify-between">
          <span className="rounded bg-base-600 px-1.5 py-0.5 text-[11px] text-gray-300">
            {signalLabel}
          </span>
          <ColorText
            value={alert.triggerValue}
            className="tnum text-sm font-bold"
          />
        </div>

        <div className="mt-1.5 flex items-center justify-between text-[11px] text-gray-500">
          <span>触发价 {alert.price.toFixed(2)}</span>
          <span className="tnum">{timeStr}</span>
        </div>
      </div>
    </div>
  )
}
