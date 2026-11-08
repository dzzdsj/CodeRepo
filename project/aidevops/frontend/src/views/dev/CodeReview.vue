<template>
  <el-card shadow="never">
    <div class="toolbar">
      <span class="tip">共 {{ tableData.length }} 条审查记录</span>
      <div class="spacer" />
      <el-button type="primary" :icon="Plus" v-if="canWrite" @click="openCreate">
        新增审查
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="repo" label="仓库" min-width="160" show-overflow-tooltip />
      <el-table-column prop="title" label="描述" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.title || '-' }}</template>
      </el-table-column>
      <el-table-column prop="branch" label="分支" width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ row.branch || '-' }}</template>
      </el-table-column>
      <el-table-column prop="commit" label="Commit" width="110" show-overflow-tooltip>
        <template #default="{ row }">{{ row.commit || '-' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'completed'" type="success" size="small">已完成</el-tag>
          <el-tag v-else-if="row.status === 'failed'" type="danger" size="small">失败</el-tag>
          <el-tag v-else type="info" size="small">待审查</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="评分" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.score !== null" :type="scoreType(row.score)" size="small">
            {{ row.score }}
          </el-tag>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" show-overflow-tooltip />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            type="primary"
            v-if="canWrite"
            :loading="reviewingId === row.id"
            @click="onReview(row)"
          >
            AI审查
          </el-button>
          <el-button size="small" @click="openDetail(row)">详情</el-button>
          <el-button size="small" type="danger" v-if="canWrite" @click="onDelete(row)">
            删除
          </el-button>
          <span v-if="!canWrite" style="color: var(--el-text-color-secondary)">—</span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 新增审查 -->
  <el-dialog v-model="dialogVisible" title="新增代码审查" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" style="padding-right: 16px">
      <el-form-item label="仓库" prop="repo">
        <el-input v-model="form.repo" placeholder="如：aidevops / https://github.com/xxx/yyy" />
      </el-form-item>
      <el-form-item label="描述" prop="title">
        <el-input v-model="form.title" placeholder="选填，本次变更说明" />
      </el-form-item>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="分支" prop="branch">
            <el-input v-model="form.branch" placeholder="选填" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Commit" prop="commit">
            <el-input v-model="form.commit" placeholder="选填" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="语言" prop="language">
            <el-select v-model="form.language" style="width: 100%">
              <el-option v-for="lang in LANGS" :key="lang" :label="lang" :value="lang" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="代码" prop="code_content">
        <el-input
          v-model="form.code_content"
          type="textarea"
          :rows="12"
          placeholder="粘贴待审查的代码"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
    </template>
  </el-dialog>

  <!-- 审查详情 -->
  <el-dialog v-model="detailVisible" title="审查详情" width="760px" @closed="detail = null">
    <div v-loading="detailLoading">
      <template v-if="detail">
        <el-descriptions :column="3" border size="small" style="margin-bottom: 16px">
          <el-descriptions-item label="仓库">{{ detail.repo }}</el-descriptions-item>
          <el-descriptions-item label="分支">{{ detail.branch || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Commit">{{ detail.commit || '-' }}</el-descriptions-item>
        </el-descriptions>

        <template v-if="detail.status === 'completed' && detail.ai_suggestions">
          <div class="section-title">
            总评
            <el-tag
              v-if="detail.score !== null"
              :type="scoreType(detail.score)"
              size="small"
              style="margin-left: 8px"
            >
              评分 {{ detail.score }}
            </el-tag>
          </div>
          <div class="summary">{{ detail.ai_suggestions.summary || '-' }}</div>

          <div class="section-title">问题列表（{{ detail.ai_suggestions.issues.length }}）</div>
          <el-table
            v-if="detail.ai_suggestions.issues.length"
            :data="detail.ai_suggestions.issues"
            border
            size="small"
          >
            <el-table-column label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="severityType(row.severity)" size="small">
                  {{ severityLabel(row.severity) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="类别" width="100" />
            <el-table-column prop="line" label="行号" width="70">
              <template #default="{ row }">{{ row.line ?? '-' }}</template>
            </el-table-column>
            <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="suggestion" label="修改建议" min-width="200" show-overflow-tooltip />
          </el-table>
          <el-empty v-else description="未发现问题" :image-size="60" />
        </template>
        <el-alert
          v-else-if="detail.status === 'failed'"
          type="error"
          :closable="false"
          :title="detail.ai_suggestions?.error || 'AI审查失败'"
          show-icon
        />
        <el-alert v-else type="info" :closable="false" title="尚未执行AI审查" show-icon />

        <div class="section-title">代码</div>
        <pre class="code-block">{{ detail.code_content }}</pre>
      </template>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  createCodeReview,
  deleteCodeReview,
  getCodeReview,
  listCodeReviews,
  runCodeReview,
  type CodeReviewDetail,
  type CodeReviewFormData,
  type CodeReviewItem
} from '@/api/codeReview'

const LANGS = ['text', 'python', 'typescript', 'javascript', 'java', 'go', 'rust', 'sql', 'shell']

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('dev:write'))

const tableData = ref<CodeReviewItem[]>([])
const loading = ref(false)

// 新增审查
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive<CodeReviewFormData>({
  repo: '',
  code_content: '',
  branch: '',
  commit: '',
  title: '',
  language: 'text'
})

const rules: FormRules = {
  repo: [{ required: true, message: '请输入仓库', trigger: 'blur' }],
  code_content: [{ required: true, message: '请粘贴待审查代码', trigger: 'blur' }]
}

// AI审查
const reviewingId = ref<number | null>(null)

// 详情
const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref<CodeReviewDetail | null>(null)

function scoreType(score: number): 'success' | 'warning' | 'danger' {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

function severityType(severity: string): 'danger' | 'warning' | 'info' {
  if (severity === 'high') return 'danger'
  if (severity === 'medium') return 'warning'
  return 'info'
}

function severityLabel(severity: string): string {
  const map: Record<string, string> = { high: '严重', medium: '一般', low: '轻微' }
  return map[severity] ?? severity
}

async function loadList() {
  loading.value = true
  try {
    tableData.value = await listCodeReviews()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.repo = ''
  form.code_content = ''
  form.branch = ''
  form.commit = ''
  form.title = ''
  form.language = 'text'
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await createCodeReview({
      repo: form.repo,
      code_content: form.code_content,
      branch: form.branch || undefined,
      commit: form.commit || undefined,
      title: form.title || undefined,
      language: form.language
    })
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadList()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    submitting.value = false
  }
}

async function onReview(row: CodeReviewItem) {
  reviewingId.value = row.id
  try {
    const result = await runCodeReview(row.id)
    if (result.status === 'failed') {
      ElMessage.error('AI审查失败，请检查大模型配置')
    } else {
      ElMessage.success('AI审查完成')
    }
    loadList()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    reviewingId.value = null
  }
}

async function openDetail(row: CodeReviewItem) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detail.value = await getCodeReview(row.id)
  } catch (err) {
    ElMessage.error((err as Error).message)
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

async function onDelete(row: CodeReviewItem) {
  try {
    await ElMessageBox.confirm(`确定删除仓库 "${row.repo}" 的审查记录吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteCodeReview(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 取消
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
.section-title {
  font-weight: 600;
  margin: 16px 0 8px;
  color: var(--el-text-color-primary);
}
.summary {
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.code-block {
  margin: 0;
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  overflow: auto;
  max-height: 300px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
