from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.models import Role, User
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("")
def list_roles(db: Session = Depends(get_db), _=Depends(require_permission("role:read"))):
    items = role_service.list_roles(db)
    data = [RoleOut.model_validate(r).model_dump(mode="json") for r in items]
    return success(data)


@router.post("")
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("role:write")),
):
    if role_service.get_role_by_code(db, payload.code):
        raise BizException("角色编码已存在")
    if role_service.get_role_by_name(db, payload.name):
        raise BizException("角色名称已存在")
    role = role_service.create_role(db, **payload.model_dump())
    return success(RoleOut.model_validate(role).model_dump(mode="json"), msg="创建成功")


@router.put("/{role_id}")
def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("role:write")),
):
    role = role_service.get_role_by_id(db, role_id)
    if role is None:
        raise BizException("角色不存在", http_status=404)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != role.name:
        if role_service.get_role_by_name(db, data["name"]):
            raise BizException("角色名称已存在")
    updated = role_service.update_role(db, role, data)
    return success(RoleOut.model_validate(updated).model_dump(mode="json"), msg="更新成功")


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("role:write")),
):
    role = role_service.get_role_by_id(db, role_id)
    if role is None:
        raise BizException("角色不存在", http_status=404)
    if role.is_default:
        raise BizException("默认角色不可删除")
    bound = db.scalar(select(User.id).where(User.role_id == role_id).limit(1))
    if bound is not None:
        raise BizException("该角色下仍有用户，无法删除")
    role_service.delete_role(db, role)
    return success(None, msg="删除成功")
