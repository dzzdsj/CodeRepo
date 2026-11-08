"""知识库服务层：文档 CRUD、分块、向量化、语义检索、RAG 问答。"""
import math
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.llm import LLMClient, ChatMessage
from app.ai.llm.embedding import EmbeddingClient
from app.ai.llm.exceptions import LLMError
from app.core.config import settings
from app.models import KnowledgeChunk, KnowledgeDoc, LlmModel


# ────────────────── 文档 CRUD ──────────────────


def get_doc_by_id(db: Session, doc_id: int) -> KnowledgeDoc | None:
    return db.get(KnowledgeDoc, doc_id)


def get_doc_by_title(db: Session, title: str) -> KnowledgeDoc | None:
    return db.scalar(select(KnowledgeDoc).where(KnowledgeDoc.title == title))


def list_docs(db: Session) -> list[KnowledgeDoc]:
    return list(db.scalars(select(KnowledgeDoc).order_by(KnowledgeDoc.id.asc())).all())


def create_doc(db: Session, **kwargs) -> KnowledgeDoc:
    doc = KnowledgeDoc(**kwargs)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_doc(db: Session, doc: KnowledgeDoc, data: dict) -> KnowledgeDoc:
    # 如果 content 被修改，重置状态为 pending（需要重新向量化）
    new_content = data.get("content")
    if new_content is not None and new_content != doc.content:
        doc.status = "pending"
        doc.chunk_count = 0
        # 删除旧分块
        db.query(KnowledgeChunk).filter(KnowledgeChunk.doc_id == doc.id).delete()

    for key, value in data.items():
        if value is not None:
            setattr(doc, key, value)

    db.commit()
    db.refresh(doc)
    return doc


def delete_doc(db: Session, doc: KnowledgeDoc) -> None:
    db.delete(doc)  # cascade 会自动删除 chunks
    db.commit()


# ────────────────── 分块 ──────────────────


def chunk_text(text: str, chunk_size: int = 0, overlap: int = 0) -> list[str]:
    """将长文本按段落+固定大小切分为带重叠的块。"""
    chunk_size = chunk_size or settings.rag_chunk_size
    overlap = overlap or settings.rag_chunk_overlap

    # 先按双换行分段
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(para) > chunk_size:
            # 段落本身超长，按 chunk_size 硬切
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(para), chunk_size - overlap):
                chunk = para[i : i + chunk_size]
                if chunk:
                    chunks.append(chunk)
        elif len(current) + len(para) + 2 > chunk_size:
            if current:
                chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para

    if current:
        chunks.append(current)

    return chunks


# ────────────────── 向量化 ──────────────────


def _get_default_llm(db: Session) -> LlmModel | None:
    """获取默认 LLM 模型配置。"""
    return db.scalar(select(LlmModel).where(LlmModel.is_default.is_(True)))


def embed_document(db: Session, doc: KnowledgeDoc) -> KnowledgeDoc:
    """对文档执行分块 + 向量化，结果存入 knowledge_chunks 表。"""
    llm_config = _get_default_llm(db)
    if llm_config is None:
        raise LLMError("未找到默认大模型，请先在「大模型管理」中设置默认模型")

    # 删除旧分块
    db.query(KnowledgeChunk).filter(KnowledgeChunk.doc_id == doc.id).delete()

    # 分块
    chunks = chunk_text(doc.content)
    if not chunks:
        raise LLMError("文档内容为空，无法分块")

    # 调用 Embedding API
    try:
        client = EmbeddingClient(
            base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            model=llm_config.model,
        )
        try:
            embeddings = client.embed(chunks)
        finally:
            client.close()
    except LLMError:
        doc.status = "failed"
        db.commit()
        raise

    # 存储分块 + 向量
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        db.add(
            KnowledgeChunk(
                doc_id=doc.id,
                chunk_index=idx,
                content=chunk,
                embedding=emb,
            )
        )

    doc.status = "embedded"
    doc.chunk_count = len(chunks)
    db.commit()
    db.refresh(doc)
    return doc


# ────────────────── 检索 ──────────────────


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_chunks(
    db: Session, query: str, top_k: int = 0
) -> list[dict]:
    """语义检索：对 query 向量化后与所有 chunk 做余弦相似度，返回 Top-K。"""
    top_k = top_k or settings.rag_top_k
    llm_config = _get_default_llm(db)
    if llm_config is None:
        raise LLMError("未找到默认大模型，请先在「大模型管理」中设置默认模型")

    # 查询所有已向量化的分块
    chunks = list(
        db.scalars(
            select(KnowledgeChunk)
            .where(KnowledgeChunk.embedding.is_not(None))
            .join(KnowledgeDoc)
            .where(KnowledgeDoc.is_enabled.is_(True))
        ).all()
    )
    if not chunks:
        return []

    # 对 query 生成向量
    client = EmbeddingClient(
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        model=llm_config.model,
    )
    try:
        query_emb = client.embed_one(query)
    finally:
        client.close()

    # 计算相似度并排序
    scored = []
    for chunk in chunks:
        score = _cosine_similarity(query_emb, chunk.embedding or [])
        scored.append((chunk, score))
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for chunk, score in scored[:top_k]:
        doc = chunk.doc
        results.append(
            {
                "doc_id": doc.id,
                "doc_title": doc.title,
                "chunk_index": chunk.chunk_index,
                "chunk_content": chunk.content,
                "score": round(score, 4),
            }
        )
    return results


# ────────────────── RAG 问答 ──────────────────


def ask(db: Session, query: str, top_k: int = 0) -> dict:
    """RAG 问答：检索相关片段 → LLM 生成回答。"""
    sources = search_chunks(db, query, top_k)
    if not sources:
        return {
            "answer": "知识库中没有已向量化的文档，请先添加文档并执行向量化。",
            "sources": [],
        }

    # 拼装 system prompt
    context_parts = "\n\n".join(
        f"[片段{i + 1}]（来自《{s['doc_title']}》）\n{s['chunk_content']}"
        for i, s in enumerate(sources)
    )
    system_prompt = (
        "你是一个知识库问答助手。请基于以下知识片段回答用户问题。\n"
        "如果知识片段中没有相关信息，请如实说明。\n\n"
        f"知识片段：\n{context_parts}"
    )

    llm_config = _get_default_llm(db)
    if llm_config is None:
        raise LLMError("未找到默认大模型，请先在「大模型管理」中设置默认模型")

    client = LLMClient(
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        model=llm_config.model,
    )
    try:
        result = client.chat(
            [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=query),
            ],
            temperature=0.3,
        )
    finally:
        client.close()

    return {"answer": result.content, "sources": sources}
