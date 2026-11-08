from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.ai.llm import LLMClient, ChatResult
from app.ai.llm.exceptions import LLMError
from app.models import LlmModel


def get_model_by_id(db: Session, model_id: int) -> LlmModel | None:
    return db.get(LlmModel, model_id)


def get_model_by_name(db: Session, name: str) -> LlmModel | None:
    return db.scalar(select(LlmModel).where(LlmModel.name == name))


def list_models(db: Session) -> list[LlmModel]:
    return list(db.scalars(select(LlmModel).order_by(LlmModel.id.asc())).all())


def _ensure_single_default(db: Session, exclude_id: int | None = None) -> None:
    """取消除 exclude_id 外所有模型的默认标记。"""
    stmt = update(LlmModel).where(LlmModel.id != exclude_id).values(is_default=False)
    db.execute(stmt)


def create_model(db: Session, **kwargs) -> LlmModel:
    is_default = bool(kwargs.get("is_default"))
    if is_default:
        _ensure_single_default(db)
    model = LlmModel(**kwargs)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_model(db: Session, model: LlmModel, data: dict) -> LlmModel:
    # api_key 为 None 或空字符串时保留原值
    api_key = data.pop("api_key", None)
    if api_key:
        model.api_key = api_key

    is_default = data.pop("is_default", None)
    if is_default is True:
        _ensure_single_default(db, exclude_id=model.id)
        model.is_default = True
    elif is_default is False:
        model.is_default = False

    for key, value in data.items():
        if value is not None:
            setattr(model, key, value)

    db.commit()
    db.refresh(model)
    return model


def delete_model(db: Session, model: LlmModel) -> None:
    db.delete(model)
    db.commit()


def test_model_connection(model: LlmModel) -> ChatResult:
    """使用已保存的模型配置进行连通性测试。"""
    client = LLMClient(
        base_url=model.base_url,
        api_key=model.api_key,
        model=model.model,
    )
    try:
        return client.test_connection()
    finally:
        client.close()


def test_connection_from_config(base_url: str, api_key: str, model_name: str) -> ChatResult:
    """使用未保存的配置进行连通性测试（创建/编辑前预览）。"""
    client = LLMClient(base_url=base_url, api_key=api_key, model=model_name)
    try:
        return client.test_connection()
    finally:
        client.close()
