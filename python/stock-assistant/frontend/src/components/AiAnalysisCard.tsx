// AI 解读卡片：加载 / 触发告警的 AI 分析
import { useEffect, useState } from 'react'
import { api } from '@/api/rest'
import type { AiAnalysis } from '@/types'
import { Sparkles, RefreshCw, CheckCircle2, AlertCircle, X } from 'lucide-react'

export default function AiAnalysisCard({ alertId }: { alertId: string }) {
  const [data, setData] = useState<AiAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [triggering, setTriggering] = useState(false)
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null)

  const load = async () => {
    try {
      const res = await api.getAiAnalysis(alertId)
      setData(res)
    } catch (e) {
      setMsg({ ok: false, text: (e as Error).message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alertId])

  const onTrigger = async () => {
    setTriggering(true)
    setMsg(null)
    try {
      const res = await api.triggerAiAnalysis(alertId, true)
      setData(res)
      setMsg({ ok: true, text: 'AI 分析已生成' })
    } catch (e) {
      setMsg({ ok: false, text: (e as Error).message })
    } finally {
      setTriggering(false)
    }
  }

  if (loading) {
    return (
      <div className="px-4 py-3 text-xs text-gray-500">AI 解读加载中…</div>
    )
  }

  return (
    <div className="space-y-3 px-4 py-3">
      {/* 已有分析结果 */}
      {data?.hasAnalysis && data.analysis ? (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-xs text-accent">
            <Sparkles size={12} />
            <span className="font-medium">AI 解读</span>
            {data.analyzedAt && (
              <span className="tnum text-gray-500">
                {new Date(data.analyzedAt).toLocaleString('zh-CN')}
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <div className="rounded-lg bg-base-700 p-2.5">
              <div className="mb-1 text-[10px] text-gray-500">解读</div>
              <p className="text-xs leading-relaxed text-gray-200">
                {data.analysis.解读}
              </p>
            </div>
            <div className="rounded-lg bg-base-700 p-2.5">
              <div className="mb-1 text-[10px] text-gray-500">建议</div>
              <p className="text-xs leading-relaxed text-gray-200">
                {data.analysis.建议}
              </p>
            </div>
            <div className="rounded-lg bg-base-700 p-2.5">
              <div className="mb-1 text-[10px] text-gray-500">风险</div>
              <p className="text-xs leading-relaxed text-gray-200">
                {data.analysis.风险}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Sparkles size={12} className="text-gray-500" />
          <span>暂无 AI 解读，点击下方按钮生成</span>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex items-center gap-2">
        <button
          onClick={onTrigger}
          disabled={triggering}
          className="flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80 disabled:opacity-50"
        >
          <RefreshCw size={12} className={triggering ? 'animate-spin' : ''} />
          {triggering ? '生成中…' : data?.hasAnalysis ? '重新生成' : '生成解读'}
        </button>
      </div>

      {/* 消息提示 */}
      {msg && (
        <div
          className={`flex items-start justify-between rounded-lg border px-2.5 py-1.5 text-xs ${
            msg.ok
              ? 'border-up/40 bg-up/10 text-up'
              : 'border-down/40 bg-down/10 text-down'
          }`}
        >
          <div className="flex items-start gap-1.5">
            {msg.ok ? (
              <CheckCircle2 size={12} className="mt-0.5 shrink-0" />
            ) : (
              <AlertCircle size={12} className="mt-0.5 shrink-0" />
            )}
            <span>{msg.text}</span>
          </div>
          <button onClick={() => setMsg(null)}>
            <X size={12} />
          </button>
        </div>
      )}
    </div>
  )
}
