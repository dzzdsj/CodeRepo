from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PromptTemplate
from app.models.prompt_template import extract_variables


def get_template_by_id(db: Session, template_id: int) -> PromptTemplate | None:
    return db.get(PromptTemplate, template_id)


def get_template_by_name(db: Session, name: str) -> PromptTemplate | None:
    return db.scalar(select(PromptTemplate).where(PromptTemplate.name == name))


def list_templates(db: Session) -> list[PromptTemplate]:
    return list(db.scalars(select(PromptTemplate).order_by(PromptTemplate.id.asc())).all())


def create_template(db: Session, name: str, content: str, description: str | None, is_enabled: bool) -> PromptTemplate:
    template = PromptTemplate(
        name=name,
        content=content,
        description=description,
        variables=extract_variables(content),
        is_enabled=is_enabled,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(db: Session, template: PromptTemplate, data: dict) -> PromptTemplate:
    new_content = data.pop("content", None)
    if new_content is not None and new_content != template.content:
        template.content = new_content
        template.variables = extract_variables(new_content)
        template.version += 1

    for key, value in data.items():
        if value is not None:
            setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template: PromptTemplate) -> None:
    db.delete(template)
    db.commit()
