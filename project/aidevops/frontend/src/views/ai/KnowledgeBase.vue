<template>
  <el-card shadow="never">
    <div class="toolbar">
      <span class="tip">共 {{ tableData.length }} 个文档</span>
      <div class="spacer" />
      <el-button type="primary" :icon="ChatRound" @click="openAsk">知识问答</el-button>
      <el-button type="success" :icon="Plus" v-if="canWrite" @click="openCreate">
        新增文档
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="source" label="来源" width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.source || '-' }}</template>
      </el-table-column>
      <el-table-column prop="doc_type" label="类型" width="90">
        <template #default="{ row }">
          <el-tag size="small">{{ row.doc_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'embedded'" type="success" size="small">已向量化</el-tag>
          <el-tag v-else-if="row.status === 'failed'" type="danger" size="small">失败</el-tag>
          <el-tag v-else type="info" size="small">待处理</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="分块数" width="90" />
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag>
          <el-tag v-else type="info" size="small">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" v-if="canWrite" :loading="embeddingId === row.id" @click="onEmbed(row)">向量化</el-button>
          <el-button size="small" v-if="canWrite" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            type="danger"
            v-if="canWrite"
            @click="onDelete(row)"
          >
            删除
          </el-button>
          <span v-if="!canWrite" style="color: var(--el-text-color-secondary)">—</span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 新增/编辑文档 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" style="padding-right: 16px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="如：系统部署手册" />
      </el-form-item>
      <el-form-item label="来源" prop="source">
        <el-input v-model="form.source" placeholder="选填，如：wiki/部署文档.md" />
      </el-form-item>
      <el-form-item label="类型" prop="doc_type">
        <el-select v-model="form.doc_type" style="width: 100%">
          <el-option label="文本" value="text" />
          <el-option label="Markdown" value="markdown" />
        </el-select>
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="10"
          placeholder="粘贴文档全文，提交后可点击「向量化」生成嵌入向量"
        />
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="form.is_enabled" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
    </template>
  </el-dialog>

  <!-- 知识问答 -->
  <el-dialog v-model="askVisible" title="知识问答" width="720px" @close="askAnswer = null; askSources = []">
    <el-input
      v-model="askQuery"
      type="textarea"
      :rows="3"
      placeholder="输入你的问题，系统将从知识库中检索相关内容并生成回答"
    />
    <div style="margin-top: 12px; text-align: right">
      <el-button type="primary" :loading="asking" :icon="Promotion" @click="onAsk">提问</el-button>
    </div>
    <el-divider v-if="askAnswer" />
    <div v-if="askAnswer" class="ask-result">
      <div class="ask-answer">
        <span class="ask-label">回答：</span>
        <div class="ask-content">{{ askAnswer }}</div>
      </div>
      <div v-if="askSources.length" class="ask-sources">
        <span class="ask-label">引用来源：</span>
        <div v-for="(s, i) in askSources" :key="i" class="source-item">
          <el-tag size="small" type="info">{{ s.doc_title }}</el-tag>
          <span class="source-score">相似度 {{ s.score }}</span>
          <div class="source-text">{{ s.chunk_content }}</div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ChatRound, Plus, Promotion } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  askKnowledge,
  createKnowledgeDoc,
  deleteKnowledgeDoc,
  embedKnowledgeDoc,
  listKnowledgeDocs,
  updateKnowledgeDoc,
  type KnowledgeDocFormData,
  type KnowledgeDocItem,
  type KnowledgeSearchResult
} from '@/api/knowledge'

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('ai:write'))

const tableData = ref<KnowledgeDocItem[]>([])
const loading = ref(false)

// 文档新增/编辑
const dialogVisible = ref(false)
const submitting = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<KnowledgeDocFormData>({
  title: '',
  content: '',
  source: '',
  doc_type: 'text',
  is_enabled: true
})

const isEdit = computed(() => mode.value === 'edit')
const dialogTitle = computed(() => (isEdit.value ? '编辑文档' : '新增文档'))

const rules: FormRules = {
  title: [{ required: true, message: '请输入文档标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入文档内容', trigger: 'blur' }]
}

// 向量化
const embeddingId = ref<number | null>(null)

// 知识问答
const askVisible = ref(false)
const askQuery = ref('')
const asking = ref(false)
const askAnswer = ref<string | null>(null)
const askSources = ref<KnowledgeSearchResult[]>([])

async function loadList() {
  loading.value = true
  try {
    tableData.value = await listKnowledgeDocs()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.title = ''
  form.content = ''
  form.source = ''
  form.doc_type = 'text'
  form.is_enabled = true
  editingId.value = null
}

function openCreate() {
  mode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

async function openEdit(row: KnowledgeDocItem) {
  mode.value = 'edit'
  editingId.value = row.id
  // 拉取详情获取 content 全文
  try {
    const detail = await import('@/api/knowledge').then((m) => m.getKnowledgeDoc(row.id))
    form.title = detail.title
    form.content = detail.content
    form.source = detail.source ?? ''
    form.doc_type = detail.doc_type
    form.is_enabled = detail.is_enabled
  } catch (err) {
    ElMessage.error((err as Error).message)
    return
  }
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: Partial<KnowledgeDocFormData> = {
      title: form.title,
      content: form.content,
      source: form.source || undefined,
      doc_type: form.doc_type,
      is_enabled: form.is_enabled
    }
    if (isEdit.value && editingId.value) {
      await updateKnowledgeDoc(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createKnowledgeDoc(payload as KnowledgeDocFormData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: KnowledgeDocItem) {
  try {
    await ElMessageBox.confirm(`确定删除文档 "${row.title}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteKnowledgeDoc(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 取消
  }
}

async function onEmbed(row: KnowledgeDocItem) {
  embeddingId.value = row.id
  try {
    const result = await embedKnowledgeDoc(row.id)
    if (result.status === 'failed') {
      ElMessage.error('向量化失败，请检查大模型配置是否支持 Embedding')
    } else {
      ElMessage.success(`向量化成功，共 ${result.chunk_count} 个分块`)
    }
    loadList()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    embeddingId.value = null
  }
}

function openAsk() {
  askQuery.value = ''
  askAnswer.value = null
  askSources.value = []
  askVisible.value = true
}

async function onAsk() {
  if (!askQuery.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  asking.value = true
  try {
    const result = await askKnowledge(askQuery.value)
    askAnswer.value = result.answer
    askSources.value = result.sources
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    asking.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.spacer {
  flex: 1;
}
.ask-result {
  margin-top: 8px;
}
.ask-answer {
  margin-bottom: 16px;
}
.ask-label {
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.ask-content {
  margin-top: 8px;
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  white-space: pre-wrap;
  line-height: 1.6;
}
.ask-sources {
  margin-top: 8px;
}
.source-item {
  margin-top: 12px;
  padding: 10px 14px;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
}
.source-score {
  margin-left: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.source-text {
  margin-top: 6px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>
