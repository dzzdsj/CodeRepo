import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import { ElMessage } from 'element-plus'
import { menus } from '@/config/menu'
import MainLayout from '@/layouts/MainLayout.vue'
import PagePlaceholder from '@/components/PagePlaceholder.vue'
import { useAuthStore } from '@/stores/auth'

// 已实现真实页面的菜单项：路径 -> 组件；未列出的菜单项使用占位组件
const realComponents: Record<string, Component> = {
  '/system/user': () => import('@/views/system/UserManagement.vue'),
  '/system/role': () => import('@/views/system/RoleManagement.vue'),
  '/dev/code-review': () => import('@/views/dev/CodeReview.vue'),
  '/ai/model': () => import('@/views/ai/ModelManagement.vue'),
  '/ai/prompt': () => import('@/views/ai/PromptTemplateManagement.vue'),
  '/ai/knowledge': () => import('@/views/ai/KnowledgeBase.vue')
}

// 由菜单配置自动生成各模块的占位页路由（父级重定向到第一个子菜单）
const moduleRoutes: RouteRecordRaw[] = menus
  .filter((item) => item.children?.length)
  .map((item) => ({
    path: item.path,
    redirect: item.children![0].path,
    children: item.children!.map((child) => ({
      path: child.path,
      name: child.path.slice(1).replaceAll('/', '-'),
      component: realComponents[child.path] ?? PagePlaceholder,
      meta: { title: child.title, icon: child.icon, permission: child.permission }
    }))
  }))

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      ...moduleRoutes
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 登录守卫 + 权限守卫
router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (to.meta.public) {
    return true
  }
  if (!authStore.isLoggedIn) {
    return {
      path: '/login',
      query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined
    }
  }
  if (!authStore.user) {
    await authStore.loadUser()
  }
  // 权限校验：超管放行
  const perm = to.meta.permission as string | undefined
  if (perm && !authStore.isSuperuser && !authStore.permissions.includes(perm)) {
    ElMessage.error('无访问权限')
    return { path: '/' }
  }
  return true
})

export default router
