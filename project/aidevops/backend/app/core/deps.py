import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.services import user_service

# tokenUrl 仅用于 Swagger 文档展示
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=401,
        detail="登录已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise credentials_exc

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exc

    user = user_service.get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_permission(perm: str):
    """依赖工厂：校验当前用户是否拥有指定权限；超管直接放行。"""

    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.is_superuser:
            return user
        if perm not in user.permissions:
            raise HTTPException(status_code=403, detail="无操作权限")
        return user

    return _dep
