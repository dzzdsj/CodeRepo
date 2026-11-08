<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="brand">
        <h2>AIDevOps</h2>
        <p>AI赋能研发运维辅助系统</p>
      </div>

      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item v-if="activeTab === 'register'" label="邮箱（选填）" prop="email">
          <el-input v-model="form.email" placeholder="选填" :prefix-icon="Message" />
        </el-form-item>

        <el-button
          type="primary"
          class="submit-btn"
          :loading="loading"
          @click="onSubmit"
        >
          {{ activeTab === 'login' ? '登 录' : '注 册' }}
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Lock, Message, User } from '@element-plus/icons-vue'
import { login, register } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

type Tab = 'login' | 'register'

const activeTab = ref<Tab>('login')
const loading = ref(false)
const formRef = ref<FormInstance>()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '', email: '' })

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度为 3-64 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度为 6-128 个字符', trigger: 'blur' }
  ]
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (activeTab.value === 'login') {
      await authStore.login(form.username, form.password)
      ElMessage.success('登录成功')
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      await register(form.username, form.password, form.email || undefined)
      ElMessage.success('注册成功，请登录')
      activeTab.value = 'login'
    }
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f2a48 0%, #0f172a 100%);
}
.login-card {
  width: 400px;
  padding: 8px 16px 16px;
}
.brand {
  text-align: center;
  margin-bottom: 8px;
}
.brand h2 {
  margin: 0;
  font-size: 28px;
  letter-spacing: 2px;
  color: var(--el-color-primary);
}
.brand p {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.submit-btn {
  width: 100%;
}
</style>
