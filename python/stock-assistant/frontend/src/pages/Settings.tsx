// 系统设置：微信推送配置 + 调度配置 + AI 模型配置
import { useEffect, useState } from 'react'
import { api } from '@/api/rest'
import type {
  PushConfig,
  SchedulerConfig,
  PushTestResult,
  AiConfig,
  AiProvider,
  AiTestResult,
} from '@/types'
import {
  Settings as SettingsIcon,
  Bell,
  Clock,
  Database,
  Eye,
  EyeOff,
  Save,
  Send,
  X,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react'

const PROVIDERS = [
  { value: 'serverchan', label: 'Server酱' },
  { value: 'pushplus', label: 'PushPlus' },
]

const DATA_SOURCES = [
  { value: 'akshare', label: 'AkShare' },
  { value: 'tushare', label: 'Tushare' },
]

export default function Settings() {
  // ── 推送配置 ──
  const [pushProvider, setPushProvider] = useState('serverchan')
  const [pushToken, setPushToken] = useState('')
  const [pushEnabled, setPushEnabled] = useState(false)
  const [hasToken, setHasToken] = useState(false)
  const [showToken, setShowToken] = useState(false)
  const [pushSaving, setPushSaving] = useState(false)
  const [pushTesting, setPushTesting] = useState(false)
  const [pushMsg, setPushMsg] = useState<{ ok: boolean; text: string } | null>(null)

  // ── 调度配置 ──
  const [dataSource, setDataSource] = useState('akshare')
  const [interval, setIntervalSec] = useState(5)
  const [sessionStart, setSessionStart] = useState('09:30')
  const [sessionEnd, setSessionEnd] = useState('15:00')
  const [schedSaving, setSchedSaving] = useState(false)
  const [schedMsg, setSchedMsg] = useState<{ ok: boolean; text: string } | null>(null)

  // ── AI 模型配置 ──
  const [aiProviders, setAiProviders] = useState<AiProvider[]>([])
  const [aiProvider, setAiProvider] = useState('zhipu')
  const [aiBaseUrl, setAiBaseUrl] = useState('')
  const [aiModel, setAiModel] = useState('')
  const [aiApiKey, setAiApiKey] = useState('')
  const [aiEnabled, setAiEnabled] = useState(false)
  const [hasApiKey, setHasApiKey] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [aiSaving, setAiSaving] = useState(false)
  const [aiTesting, setAiTesting] = useState(false)
  const [aiMsg, setAiMsg] = useState<{ ok: boolean; text: string } | null>(null)

  // ── 初始化加载 ──
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  useEffect(() => {
    ;(async () => {
      try {
        const [push, sched, ai, providers] = await Promise.all([
          api.getPushConfig(),
          api.getSchedulerConfig(),
          api.getAiConfig(),
          api.getAiProviders(),
        ])
        setPushProvider(push.provider || 'serverchan')
        setPushEnabled(push.enabled)
        setHasToken(push.hasToken)
        setDataSource(sched.dataSource || 'akshare')
        setIntervalSec(sched.intervalSeconds || 5)
        setSessionStart(sched.sessionStart || '09:30')
        setSessionEnd(sched.sessionEnd || '15:00')
        setAiProviders(providers || [])
        setAiProvider(ai.provider || 'zhipu')
        setAiBaseUrl(ai.baseUrl || '')
        setAiModel(ai.model || '')
        setAiEnabled(ai.enabled)
        setHasApiKey(ai.hasApiKey)
      } catch (e) {
        setLoadError((e as Error).message)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  // ── 保存推送配置 ──
  const onSavePush = async () => {
    setPushSaving(true)
    setPushMsg(null)
    try {
      const updated = await api.updatePushConfig({
        provider: pushProvider,
        token: pushToken,
        enabled: pushEnabled,
      })
      setHasToken(updated.hasToken)
      setPushToken('')
      setPushMsg({ ok: true, text: '推送配置已保存' })
    } catch (e) {
      setPushMsg({ ok: false, text: (e as Error).message })
    } finally {
      setPushSaving(false)
    }
  }

  // ── 测试推送 ──
  const onTestPush = async () => {
    if (!pushToken && !hasToken) {
      setPushMsg({ ok: false, text: '请先填写 Token' })
      return
    }
    setPushTesting(true)
    setPushMsg(null)
    try {
      const res: PushTestResult = await api.testPush(pushToken, pushProvider)
      setPushMsg({
        ok: res.success,
        text: res.success ? `测试成功：${res.message}` : `测试失败：${res.message}`,
      })
    } catch (e) {
      setPushMsg({ ok: false, text: (e as Error).message })
    } finally {
      setPushTesting(false)
    }
  }

  // ── 保存调度配置 ──
  const onSaveSched = async () => {
    if (interval < 3 || interval > 60) {
      setSchedMsg({ ok: false, text: '轮询间隔需在 3-60 秒之间' })
      return
    }
    setSchedSaving(true)
    setSchedMsg(null)
    try {
      await api.updateSchedulerConfig({
        dataSource,
        intervalSeconds: interval,
        sessionStart,
        sessionEnd,
      })
      setSchedMsg({ ok: true, text: '调度配置已保存' })
    } catch (e) {
      setSchedMsg({ ok: false, text: (e as Error).message })
    } finally {
      setSchedSaving(false)
    }
  }

  // ── AI Provider 切换：自动填充默认 baseUrl 与 model ──
  const onAiProviderChange = (value: string) => {
    setAiProvider(value)
    const p = aiProviders.find((x) => x.value === value)
    if (p) {
      setAiBaseUrl(p.baseUrl)
      setAiModel(p.model)
    }
  }

  // ── 保存 AI 配置 ──
  const onSaveAi = async () => {
    setAiSaving(true)
    setAiMsg(null)
    try {
      const updated: AiConfig = await api.updateAiConfig({
        provider: aiProvider,
        apiKey: aiApiKey,
        baseUrl: aiBaseUrl,
        model: aiModel,
        enabled: aiEnabled,
      })
      setHasApiKey(updated.hasApiKey)
      setAiApiKey('')
      setAiMsg({ ok: true, text: 'AI 配置已保存' })
    } catch (e) {
      setAiMsg({ ok: false, text: (e as Error).message })
    } finally {
      setAiSaving(false)
    }
  }

  // ── 测试 AI 连接 ──
  const onTestAi = async () => {
    if (!aiApiKey && !hasApiKey) {
      setAiMsg({ ok: false, text: '请先填写 API Key' })
      return
    }
    setAiTesting(true)
    setAiMsg(null)
    try {
      const res: AiTestResult = await api.testAiConnection(
        aiProvider,
        aiApiKey,
        aiBaseUrl,
        aiModel,
      )
      setAiMsg({
        ok: res.success,
        text: res.success ? `测试成功：${res.message}` : `测试失败：${res.message}`,
      })
    } catch (e) {
      setAiMsg({ ok: false, text: (e as Error).message })
    } finally {
      setAiTesting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-gray-500">
        加载中…
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center gap-2">
        <SettingsIcon size={20} className="text-accent" />
        <div>
          <h1 className="text-xl font-bold text-white">系统设置</h1>
          <p className="mt-1 text-xs text-gray-500">
            配置消息推送渠道与数据调度参数
          </p>
        </div>
      </div>

      {/* 加载错误 */}
      {loadError && (
        <div className="flex items-center justify-between rounded-lg border border-down/40 bg-down/10 px-3 py-2 text-xs text-down">
          <span>加载配置失败：{loadError}</span>
          <button onClick={() => setLoadError('')}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* ── 微信推送配置 ── */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-5">
        <div className="mb-4 flex items-center gap-2">
          <Bell size={18} className="text-accent" />
          <h2 className="text-sm font-semibold text-white">微信推送配置</h2>
        </div>

        <div className="space-y-4">
          {/* 推送渠道 */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">推送渠道</label>
            <select
              value={pushProvider}
              onChange={(e) => setPushProvider(e.target.value)}
              className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Token */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">
              Token
              {hasToken && !pushToken && (
                <span className="ml-2 text-[10px] text-up">已配置，留空则不修改</span>
              )}
            </label>
            <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
              <input
                type={showToken ? 'text' : 'password'}
                value={pushToken}
                onChange={(e) => setPushToken(e.target.value)}
                placeholder={hasToken ? '••••••••（已配置）' : '请输入推送 Token'}
                className="flex-1 bg-transparent text-sm text-white placeholder:text-gray-600 focus:outline-none"
              />
              <button
                onClick={() => setShowToken((v) => !v)}
                className="text-gray-500 hover:text-gray-300"
                title={showToken ? '隐藏' : '显示'}
              >
                {showToken ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* 启用开关 */}
          <div className="flex items-center justify-between">
            <label className="text-xs text-gray-400">启用推送</label>
            <button
              onClick={() => setPushEnabled((v) => !v)}
              className={`relative h-6 w-11 rounded-full transition-colors ${
                pushEnabled ? 'bg-accent' : 'bg-base-600'
              }`}
            >
              <span
                className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                  pushEnabled ? 'translate-x-5' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* 按钮组 */}
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={onSavePush}
              disabled={pushSaving}
              className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80 disabled:opacity-50"
            >
              <Save size={14} />
              {pushSaving ? '保存中…' : '保存'}
            </button>
            <button
              onClick={onTestPush}
              disabled={pushTesting}
              className="flex items-center gap-1.5 rounded-lg border border-base-500 bg-base-700 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-base-600 disabled:opacity-50"
            >
              <Send size={14} />
              {pushTesting ? '测试中…' : '测试推送'}
            </button>
          </div>

          {/* 测试结果 */}
          {pushMsg && (
            <div
              className={`flex items-start justify-between rounded-lg border px-3 py-2 text-xs ${
                pushMsg.ok
                  ? 'border-up/40 bg-up/10 text-up'
                  : 'border-down/40 bg-down/10 text-down'
              }`}
            >
              <div className="flex items-start gap-1.5">
                {pushMsg.ok ? <CheckCircle2 size={14} className="mt-0.5 shrink-0" /> : <AlertCircle size={14} className="mt-0.5 shrink-0" />}
                <span>{pushMsg.text}</span>
              </div>
              <button onClick={() => setPushMsg(null)}>
                <X size={14} />
              </button>
            </div>
          )}

          {/* 渠道说明 */}
          <div className="border-t border-base-500/50 pt-3">
            {pushProvider === 'serverchan' ? (
              <p className="text-xs leading-relaxed text-gray-500">
                Server酱是一个通过微信接收推送通知的服务。前往
                {' '}
                <a
                  href="https://sct.ftqq.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  sct.ftqq.com
                </a>
                {' '}
                注册并获取 SendKey，填入上方 Token 输入框。
              </p>
            ) : (
              <p className="text-xs leading-relaxed text-gray-500">
                PushPlus 是一款免费的消息推送平台，支持微信公众号、企业微信等多渠道。前往
                {' '}
                <a
                  href="https://www.pushplus.plus/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  www.pushplus.plus
                </a>
                {' '}
                注册并获取 Token，填入上方输入框。
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ── 调度配置 ── */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-5">
        <div className="mb-4 flex items-center gap-2">
          <Clock size={18} className="text-accent" />
          <h2 className="text-sm font-semibold text-white">调度配置</h2>
        </div>

        <div className="space-y-4">
          {/* 数据源 */}
          <div>
            <label className="mb-1.5 flex items-center gap-1 text-xs text-gray-400">
              <Database size={12} />
              数据源
            </label>
            <select
              value={dataSource}
              onChange={(e) => setDataSource(e.target.value)}
              className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none"
            >
              {DATA_SOURCES.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </div>

          {/* 轮询间隔 */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">
              轮询间隔（秒，范围 3-60）
            </label>
            <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
              <input
                type="number"
                min={3}
                max={60}
                value={interval}
                onChange={(e) => setIntervalSec(Number(e.target.value))}
                className="tnum flex-1 bg-transparent text-sm text-white focus:outline-none"
              />
              <span className="text-xs text-gray-500">秒</span>
            </div>
          </div>

          {/* 交易时段 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1.5 block text-xs text-gray-400">交易时段开始</label>
              <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
                <Clock size={14} className="text-gray-500" />
                <input
                  type="time"
                  value={sessionStart}
                  onChange={(e) => setSessionStart(e.target.value)}
                  className="tnum flex-1 bg-transparent text-sm text-white focus:outline-none"
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-xs text-gray-400">交易时段结束</label>
              <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
                <Clock size={14} className="text-gray-500" />
                <input
                  type="time"
                  value={sessionEnd}
                  onChange={(e) => setSessionEnd(e.target.value)}
                  className="tnum flex-1 bg-transparent text-sm text-white focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* 保存按钮 */}
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={onSaveSched}
              disabled={schedSaving}
              className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80 disabled:opacity-50"
            >
              <Save size={14} />
              {schedSaving ? '保存中…' : '保存'}
            </button>
          </div>

          {/* 保存结果 */}
          {schedMsg && (
            <div
              className={`flex items-start justify-between rounded-lg border px-3 py-2 text-xs ${
                schedMsg.ok
                  ? 'border-up/40 bg-up/10 text-up'
                  : 'border-down/40 bg-down/10 text-down'
              }`}
            >
              <div className="flex items-start gap-1.5">
                {schedMsg.ok ? <CheckCircle2 size={14} className="mt-0.5 shrink-0" /> : <AlertCircle size={14} className="mt-0.5 shrink-0" />}
                <span>{schedMsg.text}</span>
              </div>
              <button onClick={() => setSchedMsg(null)}>
                <X size={14} />
              </button>
            </div>
          )}

          {/* 提示 */}
          <div className="border-t border-base-500/50 pt-3">
            <p className="flex items-center gap-1 text-xs leading-relaxed text-gray-500">
              <AlertCircle size={12} className="shrink-0" />
              修改调度参数后需重启服务生效
            </p>
          </div>
        </div>
      </div>

      {/* ── AI 模型配置 ── */}
      <div className="rounded-xl border border-base-500 bg-base-800 p-5">
        <div className="mb-4 flex items-center gap-2">
          <Sparkles size={18} className="text-accent" />
          <h2 className="text-sm font-semibold text-white">AI 模型配置</h2>
        </div>

        <div className="space-y-4">
          {/* Provider */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">Provider</label>
            <select
              value={aiProvider}
              onChange={(e) => onAiProviderChange(e.target.value)}
              className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white focus:border-accent focus:outline-none"
            >
              {aiProviders.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Base URL */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">Base URL</label>
            <input
              type="text"
              value={aiBaseUrl}
              onChange={(e) => setAiBaseUrl(e.target.value)}
              placeholder="https://open.bigmodel.cn/api/paas/v4"
              className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none"
            />
          </div>

          {/* Model */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">Model</label>
            <input
              type="text"
              value={aiModel}
              onChange={(e) => setAiModel(e.target.value)}
              placeholder="glm-4-flash"
              className="w-full rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-accent focus:outline-none"
            />
          </div>

          {/* API Key */}
          <div>
            <label className="mb-1.5 block text-xs text-gray-400">
              API Key
              {hasApiKey && !aiApiKey && (
                <span className="ml-2 text-[10px] text-up">已配置，留空则不修改</span>
              )}
            </label>
            <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={aiApiKey}
                onChange={(e) => setAiApiKey(e.target.value)}
                placeholder={hasApiKey ? '••••••••（已配置）' : '请输入 API Key'}
                className="flex-1 bg-transparent text-sm text-white placeholder:text-gray-600 focus:outline-none"
              />
              <button
                onClick={() => setShowApiKey((v) => !v)}
                className="text-gray-500 hover:text-gray-300"
                title={showApiKey ? '隐藏' : '显示'}
              >
                {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* 启用开关 */}
          <div className="flex items-center justify-between">
            <label className="text-xs text-gray-400">启用 AI 分析</label>
            <button
              onClick={() => setAiEnabled((v) => !v)}
              className={`relative h-6 w-11 rounded-full transition-colors ${
                aiEnabled ? 'bg-accent' : 'bg-base-600'
              }`}
            >
              <span
                className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                  aiEnabled ? 'translate-x-5' : 'translate-x-0.5'
                }`}
              />
            </button>
          </div>

          {/* 按钮组 */}
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={onSaveAi}
              disabled={aiSaving}
              className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-base-900 transition-colors hover:bg-accent/80 disabled:opacity-50"
            >
              <Save size={14} />
              {aiSaving ? '保存中…' : '保存'}
            </button>
            <button
              onClick={onTestAi}
              disabled={aiTesting}
              className="flex items-center gap-1.5 rounded-lg border border-base-500 bg-base-700 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-base-600 disabled:opacity-50"
            >
              <Sparkles size={14} />
              {aiTesting ? '测试中…' : '测试连接'}
            </button>
          </div>

          {/* 测试 / 保存结果 */}
          {aiMsg && (
            <div
              className={`flex items-start justify-between rounded-lg border px-3 py-2 text-xs ${
                aiMsg.ok
                  ? 'border-up/40 bg-up/10 text-up'
                  : 'border-down/40 bg-down/10 text-down'
              }`}
            >
              <div className="flex items-start gap-1.5">
                {aiMsg.ok ? <CheckCircle2 size={14} className="mt-0.5 shrink-0" /> : <AlertCircle size={14} className="mt-0.5 shrink-0" />}
                <span>{aiMsg.text}</span>
              </div>
              <button onClick={() => setAiMsg(null)}>
                <X size={14} />
              </button>
            </div>
          )}

          {/* Provider 链接说明 */}
          <div className="border-t border-base-500/50 pt-3">
            {aiProvider === 'zhipu' && (
              <p className="text-xs leading-relaxed text-gray-500">
                智谱 GLM 是由智谱 AI 提供的大模型服务。前往
                {' '}
                <a
                  href="https://open.bigmodel.cn/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  open.bigmodel.cn
                </a>
                {' '}
                注册并创建 API Key，填入上方输入框。
              </p>
            )}
            {aiProvider === 'qwen' && (
              <p className="text-xs leading-relaxed text-gray-500">
                通义千问由阿里云提供。前往
                {' '}
                <a
                  href="https://dashscope.console.aliyun.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  dashscope.console.aliyun.com
                </a>
                {' '}
                创建 API Key。
              </p>
            )}
            {aiProvider === 'openai' && (
              <p className="text-xs leading-relaxed text-gray-500">
                OpenAI 提供 GPT 系列模型。前往
                {' '}
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  platform.openai.com
                </a>
                {' '}
                创建 API Key。
              </p>
            )}
            {aiProvider === 'deepseek' && (
              <p className="text-xs leading-relaxed text-gray-500">
                DeepSeek 提供高性价比的大模型服务。前往
                {' '}
                <a
                  href="https://platform.deepseek.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-accent hover:underline"
                >
                  platform.deepseek.com
                </a>
                {' '}
                创建 API Key。
              </p>
            )}
            {aiProvider === 'custom' && (
              <p className="flex items-center gap-1 text-xs leading-relaxed text-gray-500">
                <AlertCircle size={12} className="shrink-0" />
                自定义 Provider，请手动填写兼容 OpenAI 协议的 Base URL、Model 与 API Key。
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
