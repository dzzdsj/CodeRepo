"""权限常量、User.permissions 属性与 require_permission 依赖的单元测试。"""
import pytest
from fastapi import HTTPException

from app.core.deps import require_permission
from app.core.permissions import ALL_PERMISSIONS, PERMISSION_GROUPS, PERMISSIONS
from app.schemas.user import UserCreate
from app.services import user_service


def test_permission_constants_consistency():
    # 5 个模块 × read/write，共 10 个权限码
    assert len(PERMISSIONS) == 10
    assert ALL_PERMISSIONS == list(PERMISSIONS.keys())
    for code in ALL_PERMISSIONS:
        assert ":" in code
        module, action = code.split(":")
        assert action in {"read", "write"}
        assert module in {"user", "role", "dev", "ops", "ai"}

    # 分组必须完整覆盖所有权限码，且无重复
    grouped = [p for perms in PERMISSION_GROUPS.values() for p in perms]
    assert sorted(grouped) == sorted(ALL_PERMISSIONS)


def test_superuser_has_all_permissions(db, roles, users):
    assert users.admin.is_superuser
    assert users.admin.permissions == ALL_PERMISSIONS
    # 即使角色只包含部分权限，超管也返回全部
    users.admin.role_id = roles.viewer.id
    db.commit()
    db.refresh(users.admin)
    assert users.admin.permissions == ALL_PERMISSIONS


def test_role_permissions_propagate(db, roles, users):
    assert users.viewer.is_superuser is False
    assert users.viewer.permissions == roles.viewer.permissions
    assert "user:read" in users.viewer.permissions
    assert "user:write" not in users.viewer.permissions


def test_user_without_role_has_no_permissions(users):
    assert users.no_role.role is None
    assert users.no_role.permissions == []


def test_user_with_custom_role_permissions(db, roles, users):
    """自定义角色只赋予 user:read，用户权限应与之精确一致。"""
    custom = roles.viewer
    custom.permissions = ["user:read"]
    db.commit()
    db.refresh(users.viewer)
    assert users.viewer.permissions == ["user:read"]


def test_require_permission_dependency(users):
    """直接验证 require_permission 工厂的判定逻辑。"""
    guard = require_permission("user:write")

    # 超管放行
    assert guard(user=users.admin) is users.admin

    # 无权限抛 403
    with pytest.raises(HTTPException) as exc_info:
        guard(user=users.viewer)
    assert exc_info.value.status_code == 403

    with pytest.raises(HTTPException) as exc_info:
        guard(user=users.no_role)
    assert exc_info.value.status_code == 403


def test_require_permission_granted_when_listed(db, roles, users):
    # viewer 拥有 user:read
    guard = require_permission("user:read")
    assert guard(user=users.viewer) is users.viewer


def test_permissions_refresh_after_role_change(db, roles):
    """用户从开发角色切换到只读角色后，权限应立即反映新角色。"""
    user = user_service.create_user(
        db,
        UserCreate(username="switcher", password="Secret123", role_id=roles.developer.id),
    )
    assert "dev:write" in user.permissions

    user.role_id = roles.viewer.id
    db.commit()
    db.refresh(user)
    assert "dev:write" not in user.permissions
    assert "dev:read" in user.permissions


def test_inactive_user_creation_defaults(db):
    """禁用用户仍可读取角色权限，是否放行由认证层处理。"""
    user = user_service.create_user(
        db,
        UserCreate(
            username="disabled1",
            password="Secret123",
            is_active=False,
            role_id=None,
        ),
    )
    assert user.permissions == []
