from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.models import User
from app.schemas.user import UserCreate, UserListOut, UserOut, UserUpdate
from app.services import role_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("user:read")),
):
    items, total = user_service.list_users(db, keyword=keyword, page=page, page_size=page_size)
    data = UserListOut(
        total=total,
        list=[UserOut.model_validate(u).model_dump(mode="json") for u in items],
    ).model_dump()
    return success(data)


@router.post("")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("user:write")),
):
    if user_service.get_user_by_username(db, payload.username):
        raise BizException("用户名已存在")
    if payload.role_id is not None and role_service.get_role_by_id(db, payload.role_id) is None:
        raise BizException("指定的角色不存在")
    user = user_service.create_user(db, payload)
    return success(UserOut.model_validate(user).model_dump(mode="json"), msg="创建成功")


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("user:read")),
):
    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise BizException("用户不存在", http_status=404)
    return success(UserOut.model_validate(user).model_dump(mode="json"))


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_permission("user:write")),
):
    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise BizException("用户不存在", http_status=404)

    if payload.username and payload.username != user.username:
        if user_service.get_user_by_username(db, payload.username):
            raise BizException("用户名已存在")

    if payload.role_id is not None and role_service.get_role_by_id(db, payload.role_id) is None:
        raise BizException("指定的角色不存在")

    # 不允许禁用或降级自己的超级管理员权限（基础保护）
    if user.id == current.id:
        if payload.is_active is False:
            raise BizException("不能禁用当前登录账号")
        if payload.is_superuser is False:
            raise BizException("不能取消当前登录账号的超级管理员权限")

    updated = user_service.update_user(db, user, payload)
    return success(UserOut.model_validate(updated).model_dump(mode="json"), msg="更新成功")


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_permission("user:write")),
):
    if user_id == current.id:
        raise BizException("不能删除当前登录账号")

    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise BizException("用户不存在", http_status=404)

    user_service.delete_user(db, user)
    return success(None, msg="删除成功")
