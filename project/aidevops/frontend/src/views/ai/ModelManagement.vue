<template>
  <el-card shadow="never">
    <div class="toolbar">
      <span class="tip">共 {{ tableData.length }} 个模型</span>
      <div class="spacer" />
      <el-button type="success" :icon="Plus" v-if="canWrite" @click="openCreate">
        新增模型
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="provider" label="服务商" width="110">
        <template #default="{ row }">
          <el-tag size="small">{{ row.provider }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="base_url" label="Base URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="model" label="模型" min-width="140" show-overflow-tooltip />
      <el-table-column label="API Key" width="120">
        <template #default="{ row }">{{ row.api_key || '-' }}</template>
      </el-table-column>
      <el-table-column label="默认" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_enabled" type="success" size="small">启用</el-tag>
          <el-tag v-else type="info" size="small">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="onTest(row)">测试连接</el-button>
          <el-button size="small" v-if="canWrite" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            type="danger"
            v-if="canWrite"
            :disabled="row.is_default"
            @click="onDelete(row)"
          >
            删除
          </el-button>
          <span v-if="!canWrite" style="color: var(--el-text-color-secondary)">—</span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="padding-right: 16px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="如：DeepSeek-V3" />
      </el-form-item>
      <el-form-item label="服务商" prop="provider">
        <el-select v-model="form.provider" style="width: 100%">
          <el-option v-for="p in providers" :key="p" :label="p" :value="p" />
        </el-select>
      </el-form-item>
      <el-form-item label="Base URL" prop="base_url">
        <el-input v-model="form.base_url" placeholder="https://api.deepseek.com" />
      </el-form-item>
      <el-form-item label="API Key" prop="api_key">
        <el-input v-model="form.api_key" type="password" show-password :placeholder="isEdit ? '留空则不修改' : '请输入 API Key'" />
      </el-form-item>
      <el-form-item label="模型" prop="model">
        <el-input v-model="form.model" placeholder="如：deepseek-chat" />
      </el-form-item>
      <el-form-item label="默认模型">
        <el-switch v-model="form.is_default" />
      </el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="form.is_enabled" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="选填" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button :loading="testing" @click="onTestConfig">测试连接</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  createLlmModel,
  deleteLlmModel,
  listLlmModels,
  testLlmModel,
  testLlmModelConfig,
  updateLlmModel,
  type LlmModelFormData,
  type LlmModelItem
} from '@/api/llmModel'

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('ai:write'))

const providers = ['openai', 'deepseek', 'qwen', 'zhipu', 'ollama', 'custom']

const tableData = ref<LlmModelItem[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const submitting = ref(false)
const testing = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<LlmModelFormData>({
  name: '',
  provider: 'deepseek',
  base_url: '',
  api_key: '',
  model: '',
  is_default: false,
  is_enabled: true,
  remark: ''
})

const isEdit = computed(() => mode.value === 'edit')
const dialogTitle = computed(() => (isEdit.value ? '编辑模型' : '新增模型'))

const rules: FormRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择服务商', trigger: 'change' }],
  base_url: [{ required: true, message: '请输入 Base URL', trigger: 'blur' }],
  api_key: [
    {
      validator: (_rule, value, cb) => {
        if (!isEdit.value && !value) {
          cb(new Error('请输入 API Key'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ],
  model: [{ required: true, message: '请输入模型标识', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    tableData.value = await listLlmModels()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.provider = 'deepseek'
  form.base_url = ''
  form.api_key = ''
  form.model = ''
  form.is_default = false
  form.is_enabled = true
  form.remark = ''
  editingId.value = null
}

function openCreate() {
  mode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: LlmModelItem) {
  mode.value = 'edit'
  editingId.value = row.id
  form.name = row.name
  form.provider = row.provider
  form.base_url = row.base_url
  form.api_key = ''
  form.model = row.model
  form.is_default = row.is_default
  form.is_enabled = row.is_enabled
  form.remark = row.remark ?? ''
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: Partial<LlmModelFormData> = {
      name: form.name,
      provider: form.provider,
      base_url: form.base_url,
      model: form.model,
      is_default: form.is_default,
      is_enabled: form.is_enabled,
      remark: form.remark || undefined
    }
    if (form.api_key) {
      payload.api_key = form.api_key
    }
    if (isEdit.value && editingId.value) {
      await updateLlmModel(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createLlmModel(payload as LlmModelFormData)
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

async function onDelete(row: LlmModelItem) {
  try {
    await ElMessageBox.confirm(`确定删除模型 "${row.name}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteLlmModel(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 取消
  }
}

async function onTest(row: LlmModelItem) {
  testing.value = true
  try {
    const result = await testLlmModel(row.id)
    if (result.ok) {
      ElMessage.success(`连接成功，耗时 ${result.latency_ms}ms`)
    } else {
      ElMessage.error(`连接失败：${result.message}`)
    }
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    testing.value = false
  }
}

async function onTestConfig() {
  if (!form.base_url || !form.model || (!form.api_key && !isEdit.value)) {
    ElMessage.warning('请先填写 Base URL、模型和 API Key')
    return
  }
  testing.value = true
  try {
    const result = await testLlmModelConfig({
      base_url: form.base_url,
      api_key: form.api_key || 'placeholder',
      model: form.model
    })
    if (result.ok) {
      ElMessage.success(`连接成功，耗时 ${result.latency_ms}ms`)
    } else {
      ElMessage.error(`连接失败：${result.message}`)
    }
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    testing.value = false
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
</style>
