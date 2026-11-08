<template>
  <el-card shadow="never">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索用户名/邮箱"
        clearable
        style="width: 260px"
        @keyup.enter="onSearch"
        @clear="onSearch"
      />
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="loadList">刷新</el-button>
      <div class="spacer" />
      <el-button
        v-if="canWrite"
        type="success"
        :icon="Plus"
        @click="openCreate"
      >新增用户</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180">
        <template #default="{ row }">
          <span>{{ row.email || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="超管" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_superuser ? 'warning' : 'info'" effect="plain">
            {{ row.is_superuser ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="角色" min-width="120">
        <template #default="{ row }">
          <el-tag v-if="row.role" type="primary" effect="light">{{ row.role.name }}</el-tag>
          <span v-else style="color: var(--el-text-color-secondary)">未分配</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="170">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canWrite" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button
            v-if="canWrite"
            size="small"
            type="danger"
            :disabled="isSelf(row)"
            @click="onDelete(row)"
          >
            删除
          </el-button>
          <span v-if="!canWrite" style="color: var(--el-text-color-secondary)">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadList"
        @size-change="onPageSizeChange"
      />
    </div>
  </el-card>

  <!-- 新增/编辑弹窗 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="480px">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      style="padding-right: 16px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="isEdit" placeholder="3-64 个字符" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          show-password
          :placeholder="isEdit ? '留空则不修改密码' : '6-128 个字符'"
        />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="选填" />
      </el-form-item>
      <el-form-item label="角色" prop="role_id">
        <el-select v-model="form.role_id" placeholder="选择角色" clearable style="width: 100%">
          <el-option
            v-for="r in roles"
            :key="r.id"
            :label="`${r.name}（${r.code}）`"
            :value="r.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="启用状态" prop="is_active">
        <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
      </el-form-item>
      <el-form-item label="超级管理员" prop="is_superuser">
        <el-switch v-model="form.is_superuser" active-text="是" inactive-text="否" />
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
import { Plus, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  createUser,
  deleteUser,
  listUsers,
  updateUser,
  type UserFormData,
  type UserItem
} from '@/api/user'
import { listRoles, type RoleItem } from '@/api/role'

type DialogMode = 'create' | 'edit'

const authStore = useAuthStore()
const canWrite = computed(() => authStore.hasPerm('user:write'))

const tableData = ref<UserItem[]>([])
const roles = ref<RoleItem[]>([])
const total = ref(0)
const loading = ref(false)

const query = reactive({ page: 1, page_size: 10, keyword: '' })

const dialogVisible = ref(false)
const submitting = ref(false)
const mode = ref<DialogMode>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive<UserFormData>({
  username: '',
  password: '',
  email: '',
  is_active: true,
  is_superuser: false,
  role_id: null
})

const isEdit = computed(() => mode.value === 'edit')
const dialogTitle = computed(() => (isEdit.value ? '编辑用户' : '新增用户'))

const rules = computed<FormRules>(() => ({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度为 3-64 个字符', trigger: 'blur' }
  ],
  password: [
    // 新增时必填，编辑时留空表示不修改
    {
      validator: (_rule, value, cb) => {
        if (!isEdit.value && !value) {
          cb(new Error('请输入密码'))
        } else if (value && (value.length < 6 || value.length > 128)) {
          cb(new Error('密码长度为 6-128 个字符'))
        } else {
          cb()
        }
      },
      trigger: 'blur'
    }
  ]
}))

const isSelf = (row: UserItem) => row.id === authStore.user?.id

function formatDate(value: string) {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

async function loadList() {
  loading.value = true
  try {
    const [data, roleList] = await Promise.all([
      listUsers({
        page: query.page,
        page_size: query.page_size,
        keyword: query.keyword || undefined
      }),
      listRoles().catch(() => [])
    ])
    tableData.value = data.list
    total.value = data.total
    roles.value = roleList
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  query.page = 1
  loadList()
}

function onPageSizeChange() {
  query.page = 1
  loadList()
}

function resetForm() {
  form.username = ''
  form.password = ''
  form.email = ''
  form.is_active = true
  form.is_superuser = false
  form.role_id = null
  editingId.value = null
}

function openCreate() {
  mode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: UserItem) {
  mode.value = 'edit'
  editingId.value = row.id
  form.username = row.username
  form.password = ''
  form.email = row.email ?? ''
  form.is_active = row.is_active
  form.is_superuser = row.is_superuser
  form.role_id = row.role?.id ?? null
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value && editingId.value) {
      // 编辑时 password 为空则不提交该字段
      const payload: Partial<UserFormData> = {
        username: form.username,
        email: form.email || undefined,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
        role_id: form.role_id
      }
      if (form.password) payload.password = form.password
      await updateUser(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createUser({
        username: form.username,
        password: form.password,
        email: form.email || undefined,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
        role_id: form.role_id
      })
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

async function onDelete(row: UserItem) {
  try {
    await ElMessageBox.confirm(`确定删除用户 "${row.username}" 吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 取消操作
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
.spacer {
  flex: 1;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
