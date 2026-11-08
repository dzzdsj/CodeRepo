"""模型聚合导出，保证 Alembic / 其他模块通过单一入口导入后 metadata 完整。"""
from app.core.database import Base
from app.models.code_review import CodeReview
from app.models.knowledge_doc import KnowledgeChunk, KnowledgeDoc
from app.models.llm_model import LlmModel
from app.models.prompt_template import PromptTemplate
from app.models.role import Role
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "Role",
    "LlmModel",
    "PromptTemplate",
    "KnowledgeDoc",
    "KnowledgeChunk",
    "CodeReview",
]
