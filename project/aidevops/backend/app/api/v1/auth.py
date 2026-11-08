from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BizException
from app.core.response import success
from app.core.security import create_access_token
from app.models import User
from app.schemas.user import LoginRequest, TokenOut, UserCreate, UserOut
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """注册新用户（初始阶段开放注册，后续可改为管理员邀请）。"""
    if user_service.get_user_by_username(db, payload.username):
        raise BizException("用户名已存在")
    user = user_service.create_user(db, payload)
    return success(UserOut.model_validate(user).model_dump(), msg="注册成功")


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, payload.username, payload.password)
    if user is None:
        raise BizException("用户名或密码错误", http_status=401)
    token = create_access_token(str(user.id))
    data = TokenOut(access_token=token, user=UserOut.model_validate(user))
    return success(data.model_dump(mode="json"))


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user).model_dump(mode="json"))
