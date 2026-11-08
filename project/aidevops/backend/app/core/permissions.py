"""权限清单：所有可分配权限的唯一来源。
权限采用 '模块:动作' 命名，例如 user:read / role:write。
超级管理员（is_superuser=True）自动拥有全部权限，无需在此显式分配。
"""

PERMISSIONS: dict[str, str] = {
    "user:read": "用户管理 - 查看",
    "user:write": "用户管理 - 增删改",
    "role:read": "角色管理 - 查看",
    "role:write": "角色管理 - 增删改",
    "dev:read": "研发赋能 - 查看",
    "dev:write": "研发赋能 - 操作",
    "ops:read": "运维赋能 - 查看",
    "ops:write": "运维赋能 - 操作",
    "ai:read": "AI中台 - 查看",
    "ai:write": "AI中台 - 操作",
}

ALL_PERMISSIONS = list(PERMISSIONS.keys())

# 按模块分组，供角色管理页展示
PERMISSION_GROUPS: dict[str, list[str]] = {
    "用户管理": ["user:read", "user:write"],
    "角色管理": ["role:read", "role:write"],
    "研发赋能": ["dev:read", "dev:write"],
    "运维赋能": ["ops:read", "ops:write"],
    "AI中台": ["ai:read", "ai:write"],
}
