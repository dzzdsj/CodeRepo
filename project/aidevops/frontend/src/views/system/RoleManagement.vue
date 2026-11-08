<template>
  <el-card shadow="never">
    <div class="toolbar">
      <span class="tip">共 {{ tableData.length }} 个角色</span>
      <div class="spacer" />
      <el-button type="success" :icon="Plus" v-if="canWrite" @click="openCreate">
        新增角色
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="name" label="角色名称" min-width="140" />
      <el-table-column prop="code" label="编码" min-width="120" />
      <el-table-column prop="description" label="描述" min-width="180">
        <template #default="{ row }">{{ row.description || '-' }}</template>
      </el-table-column>
      <el-table-column label="默认" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="warning" size="small">默认</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="权限数" width="90">
        <template #default="{ row }">{{ row.permissions.length }}</template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
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

  <!-- 新增/编辑弹窗 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" style="padding-right: 16px">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="编码" prop="code">
        <el-input v-model="form.code" :disabled="isEdit" placeholder="创建后不可修改" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="2" placeholder="选填" />
      </el-form-item>
      <el-form-item label="权限" prop="permissions">
        <div class="perm-groups">
          <div v-for="(perms, group) in PERMISSION_GROUPS" :key="group" class="perm-group">
            <div class="perm-group-title">{{ group }}</div>
            <el-checkbox-group v-model="form.permissions">
              <el-checkbox
                v-for="p in perms"
                :key="p"
                :value="p"
                :label="p"
              >
                {{ PERMISSIONS[p] }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { PERMISSIONS, PERMISSION_GROUPS } from '@/config/permissions'
import { useAuthStore } from '@/stores/auth'
import {
  createRole,
  deleteRole,
  listRoles,
  updateRole,
  type RoleFormData,
  type RoleItem
} from '@/api/role'

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('role:write'))

const tableData = ref<RoleItem[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const submitting = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<RoleFormData>({
  name: '',
  code: '',
  description: '',
  permissions: []
})

const isEdit = computed(() => mode.value === 'edit')
const dialogTitle = computed(() => (isEdit.value ? '编辑角色' : '新增角色'))

const rules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

function formatDate(value: string) {
  return value ? value.replace('T', ' ').slice(0, 19) : '-'
}

async function loadList() {
  loading.value = true
  try {
    tableData.value = await listRoles()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.code = ''
  form.description = ''
  form.permissions = []
  editingId.value = null
}

function openCreate() {
  mode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: RoleItem) {
  mode.value = 'edit'
  editingId.value = row.id
  form.name = row.name
  form.code = row.code
  form.description = row.description ?? ''
  form.permissions = [...row.permissions]
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateRole(editingId.value, {
        name: form.name,
        description: form.description || undefined,
        permissions: form.permissions
      })
      ElMessage.success('更新成功')
    } else {
      await createRole({ ...form })
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

async function onDelete(row: RoleItem) {
  try {
    await ElMessageBox.confirm(`确定删除角色 "${row.name}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteRole(row.id)
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
.perm-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}
.perm-group-title {
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--el-text-color-primary);
}
.perm-group :deep(.el-checkbox) {
  margin-right: 18px;
}
</style>
