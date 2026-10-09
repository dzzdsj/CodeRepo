// 侧边导航栏
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Star,
  Bell,
  History,
  Settings,
  TrendingUp,
  Layers,
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/', label: '仪表盘', icon: LayoutDashboard, end: true },
  { to: '/watchlist', label: '自选股', icon: Star, end: false },
  { to: '/sectors', label: '板块资金', icon: Layers, end: false },
  { to: '/rules', label: '告警规则', icon: Bell, end: false },
  { to: '/history', label: '告警历史', icon: History, end: false },
  { to: '/settings', label: '设置', icon: Settings, end: false },
]

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-16 flex-col border-r border-base-500 bg-base-800 lg:flex lg:w-56">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-base-500 px-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded bg-accent text-base-900">
          <TrendingUp size={18} strokeWidth={2.5} />
        </div>
        <span className="hidden font-bold tracking-tight text-base-900 lg:text-white lg:block">
          股票助手
        </span>
      </div>

      {/* 导航项 */}
      <nav className="flex-1 space-y-1 p-2">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                'group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-base-600 text-accent'
                  : 'text-gray-400 hover:bg-base-700 hover:text-white',
              ].join(' ')
            }
          >
            <item.icon size={20} strokeWidth={2} />
            <span className="hidden lg:inline">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* 底部版本 */}
      <div className="hidden border-t border-base-500 p-3 text-xs text-gray-500 lg:block">
        v0.6.0 · P6
      </div>
    </aside>
  )
}
