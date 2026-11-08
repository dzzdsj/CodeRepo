"""role_service 与默认角色种子的单元测试。"""
from app.core.permissions import ALL_PERMISSIONS
from app.services import role_service


def test_seed_default_roles_creates_three(db):
    role_service.seed_default_roles(db)
    codes = {r.code for r in role_service.list_roles(db)}
    assert codes == {"admin", "developer", "viewer"}


def test_seed_is_idempotent(db):
    role_service.seed_default_roles(db)
    role_service.seed_default_roles(db)  # 再次执行不应重复插入
    assert len(role_service.list_roles(db)) == 3


def test_admin_role_is_default_with_all_permissions(db, roles):
    assert roles.admin.is_default is True
    assert roles.admin.name == "超级管理员"
    assert roles.admin.permissions == ALL_PERMISSIONS
    # 其余默认角色不可标记为默认，避免被误删保护逻辑误伤
    assert roles.developer.is_default is False
    assert roles.viewer.is_default is False


def test_viewer_role_is_read_only(db, roles):
    perms = roles.viewer.permissions
    assert perms == ["user:read", "role:read", "dev:read", "ops:read", "ai:read"]
    assert all(p.endswith(":read") for p in perms)


def test_developer_role_permissions(db, roles):
    assert "dev:read" in roles.developer.permissions
    assert "dev:write" in roles.developer.permissions
    assert "user:write" not in roles.developer.permissions


def test_create_and_get_role(db):
    role = role_service.create_role(
        db,
        name="审计员",
        code="auditor",
        description="只读审计",
        is_default=False,
        permissions=["user:read", "role:read"],
    )
    assert role.id is not None
    assert role_service.get_role_by_code(db, "auditor") is role
    assert role_service.get_role_by_name(db, "审计员") is role
    assert role_service.get_role_by_id(db, role.id) is role


def test_update_role(db, roles):
    updated = role_service.update(
        db,
        roles.viewer,
        {"name": "只读访客", "permissions": ["user:read"]},
    )
    assert updated.name == "只读访客"
    assert updated.permissions == ["user:read"]
    # code 不在更新字段内，保持不变
    assert updated.code == "viewer"


def test_delete_role(db, roles):
    role_id = roles.viewer.id
    role_service.delete_role(db, roles.viewer)
    assert role_service.get_role_by_id(db, role_id) is None


def test_list_roles_ordered_by_id(db, roles):
    items = role_service.list_roles(db)
    ids = [r.id for r in items]
    assert ids == sorted(ids)
    assert len(items) == 3
