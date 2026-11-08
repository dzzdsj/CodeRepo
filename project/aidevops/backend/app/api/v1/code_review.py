from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.llm.exceptions import LLMError
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.schemas.code_review import (
    CodeReviewCreate,
    CodeReviewDetail,
    CodeReviewOut,
)
from app.services import code_review_service

router = APIRouter(prefix="/code-reviews", tags=["code-review"])


@router.get("")
def list_reviews(
    db: Session = Depends(get_db),
    _=Depends(require_permission("dev:read")),
):
    items = code_review_service.list_reviews(db)
    data = [CodeReviewOut.model_validate(r).model_dump(mode="json") for r in items]
    return success(data)


@router.post("")
def create_review(
    payload: CodeReviewCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("dev:write")),
):
    review = code_review_service.create_review(db, **payload.model_dump())
    return success(CodeReviewOut.model_validate(review).model_dump(mode="json"), msg="创建成功")


@router.get("/{review_id}")
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("dev:read")),
):
    review = code_review_service.get_review_by_id(db, review_id)
    if review is None:
        raise BizException("审查记录不存在", http_status=404)
    return success(CodeReviewDetail.model_validate(review).model_dump(mode="json"))


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("dev:write")),
):
    review = code_review_service.get_review_by_id(db, review_id)
    if review is None:
        raise BizException("审查记录不存在", http_status=404)
    code_review_service.delete_review(db, review)
    return success(None, msg="删除成功")


@router.post("/{review_id}/review")
def run_review(
    review_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("dev:write")),
):
    review = code_review_service.get_review_by_id(db, review_id)
    if review is None:
        raise BizException("审查记录不存在", http_status=404)
    try:
        updated = code_review_service.run_review(db, review)
    except LLMError as exc:
        return success(
            {"status": "failed", "message": str(exc)},
            msg="AI审查失败",
        )
    return success(
        CodeReviewOut.model_validate(updated).model_dump(mode="json"),
        msg="AI审查完成",
    )
