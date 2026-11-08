from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.auth import router as auth_router
from app.api.v1.code_review import router as code_review_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.llm_models import router as llm_models_router
from app.api.v1.prompt_templates import router as prompt_templates_router
from app.api.v1.roles import router as roles_router
from app.api.v1.users import router as users_router
from app.core.database import get_db

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(llm_models_router)
api_router.include_router(prompt_templates_router)
api_router.include_router(knowledge_router)
api_router.include_router(code_review_router)


@api_router.get("/health", tags=["system"])
async def health(db: Session = Depends(get_db)):
    """存活探针 + 数据库连通性探测。"""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
