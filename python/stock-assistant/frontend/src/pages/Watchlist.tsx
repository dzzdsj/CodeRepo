// 自选股管理：搜索添加 + 分组折叠列表 + 编辑分组/备注 + 删除 + 资金流向
import { useEffect, useState, useRef, useMemo, Fragment } from 'react'
import { useWatchlistStore } from '@/stores/watchlist'
import { useQuoteStore } from '@/stores/quotes'
import { ColorText } from '@/components/ColorText'
import FundFlowCard from '@/components/FundFlowCard'
import {
  Search,
  Plus,
  Trash2,
  X,
  ChevronRight,
  Folder,
  FolderOpen,
  Pencil,
  Activity,
  CheckSquare,
  Square,
} from 'lucide-react'
import type { StockSearchResult, WatchlistItem } from '@/types'

export default function Watchlist() {
  const items = useWatchlistStore((s) => s.items)
  const fetch = useWatchlistStore((s) => s.fetch)
  const remove = useWatchlistStore((s) => s.remove)
  const search = useWatchlistStore((s) => s.search)
  const add = useWatchlistStore((s) => s.add)
  const update = useWatchlistStore((s) => s.update)
  const quotes = useQuoteStore((s) => s.quotes)

  const [keyword, setKeyword] = useState('')
  const [results, setResults] = useState<StockSearchResult[]>([])
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')
  const timer = useRef<number | null>(null)

  // 折叠状态：记录哪些分组被折叠
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set())

  // 编辑分组名
  const [editingGroup, setEditingGroup] = useState<string | null>(null)
  const [editGroupName, setEditGroupName] = useState('')

  // 资金流向展开状态
  const [expandedFundFlow, setExpandedFundFlow] = useState<string | null>(null)

  // 批量选择
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set())
  const [batchDeleting, setBatchDeleting] = useState(false)

  const allInGroupSelected = (groupItems: WatchlistItem[]) =>
    groupItems.length > 0 && groupItems.every((it) => selectedCodes.has(it.code))

  const toggleSelectCode = (code: string) => {
    setSelectedCodes((prev) => {
      const next = new Set(prev)
      if (next.has(code)) next.delete(code)
      else next.add(code)
      return next
    })
  }

  const toggleSelectGroup = (groupItems: WatchlistItem[]) => {
    setSelectedCodes((prev) => {
      const next = new Set(prev)
      const allSelected = groupItems.every((it) => next.has(it.code))
      if (allSelected) {
        for (const it of groupItems) next.delete(it.code)
      } else {
        for (const it of groupItems) next.add(it.code)
      }
      return next
    })
  }

  const toggleSelectAll = () => {
    if (selectedCodes.size === items.length) {
      setSelectedCodes(new Set())
    } else {
      setSelectedCodes(new Set(items.map((it) => it.code)))
    }
  }

  const onBatchDelete = async () => {
    if (selectedCodes.size === 0) return
    if (!confirm(`确定删除选中的 ${selectedCodes.size} 只自选股？`)) return
    setBatchDeleting(true)
    try {
      await Promise.all(
        Array.from(selectedCodes).map((code) => remove(code)),
      )
      setSelectedCodes(new Set())
      setError('')
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBatchDeleting(false)
    }
  }

  useEffect(() => {
    fetch()
  }, [fetch])

  // 按分组归类
  const grouped = useMemo(() => {
    const map = new Map<string, WatchlistItem[]>()
    for (const it of items) {
      const g = it.groupName || '默认'
      if (!map.has(g)) map.set(g, [])
      map.get(g)!.push(it)
    }
    // 排序：每组内按 sortOrder，分组按字母序
    const sorted = Array.from(map.entries()).sort((a, b) =>
      a[0].localeCompare(b[0], 'zh-CN'),
    )
    for (const [, list] of sorted) {
      list.sort((a, b) => a.sortOrder - b.sortOrder)
    }
    return sorted
  }, [items])

  const onSearch = (q: string) => {
    setKeyword(q)
    setError('')
    if (timer.current) clearTimeout(timer.current)
    if (!q.trim()) {
      setResults([])
      return
    }
    timer.current = window.setTimeout(async () => {
      setSearching(true)
      try {
        setResults(await search(q))
      } catch (e) {
        setError((e as Error).message)
      } finally {
        setSearching(false)
      }
    }, 350)
  }

  const onAdd = async (code: string, _name: string) => {
    try {
      await add(code)
      setKeyword('')
      setResults([])
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const onDelete = async (code: string) => {
    try {
      await remove(code)
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const toggleGroup = (group: string) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(group)) next.delete(group)
      else next.add(group)
      return next
    })
  }

  const onStartEditGroup = (group: string) => {
    setEditGroupName(group)
    setEditingGroup(group)
  }

  const onSaveEditGroup = async (oldName: string) => {
    const newName = editGroupName.trim()
    if (!newName || newName === oldName) {
      setEditingGroup(null)
      return
    }
    // 批量更新该组下所有股票的分组名
    try {
      const groupItems = items.filter((i) => i.groupName === oldName)
      await Promise.all(
        groupItems.map((it) => update(it.code, { groupName: newName })),
      )
    } catch (e) {
      setError((e as Error).message)
    }
    setEditingGroup(null)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">自选股</h1>
        <p className="mt-1 text-xs text-gray-500">
          添加关注股票，调度器将自动纳入实时监控
        </p>
      </div>

      {error && (
        <div className="flex items-center justify-between rounded-lg border border-up/40 bg-up/10 px-3 py-2 text-xs text-up">
          <span>{error}</span>
          <button onClick={() => setError('')}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* 搜索添加 */}
      <div className="relative">
        <div className="flex items-center gap-2 rounded-lg border border-base-500 bg-base-700 px-3 py-2.5 focus-within:border-accent">
          <Search size={18} className="text-gray-500" />
          <input
            value={keyword}
            onChange={(e) => onSearch(e.target.value)}
            placeholder="输入股票代码或名称搜索，如 600519 / 茅台"
            className="flex-1 bg-transparent text-sm text-white placeholder:text-gray-600 focus:outline-none"
          />
          {searching && <span className="text-xs text-gray-500">搜索中…</span>}
        </div>

        {results.length > 0 && (
          <div className="absolute z-20 mt-1 max-h-80 w-full overflow-auto rounded-lg border border-base-500 bg-base-800 py-1 shadow-card">
            {results.map((r) => (
              <button
                key={r.code}
                onClick={() => onAdd(r.code, r.name)}
                className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-base-600"
              >
                <div className="flex items-center gap-3">
                  <span className="tnum text-xs text-gray-400">{r.code}</span>
                  <span className="text-sm text-white">{r.name}</span>
                  <span className="rounded bg-base-600 px-1 text-[10px] text-gray-400">
                    {r.market}
                  </span>
                </div>
                <Plus size={16} className="text-accent" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 批量操作工具栏 */}
      {items.length > 0 && (
        <div className="flex items-center justify-between rounded-lg border border-base-500 bg-base-700 px-3 py-2">
          <button
            onClick={toggleSelectAll}
            className="flex items-center gap-2 text-xs text-gray-400 transition-colors hover:text-white"
          >
            {selectedCodes.size === items.length && items.length > 0 ? (
              <CheckSquare size={15} className="text-accent" />
            ) : (
              <Square size={15} />
            )}
            全选
          </button>
          {selectedCodes.size > 0 ? (
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400">
                已选 <span className="text-accent">{selectedCodes.size}</span> 只
              </span>
              <button
                onClick={onBatchDelete}
                disabled={batchDeleting}
                className="flex items-center gap-1 rounded bg-down px-2.5 py-1 text-xs font-medium text-white transition-colors hover:bg-down/80 disabled:opacity-50"
              >
                <Trash2 size={13} />
                {batchDeleting ? '删除中…' : '批量删除'}
              </button>
              <button
                onClick={() => setSelectedCodes(new Set())}
                className="text-xs text-gray-500 hover:text-white"
              >
                取消选择
              </button>
            </div>
          ) : (
            <span className="text-xs text-gray-600">勾选股票可批量操作</span>
          )}
        </div>
      )}

      {/* 分组折叠列表 */}
      {items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-base-500 bg-base-800 py-12 text-center text-xs text-gray-500">
          暂无自选股，请在上方搜索添加
        </div>
      ) : (
        <div className="space-y-3">
          {grouped.map(([group, groupItems]) => {
            const collapsed = collapsedGroups.has(group)
            const isEditing = editingGroup === group
            return (
              <div
                key={group}
                className="overflow-hidden rounded-xl border border-base-500 bg-base-800"
              >
                {/* 分组头 */}
                <div className="flex items-center justify-between border-b border-base-500 bg-base-700 px-3 py-2.5">
                  <button
                    onClick={() => toggleGroup(group)}
                    className="flex items-center gap-2 text-sm font-medium text-white transition-colors hover:text-accent"
                  >
                    {collapsed ? (
                      <ChevronRight size={16} className="text-gray-500" />
                    ) : (
                      <ChevronRight
                        size={16}
                        className="rotate-90 text-gray-500"
                      />
                    )}
                    {collapsed ? (
                      <Folder size={16} className="text-accent/60" />
                    ) : (
                      <FolderOpen size={16} className="text-accent" />
                    )}
                    {isEditing ? (
                      <input
                        autoFocus
                        value={editGroupName}
                        onChange={(e) => setEditGroupName(e.target.value)}
                        onBlur={() => onSaveEditGroup(group)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') onSaveEditGroup(group)
                          if (e.key === 'Escape') setEditingGroup(null)
                        }}
                        className="w-32 rounded border border-accent bg-base-900 px-2 py-0.5 text-sm text-white focus:outline-none"
                      />
                    ) : (
                      <span>{group}</span>
                    )}
                    <span className="rounded bg-base-600 px-1.5 py-0.5 text-[10px] text-gray-400">
                      {groupItems.length}
                    </span>
                  </button>
                  {!isEditing && (
                    <button
                      onClick={() => onStartEditGroup(group)}
                      className="rounded p-1 text-gray-500 transition-colors hover:bg-base-600 hover:text-white"
                      title="编辑分组名"
                    >
                      <Pencil size={13} />
                    </button>
                  )}
                </div>

                {/* 分组内股票列表 */}
                {!collapsed && (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-base-500 text-xs text-gray-500">
                        <th className="px-3 py-2 text-center font-medium">
                          <button
                            onClick={() => toggleSelectGroup(groupItems)}
                            className={
                              allInGroupSelected(groupItems)
                                ? 'text-accent'
                                : 'text-gray-500 hover:text-white'
                            }
                          >
                            {allInGroupSelected(groupItems) ? (
                              <CheckSquare size={14} />
                            ) : (
                              <Square size={14} />
                            )}
                          </button>
                        </th>
                        <th className="px-4 py-2 text-left font-medium">代码</th>
                        <th className="px-4 py-2 text-left font-medium">名称</th>
                        <th className="px-4 py-2 text-right font-medium">最新价</th>
                        <th className="px-4 py-2 text-right font-medium">涨跌幅</th>
                        <th className="px-4 py-2 text-right font-medium">成交量</th>
                        <th className="px-4 py-2 text-center font-medium">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      {groupItems.map((it) => {
                        const q = quotes[it.code]
                        const isFundFlowExpanded = expandedFundFlow === it.code
                        return (
                          <Fragment key={it.id}>
                            <tr
                              className="border-b border-base-500/30 last:border-0 hover:bg-base-700"
                            >
                              <td className="px-3 py-2.5 text-center">
                                <button
                                  onClick={() => toggleSelectCode(it.code)}
                                  className={
                                    selectedCodes.has(it.code)
                                      ? 'text-accent'
                                      : 'text-gray-600 hover:text-white'
                                  }
                                >
                                  {selectedCodes.has(it.code) ? (
                                    <CheckSquare size={14} />
                                  ) : (
                                    <Square size={14} />
                                  )}
                                </button>
                              </td>
                              <td className="tnum px-4 py-2.5 text-xs text-gray-400">
                                {it.code}
                              </td>
                              <td className="px-4 py-2.5 text-white">{it.name}</td>
                              <td className="tnum px-4 py-2.5 text-right text-white">
                                {q ? q.price.toFixed(2) : '--'}
                              </td>
                              <td className="tnum px-4 py-2.5 text-right">
                                {q ? (
                                  <ColorText value={q.changePct} suffix="%" />
                                ) : (
                                  <span className="text-gray-600">--</span>
                                )}
                              </td>
                              <td className="tnum px-4 py-2.5 text-right text-xs text-gray-400">
                                {q ? fmtVol(q.volume) : '--'}
                              </td>
                              <td className="px-4 py-2.5 text-center">
                                <div className="flex items-center justify-center gap-1">
                                  <button
                                    onClick={() =>
                                      setExpandedFundFlow(
                                        isFundFlowExpanded ? null : it.code,
                                      )
                                    }
                                    className={`rounded p-1 transition-colors ${
                                      isFundFlowExpanded
                                        ? 'bg-accent/20 text-accent'
                                        : 'text-gray-500 hover:bg-base-600 hover:text-accent'
                                    }`}
                                    title="资金流向"
                                  >
                                    <Activity size={15} />
                                  </button>
                                  <button
                                    onClick={() => onDelete(it.code)}
                                    className="rounded p-1 text-gray-500 hover:bg-up/10 hover:text-up"
                                    title="删除"
                                  >
                                    <Trash2 size={15} />
                                  </button>
                                </div>
                              </td>
                            </tr>
                            {isFundFlowExpanded && (
                              <tr>
                                <td colSpan={7} className="bg-base-800 p-4">
                                  <FundFlowCard code={it.code} name={it.name} />
                                </td>
                              </tr>
                            )}
                          </Fragment>
                        )
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function fmtVol(n: number): string {
  if (!n) return '--'
  if (n >= 1e8) return (n / 1e8).toFixed(2) + '亿'
  if (n >= 1e4) return (n / 1e4).toFixed(2) + '万'
  return n.toFixed(0) + '手'
}
