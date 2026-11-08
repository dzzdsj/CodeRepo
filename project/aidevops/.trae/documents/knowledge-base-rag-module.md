# 知识库 / RAG 模块实现方案

## Context

AI 赋能研发运维辅助系统已完成阶段一（认证、RBAC、用户管理）和阶段二的大部分（大模型管理、Prompt 模板管理）。菜单中 `/ai/knowledge`（知识库）已存在但路由指向占位组件 `PagePlaceholder`。按 README 开发计划，下一步是实现「RAG 知识库基础」——文档上传、向量化、检索增强生成。

## 设计思路

遵循项目「默认 SQLite，零外部依赖」的精简哲学：

- **不引入 chromadb / langchain / sentence-transformers 等重型依赖**
- **Embedding 存储为 JSON 数组存入 SQLite**——复用现有数据库，无需独立向量库
- **Embedding 生成调用 OpenAI 兼容的 `/v1/embeddings` 端点**——复用已配置的大模型（base_url + api_key）
- **纯 Python cosine similarity**——无需 numpy，小数据量足够
- **RAG 问答复用现有 `LLMClient`**——检索相关片段后，用 chat completions 生成回答

## 后端实现

### 新增文件

#### 1. `backend/app/models/knowledge_doc.py` — 数据模型

两个表，一对多关系：

```
KnowledgeDoc（文档元数据）
  id, title(256, index), content(Text), source(256, nullable), 
  doc_type(32, default="text"), status(32, default="pending"),  # pending/embedded/failed
  chunk_count(int, default=0), is_enabled(bool, default=True), 
  remark(Text, nullable), timestamps

KnowledgeChunk（文档分块 + 向量）
  id, doc_id(FK→knowledge_docs.id, CASCADE), chunk_index(int), 
  content(Text), embedding(JSON, nullable), timestamps
```

#### 2. `backend/app/schemas/knowledge_doc.py` — Pydantic 模式

遵循 `llm_model.py` 的 Base→Create→Update→Out 分层模式：
- `KnowledgeDocCreate`: title, content, source?, doc_type?, is_enabled?
- `KnowledgeDocUpdate`: 所有字段可选
- `KnowledgeDocOut`: from_attributes=True，不含 content 全文（列表场景），详情接口单独返回
- `KnowledgeSearchRequest`: query, top_k?=5
- `KnowledgeSearchResultItem`: doc_id, doc_title, chunk_index, chunk_content, score
- `KnowledgeAskRequest`: query, top_k?=5
- `KnowledgeAskResponse`: answer, sources(list[KnowledgeSearchResultItem])

#### 3. `backend/app/ai/llm/embedding.py` — Embedding 客户端

仿照 `LLMClient`（`app/ai/llm/client.py`）的 httpx 模式：
- `EmbeddingClient(base_url, api_key, model)`
- `embed(texts: list[str]) -> list[list[float]]` — 调用 `/v1/embeddings`
- `embed_one(text: str) -> list[float]` — 单条便捷方法
- `close()` / `__enter__` / `__exit__` — 同 LLMClient

#### 4. `backend/app/services/knowledge_service.py` — 业务逻辑层

仿照 `llm_model_service.py` 的函数式组织：

- **文档 CRUD**: `get_doc_by_id`, `get_doc_by_title`, `list_docs`, `create_doc`, `update_doc`, `delete_doc`
- **分块**: `chunk_text(text, chunk_size=500, overlap=50) -> list[str]` — 按段落+固定大小切分
- **向量化**: `embed_document(db, doc)` — 分块 → 调用 EmbeddingClient → 存入 KnowledgeChunk → 更新 doc.status
- **检索**: `search(db, query, top_k=5)` — 查询向量化 → cosine similarity → 返回 Top-K
- **RAG 问答**: `ask(db, query, top_k=5)` — search → 拼 system prompt（含知识片段）→ LLMClient.chat → 返回答案 + sources
- **辅助**: `_get_default_llm_config(db)` — 获取 is_default=True 的 LlmModel，返回 (base_url, api_key, model)
- **辅助**: `_cosine_similarity(a, b)` — 纯 Python 实现

#### 5. `backend/app/api/v1/knowledge.py` — API 路由

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/knowledge/docs` | ai:read | 文档列表 |
| POST | `/knowledge/docs` | ai:write | 新建文档 |
| GET | `/knowledge/docs/{id}` | ai:read | 文档详情（含 content） |
| PUT | `/knowledge/docs/{id}` | ai:write | 更新文档 |
| DELETE | `/knowledge/docs/{id}` | ai:write | 删除文档（级联删除分块） |
| POST | `/knowledge/docs/{id}/embed` | ai:write | 触发向量化 |
| POST | `/knowledge/search` | ai:read | 语义检索 |
| POST | `/knowledge/ask` | ai:read | RAG 问答 |

### 修改文件

| 文件 | 改动 |
|------|------|
| `backend/app/models/__init__.py` | 导出 `KnowledgeDoc`, `KnowledgeChunk` |
| `backend/app/schemas/__init__.py` | 导出 `knowledge_doc` 模块 |
| `backend/app/ai/llm/__init__.py` | 导出 `EmbeddingClient` |
| `backend/app/api/v1/router.py` | `include_router(knowledge_router)` |
| `backend/app/core/config.py` | 新增 `rag_chunk_size=500`, `rag_chunk_overlap=50`, `rag_top_k=5` |

### Alembic 迁移

```bash
cd backend && alembic revision --autogenerate -m "add knowledge_docs and knowledge_chunks"
alembic upgrade head
```

## 前端实现

### 新增文件

#### 1. `frontend/src/api/knowledge.ts` — API 客户端

仿照 `llmModel.ts`：定义 TypeScript 接口 + request 封装。

#### 2. `frontend/src/views/ai/KnowledgeBase.vue` — 管理页面

仿照 `ModelManagement.vue` 的 el-card + el-table + el-dialog 模式：

- **工具栏**: 文档数量 + "新增文档" 按钮 + "知识问答" 按钮
- **表格列**: 标题、来源、类型、状态(pending/embedded/failed tag)、分块数、启用、操作
- **操作按钮**: 向量化(embed) / 编辑 / 删除
- **新增/编辑 Dialog**: title, source, doc_type(select), content(textarea), is_enabled(switch)
- **知识问答 Dialog**: query(textarea) + "搜索"按钮 → 答案区域 + 引用来源列表

### 修改文件

| 文件 | 改动 |
|------|------|
| `frontend/src/router/index.ts` | `realComponents` 添加 `'/ai/knowledge': () => import('@/views/ai/KnowledgeBase.vue')` |

## 验证方式

1. 后端: `alembic upgrade head` → `uvicorn app.main:app --reload`
2. 前端: `npm run dev`
3. 功能测试: 新建文档 → 触发向量化 → 语义检索 → RAG 问答
4. 类型检查: `npx vue-tsc --noEmit`
5. 权限验证: 只读用户可访问页面但无写操作按钮
