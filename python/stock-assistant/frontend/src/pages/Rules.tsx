// 告警规则管理：规则列表卡片网格 + 抽屉式编辑器
import { useEffect, useState } from 'react'
import type { RuleStats } from '@/types'
import { api } from '@/api/rest'
import type { AlertRule, AlertRuleCreate, SignalType } from '@/types'
import {
  Bell,
  Plus,
  Trash2,
  Edit3,
  X,
  Save,
  AlertCircle,
  CheckCircle2,
  Copy,
} from 'lucide-react'

// ── 信号类型映射 ──
const SIGNAL_TYPES: {
  value: SignalType
  label: string
  color: string
  bg: string
}[] = [
  { value: 'change_pct', label: '涨跌幅', color: 'text-up', bg: 'bg-up/10' },
  { value: 'speed', label: '涨速', color: 'text-accent', bg: 'bg-accent/10' },
  { value: 'volume', label: '量比', color: 'text-white', bg: 'bg-base-600' },
  { value: 'indicator', label: '指标', color: 'text-down', bg: 'bg-down/10' },
]

function sigMeta(t: SignalType) {
  return SIGNAL_TYPES.find((s) => s.value === t) ?? SIGNAL_TYPES[0]
}

// 阈值字段 label 根据信号类型变化
function thresholdLabel(t: SignalType): string {
  switch (t) {
    case 'change_pct':
      return '涨跌幅阈值 (%)'
    case 'speed':
      return '涨速阈值 (%/分)'
    case 'volume':
      return '量比阈值'
    case 'indicator':
      return '指标阈值'
  }
}

function channelLabel(c: string): string {
  if (c === 'wechat') return '微信'
  if (c === 'web') return 'Web'
  return c
}

const CHANNELS = [
  { value: 'wechat', label: '微信' },
  { value: 'web', label: 'Web' },
]

// ── 指标类型选项（indicator 信号专用）──
const INDICATOR_TYPES: {
  value: string
  label: string
  thresholdLabel?: string // undefined = 阈值无意义（金叉类）
  defaultThreshold?: number
}[] = [
  { value: 'ma_golden_cross', label: 'MA金叉' },
  { value: 'macd_golden_cross', label: 'MACD金叉' },
  {
    value: 'rsi_oversold',
    label: 'RSI超卖',
    thresholdLabel: 'RSI 下限(%)',
    defaultThreshold: 30,
  },
  {
    value: 'rsi_overbought',
    label: 'RSI超买',
    thresholdLabel: 'RSI 上限(%)',
    defaultThreshold: 70,
  },
  {
    value: 'kdj_oversold',
    label: 'KDJ超卖',
    thresholdLabel: 'K 下限(%)',
    defaultThreshold: 20,
  },
  {
    value: 'kdj_overbought',
    label: 'KDJ超买',
    thresholdLabel: 'K 上限(%)',
    defaultThreshold: 80,
  },
]

function indicatorMeta(indicator?: string) {
  return INDICATOR_TYPES.find((i) => i.value === indicator)
}

const DEFAULT_FORM: AlertRuleCreate = {
  name: '',
  enabled: true,
  signalType: 'change_pct',
  params: { threshold: 5 },
  scope: { codes: null },
  sessionStart: '09:30',
  sessionEnd: '15:00',
  channels: ['wechat'],
  cooldownMinutes: 5,
}

export default function Rules() {
  // ── 列表状态 ──
  const [rules, setRules] = useState<AlertRule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // ── 抽屉编辑器 ──
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [editing, setEditing] = useState<AlertRule | null>(null) // null = 新建模式
  const [form, setForm] = useState<AlertRuleCreate>(DEFAULT_FORM)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  // ── 删除确认 ──
  const [pendingDelete, setPendingDelete] = useState<AlertRule | null>(null)
  const [deleting, setDeleting] = useState(false)

  // ── 复制规则 ──
  const [copyingId, setCopyingId] = useState<string | null>(null)

  const onCopy = async (r: AlertRule) => {
    setCopyingId(r.id)
    try {
      const created = await api.copyRule(r.id)
      setRules((prev) => [...prev, created])
      setToast({ ok: true, text: `已复制规则「${r.name}」` })
    } catch (e) {
      setToast({ ok: false, text: '复制失败：' + (e as Error).message })
    } finally {
      setCopyingId(null)
    }
  }

  // ── 全局提示 ──
  const [toast, setToast] = useState<{ ok: boolean; text: string } | null>(null)

  // 自动消失的 toast
  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 2600)
    return () => clearTimeout(t)
  }, [toast])

  // 规则统计缓存
  const [statsMap, setStatsMap] = useState<Record<string, RuleStats>>({})

  const loadRules = async () => {
    setLoading(true)
    setError('')
    try {
      const list = await api.getRules()
      setRules(list)
      // 并行加载所有规则的统计数据
      const statsResults = await Promise.allSettled(
        list.map((r) => api.getRuleStats(r.id)),
      )
      const map: Record<string, RuleStats> = {}
      statsResults.forEach((res, i) => {
        if (res.status === 'fulfilled') map[list[i].id] = res.value
      })
      setStatsMap(map)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRules()
  }, [])

  // ── 打开新建 ──
  const onNew = () => {
    setEditing(null)
    setForm({ ...DEFAULT_FORM, params: { threshold: 5 } })
    setFormError('')
    setDrawerOpen(true)
  }

  // ── 打开编辑 ──
  const onEdit = (r: AlertRule) => {
    setEditing(r)
    setForm({
      name: r.name,
      enabled: r.enabled,
      signalType: r.signalType,
      params: { ...r.params },
      scope: { codes: r.scope?.codes ?? null },
      sessionStart: r.sessionStart || '09:30',
      sessionEnd: r.sessionEnd || '15:00',
      channels: r.channels?.length ? [...r.channels] : [],
      cooldownMinutes: r.cooldownMinutes ?? 5,
    })
    setFormError('')
    setDrawerOpen(true)
  }

  const onCloseDrawer = () => {
    if (saving) return
    setDrawerOpen(false)
  }

  // ── 表单更新辅助 ──
  const update = (patch: Partial<AlertRuleCreate>) =>
    setForm((f) => ({ ...f, ...patch }))

  const updateParams = (patch: Partial<AlertRuleCreate['params']>) =>
    setForm((f) => ({ ...f, params: { ...f.params, ...patch } }))

  const onSignalTypeChange = (t: SignalType) => {
    setForm((f) => {
      const params = { ...f.params }
      // 切换时为类型专属字段补默认值（仅在未设置时）
      if (t === 'speed' && params.windowMinutes == null) {
        params.windowMinutes = 5
      }
      if (t === 'volume' && params.volMultiple == null) {
        params.volMultiple = 2
      }
      if (t === 'indicator' && !params.indicator) {
        params.indicator = 'ma_golden_cross'
      }
      return { ...f, signalType: t, params }
    })
  }

  // ── 指标类型切换 ──
  const onIndicatorChange = (indicator: string) => {
    setForm((f) => {
      const params = { ...f.params, indicator }
      const meta = indicatorMeta(indicator)
      // RSI/KDJ 类指标需要阈值，未设置时补默认值
      if (
        meta?.defaultThreshold != null &&
        (params.threshold == null || isNaN(params.threshold))
      ) {
        params.threshold = meta.defaultThreshold
      }
      return { ...f, params }
    })
  }

  const toggleChannel = (c: string) => {
    setForm((f) => ({
      ...f,
      channels: f.channels.includes(c)
        ? f.channels.filter((x) => x !== c)
        : [...f.channels, c],
    }))
  }

  // ── 保存规则 ──
  const onSave = async () => {
    setFormError('')
    if (!form.name.trim()) {
      setFormError('请输入规则名称')
      return
    }
    if (form.signalType === 'indicator' && !form.params.indicator) {
      setFormError('请选择指标类型')
      return
    }
    // 金叉类指标阈值无意义，跳过阈值校验
    const skipThresholdCheck =
      form.signalType === 'indicator' &&
      !indicatorMeta(form.params.indicator)?.thresholdLabel
    if (
      !skipThresholdCheck &&
      (form.params.threshold == null || isNaN(form.params.threshold))
    ) {
      setFormError('请输入有效的阈值')
      return
    }
    if (
      form.signalType === 'speed' &&
      (form.params.windowMinutes == null ||
        isNaN(form.params.windowMinutes as number) ||
        (form.params.windowMinutes as number) <= 0)
    ) {
      setFormError('请输入有效的涨速窗口分钟数')
      return
    }
    if (
      form.signalType === 'volume' &&
      (form.params.volMultiple == null ||
        isNaN(form.params.volMultiple as number) ||
        (form.params.volMultiple as number) <= 0)
    ) {
      setFormError('请输入有效的量比倍数')
      return
    }
    if (form.channels.length === 0) {
      setFormError('请至少选择一个推送渠道')
      return
    }
    if (form.sessionStart >= form.sessionEnd) {
      setFormError('生效时段开始时间需早于结束时间')
      return
    }

    setSaving(true)
    try {
      if (editing) {
        const updated = await api.updateRule(editing.id, form)
        setRules((prev) =>
          prev.map((r) => (r.id === editing.id ? updated : r)),
        )
        setToast({ ok: true, text: '规则已更新' })
      } else {
        const created = await api.createRule(form)
        setRules((prev) => [...prev, created])
        setToast({ ok: true, text: '规则已创建' })
      }
      setDrawerOpen(false)
    } catch (e) {
      setFormError((e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  // ── 启用/禁用切换（乐观更新 + 回滚）──
  const onToggle = async (r: AlertRule) => {
    const prev = r.enabled
    setRules((list) =>
      list.map((it) => (it.id === r.id ? { ...it, enabled: !prev } : it)),
    )
    try {
      const updated = await api.toggleRule(r.id)
      setRules((list) => list.map((it) => (it.id === r.id ? updated : it)))
    } catch (e) {
      setRules((list) =>
        list.map((it) => (it.id === r.id ? { ...it, enabled: prev } : it)),
      )
      setToast({ ok: false, text: '切换失败：' + (e as Error).message })
    }
  }

  // ── 删除确认 ──
  const onConfirmDelete = async () => {
    if (!pendingDelete) return
    setDeleting(true)
    try {
      await api.deleteRule(pendingDelete.id)
      setRules((list) => list.filter((r) => r.id !== pendingDelete.id))
      setToast({ ok: true, text: '规则已删除' })
      setPendingDelete(null)
    } catch (e) {
      setToast({ ok: false, text: '删除失败：' + (e as Error).message })
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell size={20} className="text-accent" />
          <div>
            <h1 className="text-xl font-bold text-white">告警规则</h1>
            <p className="mt-1 text-xs text-gray-500">
              配置信号检测阈值与推送渠道，盘中自动触发告警
            </p>
          </div>
        </div>
        <button
          onClick={onNew}
          className="flex items-center gap-1.5 rounded-lg bg-accent px-3.5 py-2 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80"
        >
          <Plus size={14} />
          新建规则
        </button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="flex items-center justify-between rounded-lg border border-down/40 bg-down/10 px-3 py-2 text-xs text-down">
          <span>加载失败：{error}</span>
          <button onClick={() => setError('')}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* 规则列表 */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-sm text-gray-500">
          加载中…
        </div>
      ) : rules.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-base-500 bg-base-800 py-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-base-700 text-accent">
            <Bell size={22} />
          </div>
          <p className="mt-3 text-sm text-gray-400">暂无告警规则</p>
          <p className="mt-1 text-xs text-gray-600">
            点击右上角「新建规则」开始配置
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {rules.map((r) => (
            <RuleCard
              key={r.id}
              rule={r}
              stats={statsMap[r.id]}
              onToggle={onToggle}
              onEdit={onEdit}
              onDelete={setPendingDelete}
              onCopy={onCopy}
              copying={copyingId === r.id}
            />
          ))}
        </div>
      )}

      {/* 抽屉式编辑器 */}
      {drawerOpen && (
        <div className="fixed inset-0 z-50 flex">
          {/* 遮罩 */}
          <div
            className="absolute inset-0 bg-black/60"
            onClick={onCloseDrawer}
          />
          {/* 面板 */}
          <div className="relative ml-auto flex h-full w-full max-w-md flex-col bg-base-800 shadow-card">
            {/* 抽屉头 */}
            <div className="flex items-center justify-between border-b border-base-500 px-5 py-4">
              <div className="flex items-center gap-2">
                <Bell size={18} className="text-accent" />
                <h2 className="text-sm font-semibold text-white">
                  {editing ? '编辑规则' : '新建规则'}
                </h2>
              </div>
              <button
                onClick={onCloseDrawer}
                className="rounded p-1 text-gray-500 hover:bg-base-700 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {/* 表单内容（可滚动） */}
            <div className="flex-1 space-y-4 overflow-y-auto p-5">
              {/* 规则名称 */}
              <Field label="规则名称">
                <input
                  value={form.name}
                  onChange={(e) => update({ name: e.target.value })}
                  placeholder="如：茅台涨跌幅超 3%"
                  maxLength={40}
                  className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none"
                />
              </Field>

              {/* 信号类型 Tab */}
              <Field label="信号类型">
                <div className="flex gap-1 rounded-lg border border-base-500 bg-base-700 p-1">
                  {SIGNAL_TYPES.map((s) => (
                    <button
                      key={s.value}
                      onClick={() => onSignalTypeChange(s.value)}
                      className={`flex-1 rounded px-2 py-1.5 text-xs transition-colors ${
                        form.signalType === s.value
                          ? 'bg-accent text-base-900'
                          : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </Field>

              {/* 指标类型（仅 indicator 显示） */}
              {form.signalType === 'indicator' && (
                <Field label="指标类型" hint="选择具体的技术指标">
                  <select
                    value={form.params.indicator ?? ''}
                    onChange={(e) => onIndicatorChange(e.target.value)}
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none"
                  >
                    {INDICATOR_TYPES.map((i) => (
                      <option key={i.value} value={i.value}>
                        {i.label}
                      </option>
                    ))}
                  </select>
                </Field>
              )}

              {/* 阈值（金叉类指标隐藏） */}
              {!(
                form.signalType === 'indicator' &&
                !indicatorMeta(form.params.indicator)?.thresholdLabel
              ) && (
                <Field
                  label={
                    form.signalType === 'indicator'
                      ? (indicatorMeta(form.params.indicator)
                          ?.thresholdLabel ?? '指标阈值')
                      : thresholdLabel(form.signalType)
                  }
                >
                  <input
                    type="number"
                    step="0.1"
                    value={
                      form.params.threshold == null
                        ? ''
                        : form.params.threshold
                    }
                    onChange={(e) =>
                      updateParams({
                        threshold: parseFloat(e.target.value),
                      })
                    }
                    placeholder="请输入数值"
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none tnum"
                  />
                </Field>
              )}

              {/* 涨速窗口分钟数（仅 speed 显示） */}
              {form.signalType === 'speed' && (
                <Field label="涨速窗口分钟数" hint="统计该分钟数内的涨跌幅速度">
                  <input
                    type="number"
                    step="1"
                    min={1}
                    value={
                      form.params.windowMinutes == null
                        ? ''
                        : form.params.windowMinutes
                    }
                    onChange={(e) =>
                      updateParams({
                        windowMinutes: parseInt(e.target.value, 10),
                      })
                    }
                    placeholder="如：5"
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none tnum"
                  />
                </Field>
              )}

              {/* 量比倍数（仅 volume 显示） */}
              {form.signalType === 'volume' && (
                <Field label="量比倍数" hint="成交量相对于近期均量的倍数">
                  <input
                    type="number"
                    step="0.1"
                    min={0.1}
                    value={
                      form.params.volMultiple == null
                        ? ''
                        : form.params.volMultiple
                    }
                    onChange={(e) =>
                      updateParams({
                        volMultiple: parseFloat(e.target.value),
                      })
                    }
                    placeholder="如：2.0"
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none tnum"
                  />
                </Field>
              )}

              {/* 生效时段 */}
              <div className="grid grid-cols-2 gap-3">
                <Field label="生效开始">
                  <input
                    type="time"
                    value={form.sessionStart}
                    onChange={(e) =>
                      update({ sessionStart: e.target.value })
                    }
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none tnum [color-scheme:dark]"
                  />
                </Field>
                <Field label="生效结束">
                  <input
                    type="time"
                    value={form.sessionEnd}
                    onChange={(e) => update({ sessionEnd: e.target.value })}
                    className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none tnum [color-scheme:dark]"
                  />
                </Field>
              </div>

              {/* 推送渠道 */}
              <Field label="推送渠道">
                <div className="flex gap-2">
                  {CHANNELS.map((c) => {
                    const checked = form.channels.includes(c.value)
                    return (
                      <button
                        key={c.value}
                        onClick={() => toggleChannel(c.value)}
                        className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs transition-colors ${
                          checked
                            ? 'border-accent bg-accent/10 text-accent'
                            : 'border-base-500 bg-base-700 text-gray-400 hover:text-white'
                        }`}
                      >
                        <span
                          className={`flex h-3.5 w-3.5 items-center justify-center rounded border ${
                            checked
                              ? 'border-accent bg-accent text-base-900'
                              : 'border-base-500'
                          }`}
                        >
                          {checked && <CheckCircle2 size={10} />}
                        </span>
                        {c.label}
                      </button>
                    )
                  })}
                </div>
              </Field>

              {/* 冷却时间 */}
              <Field label="冷却时间（分钟）" hint="同一规则触发后的间隔时间">
                <input
                  type="number"
                  step="1"
                  min={0}
                  value={form.cooldownMinutes}
                  onChange={(e) =>
                    update({ cooldownMinutes: parseInt(e.target.value, 10) })
                  }
                  placeholder="如：5"
                  className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none tnum"
                />
              </Field>

              {/* 启用开关 */}
              <div className="flex items-center justify-between rounded-lg border border-base-500 bg-base-700 px-3 py-2.5">
                <label className="text-xs text-gray-400">启用规则</label>
                <button
                  onClick={() => update({ enabled: !form.enabled })}
                  className={`relative h-6 w-11 rounded-full transition-colors ${
                    form.enabled ? 'bg-accent' : 'bg-base-600'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                      form.enabled ? 'translate-x-5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>

              {/* 表单错误 */}
              {formError && (
                <div className="flex items-start gap-1.5 rounded-lg border border-down/40 bg-down/10 px-3 py-2 text-xs text-down">
                  <AlertCircle size={14} className="mt-0.5 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}
            </div>

            {/* 抽屉底部 */}
            <div className="border-t border-base-500 p-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={onSave}
                  disabled={saving}
                  className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-accent px-4 py-2.5 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80 disabled:opacity-50"
                >
                  <Save size={14} />
                  {saving ? '保存中…' : '保存'}
                </button>
                <button
                  onClick={onCloseDrawer}
                  disabled={saving}
                  className="rounded-lg border border-base-500 bg-base-700 px-4 py-2.5 text-xs font-medium text-white transition-colors hover:bg-base-600 disabled:opacity-50"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 删除确认弹窗 */}
      {pendingDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => !deleting && setPendingDelete(null)}
          />
          <div className="relative w-full max-w-sm rounded-xl border border-base-500 bg-base-800 p-5 shadow-card">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-down/10 text-down">
                <AlertCircle size={18} />
              </div>
              <div className="min-w-0">
                <h3 className="text-sm font-semibold text-white">删除规则</h3>
                <p className="mt-1 text-xs text-gray-400">
                  确定要删除规则「
                  <span className="text-white">{pendingDelete.name}</span>
                  」吗？该操作不可撤销。
                </p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-end gap-2">
              <button
                onClick={() => setPendingDelete(null)}
                disabled={deleting}
                className="rounded-lg border border-base-500 bg-base-700 px-3 py-1.5 text-xs text-white transition-colors hover:bg-base-600 disabled:opacity-50"
              >
                取消
              </button>
              <button
                onClick={onConfirmDelete}
                disabled={deleting}
                className="flex items-center gap-1 rounded-lg bg-down px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-down/80 disabled:opacity-50"
              >
                <Trash2 size={13} />
                {deleting ? '删除中…' : '确认删除'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 全局 toast */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2">
          <div
            className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-xs shadow-card ${
              toast.ok
                ? 'border-up/40 bg-base-800 text-up'
                : 'border-down/40 bg-base-800 text-down'
            }`}
          >
            {toast.ok ? (
              <CheckCircle2 size={14} />
            ) : (
              <AlertCircle size={14} />
            )}
            <span>{toast.text}</span>
            <button
              onClick={() => setToast(null)}
              className="ml-2 text-gray-500 hover:text-white"
            >
              <X size={12} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ── 规则卡片 ──
function RuleCard({
  rule,
  stats,
  onToggle,
  onEdit,
  onDelete,
  onCopy,
  copying,
}: {
  rule: AlertRule
  stats?: RuleStats
  onToggle: (r: AlertRule) => void
  onEdit: (r: AlertRule) => void
  onDelete: (r: AlertRule) => void
  onCopy: (r: AlertRule) => void
  copying: boolean
}) {
  const meta = sigMeta(rule.signalType)
  const enabled = rule.enabled

  return (
    <div className="flex flex-col rounded-xl border border-base-500 bg-base-700 p-4 shadow-card transition-colors hover:border-base-400">
      {/* 头部：名称 + 启用开关 */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-medium text-white">
            {rule.name}
          </h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
            <span
              className={`rounded px-1.5 py-0.5 text-[10px] ${meta.bg} ${meta.color}`}
            >
              {meta.label}
            </span>
            <span
              className={`rounded px-1.5 py-0.5 text-[10px] ${
                enabled ? 'bg-up/10 text-up' : 'bg-base-600 text-gray-500'
              }`}
            >
              {enabled ? '启用' : '停用'}
            </span>
          </div>
        </div>
        <button
          onClick={() => onToggle(rule)}
          className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${
            enabled ? 'bg-accent' : 'bg-base-600'
          }`}
          title={enabled ? '点击禁用' : '点击启用'}
        >
          <span
            className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${
              enabled ? 'translate-x-4' : 'translate-x-0.5'
            }`}
          />
        </button>
      </div>

      {/* 参数网格 */}
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        {rule.signalType === 'indicator' && rule.params.indicator ? (
          <Param
            label="指标"
            value={
              indicatorMeta(rule.params.indicator)?.label ??
              rule.params.indicator
            }
          />
        ) : (
          <Param label="阈值" value={fmtThreshold(rule)} />
        )}
        {rule.signalType === 'indicator' &&
          indicatorMeta(rule.params.indicator)?.thresholdLabel && (
            <Param label="阈值" value={fmtThreshold(rule)} />
          )}
        {rule.signalType === 'speed' &&
          rule.params.windowMinutes != null && (
            <Param label="窗口" value={`${rule.params.windowMinutes} 分`} />
          )}
        {rule.signalType === 'volume' &&
          rule.params.volMultiple != null && (
            <Param label="量比" value={`${rule.params.volMultiple} 倍`} />
          )}
        <Param
          label="时段"
          value={`${rule.sessionStart}-${rule.sessionEnd}`}
        />
        <Param label="冷却" value={`${rule.cooldownMinutes} 分`} />
      </div>

      {/* 推送渠道 */}
      <div className="mt-2.5 flex items-center gap-1.5 text-[10px] text-gray-500">
        <Bell size={11} />
        <span>
          {rule.channels?.length
            ? rule.channels.map(channelLabel).join(' / ')
            : '无渠道'}
        </span>
      </div>

      {/* 触发统计 */}
      {stats && (
        <div className="mt-2.5 grid grid-cols-3 gap-1.5 rounded-lg border border-base-500/50 bg-base-800/50 px-2.5 py-2">
          <StatCell label="总触发" value={stats.totalTriggers} />
          <StatCell label="近7天" value={stats.weekTriggers} />
          <StatCell
            label="推送率"
            value={`${stats.pushRate}%`}
            highlight={stats.pushRate > 0}
          />
        </div>
      )}

      {/* 操作按钮 */}
      <div className="mt-3 flex items-center gap-1 border-t border-base-500/50 pt-3">
        <button
          onClick={() => onEdit(rule)}
          className="flex items-center gap-1 rounded px-2 py-1 text-xs text-gray-400 transition-colors hover:bg-base-600 hover:text-white"
        >
          <Edit3 size={13} /> 编辑
        </button>
        <button
          onClick={() => onCopy(rule)}
          disabled={copying}
          className="flex items-center gap-1 rounded px-2 py-1 text-xs text-gray-400 transition-colors hover:bg-base-600 hover:text-white disabled:opacity-50"
        >
          <Copy size={13} /> {copying ? '复制中…' : '复制'}
        </button>
        <button
          onClick={() => onDelete(rule)}
          className="flex items-center gap-1 rounded px-2 py-1 text-xs text-gray-400 transition-colors hover:bg-down/10 hover:text-down"
        >
          <Trash2 size={13} /> 删除
        </button>
      </div>
    </div>
  )
}

// ── 统计单元格 ──
function StatCell({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: number | string
  highlight?: boolean
}) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-[9px] text-gray-500">{label}</span>
      <span
        className={`tnum text-xs font-medium ${
          highlight ? 'text-up' : 'text-gray-300'
        }`}
      >
        {value}
      </span>
    </div>
  )
}

// ── 参数项 ──
function Param({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] text-gray-500">{label}</span>
      <span className="tnum text-gray-300">{value}</span>
    </div>
  )
}

// ── 字段包装 ──
function Field({
  label,
  children,
  hint,
}: {
  label: string
  children: React.ReactNode
  hint?: string
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs text-gray-400">{label}</label>
      {children}
      {hint && <p className="mt-1 text-[10px] text-gray-600">{hint}</p>}
    </div>
  )
}

// ── 阈值格式化 ──
function fmtThreshold(rule: AlertRule): string {
  const t = rule.params.threshold
  if (rule.signalType === 'indicator') {
    const meta = indicatorMeta(rule.params.indicator)
    if (!meta?.thresholdLabel) return '--'
    if (t == null || isNaN(t)) return '--'
    return `${t}%`
  }
  if (t == null || isNaN(t)) return '--'
  if (rule.signalType === 'change_pct') return `${t}%`
  if (rule.signalType === 'speed') return `${t}%/分`
  if (rule.signalType === 'volume') return `${t}`
  return `${t}`
}
