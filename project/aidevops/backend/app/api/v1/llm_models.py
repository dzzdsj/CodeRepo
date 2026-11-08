from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.llm.exceptions import LLMError
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.models import LlmModel
from app.schemas.llm_model import (
    LlmModelCreate,
    LlmModelOut,
    LlmModelTestRequest,
    LlmModelTestResponse,
    LlmModelUpdate,
)
from app.services import llm_model_service

router = APIRouter(prefix="/llm-models", tags=["llm-models"])


@router.get("")
def list_models(db: Session = Depends(get_db), _=Depends(require_permission("ai:read"))):
    items = llm_model_service.list_models(db)
    data = [LlmModelOut.model_validate(m).model_dump(mode="json") for m in items]
    return success(data)


@router.get("/{model_id}")
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    model = llm_model_service.get_model_by_id(db, model_id)
    if model is None:
        raise BizException("模型不存在", http_status=404)
    return success(LlmModelOut.model_validate(model).model_dump(mode="json"))


@router.post("")
def create_model(
    payload: LlmModelCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    if llm_model_service.get_model_by_name(db, payload.name):
        raise BizException("模型名称已存在")
    model = llm_model_service.create_model(db, **payload.model_dump())
    return success(LlmModelOut.model_validate(model).model_dump(mode="json"), msg="创建成功")


@router.put("/{model_id}")
def update_model(
    model_id: int,
    payload: LlmModelUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    model = llm_model_service.get_model_by_id(db, model_id)
    if model is None:
        raise BizException("模型不存在", http_status=404)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != model.name:
        if llm_model_service.get_model_by_name(db, data["name"]):
            raise BizException("模型名称已存在")
    updated = llm_model_service.update_model(db, model, data)
    return success(LlmModelOut.model_validate(updated).model_dump(mode="json"), msg="更新成功")


@router.delete("/{model_id}")
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    model = llm_model_service.get_model_by_id(db, model_id)
    if model is None:
        raise BizException("模型不存在", http_status=404)
    if model.is_default:
        raise BizException("默认模型不可删除，请先将其他模型设为默认")
    llm_model_service.delete_model(db, model)
    return success(None, msg="删除成功")


@router.post("/{model_id}/test")
def test_saved_model(
    model_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    model = llm_model_service.get_model_by_id(db, model_id)
    if model is None:
        raise BizException("模型不存在", http_status=404)
    try:
        result = llm_model_service.test_model_connection(model)
    except LLMError as exc:
        return success(
            LlmModelTestResponse(ok=False, latency_ms=0, message=str(exc)).model_dump()
        )
    return success(
        LlmModelTestResponse(
            ok=True,
            latency_ms=result.latency_ms,
            message=result.content[:200],
        ).model_dump()
    )


@router.post("/test")
def test_config(
    payload: LlmModelTestRequest,
    _=Depends(require_permission("ai:write")),
):
    """使用未保存的配置测试连通性。"""
    try:
        result = llm_model_service.test_connection_from_config(
            base_url=payload.base_url,
            api_key=payload.api_key,
            model_name=payload.model,
        )
    except LLMError as exc:
        return success(
            LlmModelTestResponse(ok=False, latency_ms=0, message=str(exc)).model_dump()
        )
    return success(
        LlmModelTestResponse(
            ok=True,
            latency_ms=result.latency_ms,
            message=result.content[:200],
        ).model_dump()
    )
