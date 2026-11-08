from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permissions import ALL_PERMISSIONS
from app.models import Role


def get_role_by_id(db: Session, role_id: int) -> Role | None:
    return db.get(Role, role_id)


def get_role_by_code(db: Session, code: str) -> Role | None:
    return db.scalar(select(Role).where(Role.code == code))


def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name))


def list_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.id.asc())).all())


def create_role(db: Session, **kwargs) -> Role:
    role = Role(**kwargs)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, data: dict) -> Role:
    for key, value in data.items():
        if value is not None:
            setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()


def seed_default_roles(db: Session) -> None:
    """首次启动时创建默认角色，已存在则跳过。"""
    defaults = [
        {
            "name": "超级管理员",
            "code": "admin",
            "description": "拥有全部权限",
            "is_default": True,
            "permissions": ALL_PERMISSIONS,
        },
        {
            "name": "开发人员",
            "code": "developer",
            "description": "研发与查看基础数据",
            "is_default": False,
            "permissions": ["dev:read", "dev:write", "user:read", "ops:read", "ai:read"],
        },
        {
            "name": "只读用户",
            "code": "viewer",
            "description": "仅可查看各模块",
            "is_default": False,
            "permissions": [
                "user:read",
                "role:read",
                "dev:read",
                "ops:read",
                "ai:read",
            ],
        },
    ]
    for item in defaults:
        if get_role_by_code(db, item["code"]) is None:
            create_role(db, **item)
