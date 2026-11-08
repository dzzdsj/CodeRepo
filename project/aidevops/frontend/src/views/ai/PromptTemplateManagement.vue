<template>
  <el-card shadow="never">
    <div class="toolbar">
      <span class="tip">共 {{ tableData.length }} 个模板</span>
      <div class="spacer" />
      <el-button type="success" :icon="Plus" v-if="canWrite" @click="openCreate">
        新增模板
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="description" label="描述" min-width="180">
        <template #default="{ row }">{{ row.description || '-' }}</template>
      </el-table-column>
      <el-table-column label="变量" min-width="200">
        <template #default="{ row }">
          <el-tag v-if="row.variables.length" v-for="v in row.variables" :key="v" size="small" style="margin-right: 6px">
            {{ v }}
          </el-tag>
          <span v-else style="color: var(--el-text-color-secondary)">无</span>
        </template>
      </el-table-column>
      <el-table-column label="版本" width="80">
        <template #default="{ row }">v{{ row.version }}</template>
      </el-table-column>
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag>
          <el-tag v-else type="info" size="small">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="170">
        <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openPreview(row)">预览渲染</el-button>
          <el-button size="small" v-if="canWrite" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" v-if="canWrite" @click="onDelete(row)">删除</el-button>
          <span v-if="!canWrite" style="color: var(--el-text-color-secondary)">—</span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 新增/编辑弹窗 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" style="padding-right: 16px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" placeholder="选填" />
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="8"
          placeholder="使用 {{变量名}} 作为占位符，例如：请审查以下代码：{{code}}"
        />
        <div class="hint">变量将从内容中自动提取</div>
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

  <!-- 预览渲染弹窗 -->
  <el-dialog v-model="previewVisible" title="预览渲染" width="640px">
    <div v-if="previewTemplate">
      <div class="preview-meta">模板：{{ previewTemplate.name }}（v{{ previewTemplate.version }}）</div>
      <div v-if="previewTemplate.variables.length" class="preview-vars">
        <el-form label-width="120px">
          <el-form-item v-for="v in previewTemplate.variables" :key="v" :label="v">
            <el-input v-model="previewValues[v]" :placeholder="`请输入 ${v}`" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else class="hint">该模板无变量</div>
      <el-button type="primary" size="small" :loading="rendering" @click="doRender">渲染</el-button>
      <div v-if="rendered" class="rendered-box">
        <div class="rendered-title">渲染结果：</div>
        <pre>{{ rendered }}</pre>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  createPromptTemplate,
  deletePromptTemplate,
  listPromptTemplates,
  renderPromptTemplate,
  updatePromptTemplate,
  type PromptTemplateFormData,
  type PromptTemplateItem
} from '@/api/promptTemplate'

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('ai:write'))

const tableData = ref<PromptTemplateItem[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const submitting = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<PromptTemplateFormData>({
  name: '',
  description: '',
  content: '',
  is_enabled: true
})

const previewVisible = ref(false)
const previewTemplate = ref<PromptTemplateItem | null>(null)
const previewValues = reactive<Record<string, string>>({})
const rendering = ref(false)
const rendered = ref('')

const isEdit = computed(() => mode.value === 'edit')
const dialogTitle = computed(() => (isEdit.value ? '编辑模板' : '新增模板'))

const rules: FormRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
}

function formatDate(value: string) {
  return value ? value.replace('T', ' ').slice(0, 19) : '-'
}

async function loadList() {
  loading.value = true
  try {
    tableData.value = await listPromptTemplates()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.description = ''
  form.content = ''
  form.is_enabled = true
  editingId.value = null
}

function openCreate() {
  mode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: PromptTemplateItem) {
  mode.value = 'edit'
  editingId.value = row.id
  form.name = row.name
  form.description = row.description ?? ''
  form.content = row.content
  form.is_enabled = row.is_enabled
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: Partial<PromptTemplateFormData> = {
      name: form.name,
      description: form.description || undefined,
      content: form.content,
      is_enabled: form.is_enabled
    }
    if (isEdit.value && editingId.value) {
      await updatePromptTemplate(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createPromptTemplate(payload as PromptTemplateFormData)
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

async function onDelete(row: PromptTemplateItem) {
  try {
    await ElMessageBox.confirm(`确定删除模板 "${row.name}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deletePromptTemplate(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 取消
  }
}

function openPreview(row: PromptTemplateItem) {
  previewTemplate.value = row
  Object.keys(previewValues).forEach((k) => delete previewValues[k])
  row.variables.forEach((v) => (previewValues[v] = ''))
  rendered.value = ''
  previewVisible.value = true
}

async function doRender() {
  if (!previewTemplate.value) return
  rendering.value = true
  try {
    const res = await renderPromptTemplate(previewTemplate.value.id, { ...previewValues })
    rendered.value = res.rendered
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    rendering.value = false
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
.hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 4px;
}
.preview-meta {
  font-weight: 600;
  margin-bottom: 12px;
}
.preview-vars {
  margin-bottom: 12px;
}
.rendered-box {
  margin-top: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}
.rendered-title {
  font-weight: 600;
  margin-bottom: 8px;
}
.rendered-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
}
</style>
