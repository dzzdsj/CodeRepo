"""AI 代码审查服务层：记录 CRUD + LLM 结构化审查。"""
import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.llm import LLMClient, ChatMessage
from app.ai.llm.exceptions import LLMError
from app.models import CodeReview, LlmModel


# ────────────────── 记录 CRUD ──────────────────


def get_review_by_id(db: Session, review_id: int) -> CodeReview | None:
    return db.get(CodeReview, review_id)


def list_reviews(db: Session) -> list[CodeReview]:
    return list(db.scalars(select(CodeReview).order_by(CodeReview.id.desc())).all())


def create_review(db: Session, **kwargs) -> CodeReview:
    review = CodeReview(**kwargs)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review: CodeReview) -> None:
    db.delete(review)
    db.commit()


# ────────────────── LLM 审查 ──────────────────


def _get_default_llm(db: Session) -> LlmModel | None:
    return db.scalar(select(LlmModel).where(LlmModel.is_default.is_(True)))


REVIEW_SYSTEM_PROMPT = """你是一名资深代码审查专家。请审查用户提交的代码，从以下维度识别问题：
1. Bug（逻辑错误、边界条件、空指针等）
2. 安全漏洞（注入、硬编码密钥、不安全反序列化等）
3. 规范问题（命名、可读性、代码风格）
4. 性能问题（低效算法、内存泄漏、N+1查询等）

请严格按以下 JSON 格式输出，不要输出任何其他内容：
{
  "summary": "整体评价（100字以内）",
  "score": 0-100的质量评分,
  "issues": [
    {
      "severity": "high|medium|low",
      "category": "bug|security|style|performance|other",
      "line": 行号或null,
      "description": "问题描述",
      "suggestion": "修改建议"
    }
  ]
}
如果没有发现问题，issues 返回空数组。"""


def _parse_review_json(content: str) -> dict:
    """从 LLM 输出中提取 JSON；失败则降级为 raw 文本。"""
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if isinstance(data, dict) and "issues" in data:
                data.setdefault("summary", "")
                return data
        except json.JSONDecodeError:
            pass
    return {"summary": content, "score": None, "issues": []}


def run_review(db: Session, review: CodeReview) -> CodeReview:
    """调用默认大模型对代码执行审查，结构化结果写入 ai_suggestions。"""
    llm_config = _get_default_llm(db)
    if llm_config is None:
        raise LLMError("未找到默认大模型，请先在「大模型管理」中设置默认模型")

    lang = f"（语言：{review.language}）" if review.language != "text" else ""
    user_content = f"请审查以下代码{lang}：\n\n```\n{review.code_content}\n```"

    client = LLMClient(
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        model=llm_config.model,
    )
    try:
        result = client.chat(
            [
                ChatMessage(role="system", content=REVIEW_SYSTEM_PROMPT),
                ChatMessage(role="user", content=user_content),
            ],
            temperature=0.2,
        )
    except LLMError as exc:
        review.status = "failed"
        review.ai_suggestions = {
            "summary": "审查失败",
            "score": None,
            "issues": [],
            "error": str(exc),
        }
        db.commit()
        raise
    finally:
        client.close()

    suggestions = _parse_review_json(result.content)
    review.ai_suggestions = suggestions
    review.status = "completed"
    review.score = suggestions.get("score") if isinstance(suggestions.get("score"), int) else None
    db.commit()
    db.refresh(review)
    return review
