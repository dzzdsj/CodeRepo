from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.exceptions import BizException
from app.core.response import success
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateOut,
    PromptTemplateRenderRequest,
    PromptTemplateRenderResponse,
    PromptTemplateUpdate,
)
from app.services import prompt_template_service

router = APIRouter(prefix="/prompt-templates", tags=["prompt-templates"])


@router.get("")
def list_templates(db: Session = Depends(get_db), _=Depends(require_permission("ai:read"))):
    items = prompt_template_service.list_templates(db)
    data = [PromptTemplateOut.model_validate(t).model_dump(mode="json") for t in items]
    return success(data)


@router.get("/{template_id}")
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    template = prompt_template_service.get_template_by_id(db, template_id)
    if template is None:
        raise BizException("模板不存在", http_status=404)
    return success(PromptTemplateOut.model_validate(template).model_dump(mode="json"))


@router.post("")
def create_template(
    payload: PromptTemplateCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    if prompt_template_service.get_template_by_name(db, payload.name):
        raise BizException("模板名称已存在")
    template = prompt_template_service.create_template(db, **payload.model_dump())
    return success(PromptTemplateOut.model_validate(template).model_dump(mode="json"), msg="创建成功")


@router.put("/{template_id}")
def update_template(
    template_id: int,
    payload: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    template = prompt_template_service.get_template_by_id(db, template_id)
    if template is None:
        raise BizException("模板不存在", http_status=404)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != template.name:
        if prompt_template_service.get_template_by_name(db, data["name"]):
            raise BizException("模板名称已存在")
    updated = prompt_template_service.update_template(db, template, data)
    return success(PromptTemplateOut.model_validate(updated).model_dump(mode="json"), msg="更新成功")


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:write")),
):
    template = prompt_template_service.get_template_by_id(db, template_id)
    if template is None:
        raise BizException("模板不存在", http_status=404)
    prompt_template_service.delete_template(db, template)
    return success(None, msg="删除成功")


@router.post("/{template_id}/render")
def render_template(
    template_id: int,
    payload: PromptTemplateRenderRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("ai:read")),
):
    template = prompt_template_service.get_template_by_id(db, template_id)
    if template is None:
        raise BizException("模板不存在", http_status=404)
    rendered = template.render(payload.values)
    return success(PromptTemplateRenderResponse(rendered=rendered).model_dump())
