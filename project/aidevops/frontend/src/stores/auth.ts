import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { clearToken, getToken, setToken } from '@/api/request'
import { fetchMe, login as loginApi, type UserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getToken())
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isSuperuser = computed(() => !!user.value?.is_superuser)
  const username = computed(() => user.value?.username ?? '')
  const permissions = computed<string[]>(() => user.value?.permissions ?? [])

  /** 单一权限判定：超管放行，否则检查权限列表 */
  function hasPerm(perm: string): boolean {
    if (isSuperuser.value) return true
    return permissions.value.includes(perm)
  }

  function hasAnyPerm(...perms: string[]): boolean {
    if (isSuperuser.value) return true
    return perms.some((p) => permissions.value.includes(p))
  }

  async function login(username: string, password: string) {
    const result = await loginApi(username, password)
    token.value = result.access_token
    user.value = result.user
    setToken(result.access_token)
  }

  /** 刷新页面后用 token 拉取用户信息 */
  async function loadUser() {
    if (!token.value) return
    try {
      user.value = await fetchMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    clearToken()
  }

  return {
    token,
    user,
    isLoggedIn,
    isSuperuser,
    username,
    permissions,
    hasPerm,
    hasAnyPerm,
    login,
    loadUser,
    logout
  }
})
