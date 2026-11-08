<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">AIDevOps</div>
      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :default-openeds="openedMenus"
          router
          class="menu"
          background-color="#001529"
          text-color="#b7c0cd"
          active-text-color="#ffffff"
        >
          <template v-for="item in visibleMenus" :key="item.path">
            <!-- 无子菜单：一级入口 -->
            <el-menu-item v-if="!item.children" :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>

            <!-- 有子菜单：可展开分组 -->
            <el-sub-menu v-else :index="item.path">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon><component :is="child.icon" /></el-icon>
                <span>{{ child.title }}</span>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container>
      <el-header class="header">
        <span class="title">{{ currentTitle }}</span>
        <div class="header-right">
          <el-dropdown @command="onCommand">
            <span class="user">
              <el-icon><UserFilled /></el-icon>
              {{ authStore.username || '用户' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { menus, type MenuItem } from '@/config/menu'
import { useAuthStore } from '@/stores/auth'

// 先声明响应式状态，再声明 computed（避免引用顺序问题）
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 按权限过滤菜单：超管看到全部；普通用户仅看到有权限的子菜单，无子菜单的分组隐藏
const visibleMenus = computed<MenuItem[]>(() => {
  if (authStore.isSuperuser) return menus
  return menus
    .map((item) => {
      if (!item.children) return item
      const children = item.children.filter((c) => !c.permission || authStore.hasPerm(c.permission))
      return children.length ? { ...item, children } : null
    })
    .filter((item): item is MenuItem => item !== null)
})

const activeMenu = computed(() => route.path)

// 进入页面时自动展开当前路由所属的菜单分组
const openedMenus = computed(() =>
  menus
    .filter((item) => item.children?.some((child) => route.path.startsWith(child.path)))
    .map((item) => item.path)
)

const currentTitle = computed(() => (route.meta.title as string) ?? 'AIDevOps 研发运维辅助系统')

function onCommand(command: string) {
  if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.aside {
  background-color: #001529;
  overflow-x: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.menu {
  border-right: none;
}
.menu:not(.el-menu--collapse) {
  width: 220px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.user {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  outline: none;
}
.main {
  background-color: var(--el-fill-color-light);
  padding: 16px;
}
</style>
