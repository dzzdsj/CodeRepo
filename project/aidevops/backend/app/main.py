from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.models import User
from app.services import role_service


def seed_on_startup() -> None:
    db = SessionLocal()
    try:
        role_service.seed_default_roles(db)
        # 将尚未分配角色的超级管理员绑定到 admin 角色
        admin_role = role_service.get_role_by_code(db, "admin")
        if admin_role:
            superusers = db.scalars(
                select(User).where(User.is_superuser.is_(True), User.role_id.is_(None))
            ).all()
            for u in superusers:
                u.role_id = admin_role.id
            if superusers:
                db.commit()
    finally:
        db.close()


def create_app() -> FastAPI:
    setup_logging(settings.debug)

    app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    def _startup() -> None:
        seed_on_startup()

    return app


app = create_app()
