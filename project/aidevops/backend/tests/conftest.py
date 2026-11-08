"""RBAC 单元测试公共夹具。

每个测试用例使用独立的内存 SQLite（StaticPool 保证同一连接），
并覆盖 FastAPI 的 get_db 依赖，测试之间数据完全隔离、不触碰开发库。
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace

# 必须在导入 app.* 之前设置：强制内存数据库，避免生成/访问 aidevops.db
os.environ["DATABASE_URL"] = "sqlite://"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401  导入以注册全部 ORM 模型到 metadata
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services import role_service, user_service  # noqa: E402


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def SessionTesting(db_engine):
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False)


@pytest.fixture
def db(SessionTesting):
    """直接操作数据库的会话，用于构造数据与断言。"""
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(SessionTesting):
    """覆盖 get_db 依赖；不进入 with 上下文，避免触发 main.seed_on_startup。"""

    def _override_get_db():
        session = SessionTesting()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    # 不使用 with：跳过 lifespan startup（种子逻辑由测试夹具自行控制）
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def roles(db):
    """写入三个默认角色。"""
    role_service.seed_default_roles(db)
    return SimpleNamespace(
        admin=role_service.get_role_by_code(db, "admin"),
        developer=role_service.get_role_by_code(db, "developer"),
        viewer=role_service.get_role_by_code(db, "viewer"),
    )


@pytest.fixture
def users(db, roles):
    """常用测试账号：超管 admin、只读 viewer1、无角色 norole1。"""
    admin = user_service.create_user(
        db,
        UserCreate(
            username="admin",
            password="Secret123",
            is_superuser=True,
            role_id=roles.admin.id,
        ),
    )
    viewer = user_service.create_user(
        db,
        UserCreate(username="viewer1", password="Secret123", role_id=roles.viewer.id),
    )
    no_role = user_service.create_user(
        db,
        UserCreate(username="norole1", password="Secret123"),
    )
    return SimpleNamespace(admin=admin, viewer=viewer, no_role=no_role)


@pytest.fixture
def auth():
    """生成指定用户的认证头。"""

    def _headers(user) -> dict[str, str]:
        token = create_access_token(str(user.id))
        return {"Authorization": f"Bearer {token}"}

    return _headers
