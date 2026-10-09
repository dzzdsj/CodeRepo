// 占位页：规则/历史/设置（P2/P3 实现）
import { Bell, History, Settings } from 'lucide-react'

interface Props {
  title: string
  desc: string
  icon: 'rules' | 'history' | 'settings'
}

const ICONS = {
  rules: Bell,
  history: History,
  settings: Settings,
}

export default function Placeholder({ title, desc, icon }: Props) {
  const Icon = ICONS[icon]
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">{title}</h1>
        <p className="mt-1 text-xs text-gray-500">{desc}</p>
      </div>
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-base-500 bg-base-800 py-20 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-base-700 text-accent">
          <Icon size={26} />
        </div>
        <p className="mt-4 text-sm text-gray-400">该功能将在后续阶段实现</p>
        <p className="mt-1 text-xs text-gray-600">P2：异常检测 + 智能通知 · P3：AI 分析</p>
      </div>
    </div>
  )
}
