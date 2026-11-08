import type { Directive } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * v-permission="'user:write'" 或 v-permission="['user:write','role:write']"
 * 不满足权限时移除该元素。
 */
export const permission: Directive<HTMLElement, string | string[]> = {
  mounted(el, binding) {
    const auth = useAuthStore()
    const value = binding.value
    const perms = Array.isArray(value) ? value : [value]
    const ok = auth.isSuperuser || perms.some((p) => auth.permissions.includes(p))
    if (!ok) {
      el.parentNode?.removeChild(el)
    }
  }
}
