import type { Component } from 'vue'
import {
  HomeFilled,
  Cpu,
  Monitor,
  MagicStick,
  Setting,
  View,
  Document,
  Bell,
  Files,
  Connection,
  Collection,
  ChatDotRound,
  User,
  UserFilled
} from '@element-plus/icons-vue'

/**
 * 侧边栏菜单配置（单一数据源）
 * permission：访问该菜单所需的权限码；超管自动放行。
 */
export interface MenuItem {
  path: string
  title: string
  icon: Component
  permission?: string
  children?: MenuItem[]
}

export const menus: MenuItem[] = [
  { path: '/', title: '首页', icon: HomeFilled },
  {
    path: '/dev',
    title: '研发赋能',
    icon: Cpu,
    children: [
      { path: '/dev/code-review', title: 'AI代码审查', icon: View, permission: 'dev:read' },
      { path: '/dev/test-gen', title: '智能测试生成', icon: Document, permission: 'dev:read' }
    ]
  },
  {
    path: '/ops',
    title: '运维赋能',
    icon: Monitor,
    children: [
      { path: '/ops/alert', title: '智能监控告警', icon: Bell, permission: 'ops:read' },
      { path: '/ops/log', title: '日志智能分析', icon: Files, permission: 'ops:read' }
    ]
  },
  {
    path: '/ai',
    title: 'AI中台',
    icon: MagicStick,
    children: [
      { path: '/ai/model', title: '大模型管理', icon: Connection, permission: 'ai:read' },
      { path: '/ai/prompt', title: 'Prompt模板', icon: ChatDotRound, permission: 'ai:read' },
      { path: '/ai/knowledge', title: '知识库', icon: Collection, permission: 'ai:read' }
    ]
  },
  {
    path: '/system',
    title: '系统管理',
    icon: Setting,
    children: [
      { path: '/system/user', title: '用户管理', icon: User, permission: 'user:read' },
      { path: '/system/role', title: '角色管理', icon: UserFilled, permission: 'role:read' }
    ]
  }
]
