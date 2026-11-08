from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.llm.exceptions import LLMError
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.schemas.knowledge_doc import (
    KnowledgeAskRequest,
    KnowledgeAskResponse,
    KnowledgeDocCreate,
    KnowledgeDocDetail,
    KnowledgeDocOut,
    KnowledgeDocUpdate,
    KnowledgeSearchRequest,
    KnowledgeSearchResultItem,
)
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/docs")
def list_docs(db: Session = Depends(get_db), _=Depends(require_permission("ai:read"))):
    items = knowledge_service.list_docs(db)
    data = [KnowledgeDocOut.model_validate(d).model_dump(mode="json") for d in items]
    return success(data)


@router.post("/docs")
def create_doc(
    payload: KnowledgeDocCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    if knowledge_service.get_doc_by_title(db, payload.title):
        raise BizException("文档标题已存在")
    doc = knowledge_service.create_doc(db, **payload.model_dump())
    return success(KnowledgeDocOut.model_validate(doc).model_dump(mode="json"), msg="创建成功")


@router.get("/docs/{doc_id}")
def get_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    doc = knowledge_service.get_doc_by_id(db, doc_id)
    if doc is None:
        raise BizException("文档不存在", http_status=404)
    return success(KnowledgeDocDetail.model_validate(doc).model_dump(mode="json"))


@router.put("/docs/{doc_id}")
def update_doc(
    doc_id: int,
    payload: KnowledgeDocUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    doc = knowledge_service.get_doc_by_id(db, doc_id)
    if doc is None:
        raise BizException("文档不存在", http_status=404)
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] != doc.title:
        if knowledge_service.get_doc_by_title(db, data["title"]):
            raise BizException("文档标题已存在")
    updated = knowledge_service.update_doc(db, doc, data)
    return success(KnowledgeDocOut.model_validate(updated).model_dump(mode="json"), msg="更新成功")


@router.delete("/docs/{doc_id}")
def delete_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    doc = knowledge_service.get_doc_by_id(db, doc_id)
    if doc is None:
        raise BizException("文档不存在", http_status=404)
    knowledge_service.delete_doc(db, doc)
    return success(None, msg="删除成功")


@router.post("/docs/{doc_id}/embed")
def embed_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    doc = knowledge_service.get_doc_by_id(db, doc_id)
    if doc is None:
        raise BizException("文档不存在", http_status=404)
    try:
        updated = knowledge_service.embed_document(db, doc)
    except LLMError as exc:
        return success(
            {"status": "failed", "message": str(exc)},
            msg="向量化失败",
        )
    return success(
        KnowledgeDocOut.model_validate(updated).model_dump(mode="json"),
        msg="向量化成功",
    )


@router.post("/search")
def search(
    payload: KnowledgeSearchRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    try:
        results = knowledge_service.search_chunks(db, payload.query, payload.top_k)
    except LLMError as exc:
        raise BizException(str(exc))
    data = [KnowledgeSearchResultItem(**r).model_dump(mode="json") for r in results]
    return success(data)


@router.post("/ask")
def ask(
    payload: KnowledgeAskRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    try:
        result = knowledge_service.ask(db, payload.query, payload.top_k)
    except LLMError as exc:
        raise BizException(str(exc))
    resp = KnowledgeAskResponse(
        answer=result["answer"],
        sources=[KnowledgeSearchResultItem(**s) for s in result["sources"]],
    )
    return success(resp.model_dump(mode="json"))
