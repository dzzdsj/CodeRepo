/** 与后端 app/core/permissions.py 保持一致的权限清单 */
export const PERMISSIONS: Record<string, string> = {
  'user:read': '用户管理 - 查看',
  'user:write': '用户管理 - 增删改',
  'role:read': '角色管理 - 查看',
  'role:write': '角色管理 - 增删改',
  'dev:read': '研发赋能 - 查看',
  'dev:write': '研发赋能 - 操作',
  'ops:read': '运维赋能 - 查看',
  'ops:write': '运维赋能 - 操作',
  'ai:read': 'AI中台 - 查看',
  'ai:write': 'AI中台 - 操作'
}

export const PERMISSION_GROUPS: Record<string, string[]> = {
  用户管理: ['user:read', 'user:write'],
  角色管理: ['role:read', 'role:write'],
  研发赋能: ['dev:read', 'dev:write'],
  运维赋能: ['ops:read', 'ops:write'],
  AI中台: ['ai:read', 'ai:write']
}
