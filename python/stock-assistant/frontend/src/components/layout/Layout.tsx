// 全局布局：侧边栏 + 顶部指数条 + 主内容区 + 移动端底部 Tab
import { Outlet, NavLink } from 'react-router-dom'
import Sidebar from './Sidebar'
import IndexBar from './IndexBar'
import { LayoutDashboard, Star, Bell, History, Settings, Layers } from 'lucide-react'

const MOBILE_NAV = [
  { to: '/', label: '行情', icon: LayoutDashboard, end: true },
  { to: '/watchlist', label: '自选', icon: Star, end: false },
  { to: '/sectors', label: '板块', icon: Layers, end: false },
  { to: '/rules', label: '规则', icon: Bell, end: false },
  { to: '/history', label: '告警', icon: History, end: false },
  { to: '/settings', label: '设置', icon: Settings, end: false },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-base-900">
      <Sidebar />
      <div className="lg:pl-56">
        <IndexBar />
        <main className="px-4 py-4 lg:px-6 lg:py-6">
          <Outlet />
        </main>
        {/* 移动端底部留白，避免被 Tab 栏遮挡 */}
        <div className="h-16 lg:hidden" />
      </div>

      {/* 移动端底部 Tab 导航 */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex items-center justify-around border-t border-base-500 bg-base-800 lg:hidden">
        {MOBILE_NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                'flex flex-col items-center gap-0.5 px-2 py-2 text-[10px] font-medium transition-colors',
                isActive
                  ? 'text-accent'
                  : 'text-gray-500 hover:text-white',
              ].join(' ')
            }
          >
            <item.icon size={20} strokeWidth={2} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
