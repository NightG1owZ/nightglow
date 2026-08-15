import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { LoginUserVO } from '@/types'
import { login as apiLogin, logout as apiLogout, getCurrentUser, wechatLogin as apiWechatLogin } from '@/api/user'
import type { UserLoginRequest } from '@/types'

const STORAGE_KEY = 'blog_user'

function loadFromStorage(): LoginUserVO | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as LoginUserVO) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const user = ref<LoginUserVO | null>(loadFromStorage())
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const nickname = computed(() => user.value?.nickname || user.value?.username || '未登录')
  const avatar = computed(() => user.value?.avatar || '')

  function saveUser(u: LoginUserVO | null) {
    user.value = u
    if (u) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(u))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function login(payload: UserLoginRequest) {
    loading.value = true
    try {
      const res = await apiLogin(payload)
      saveUser(res)
      return res
    } finally {
      loading.value = false
    }
  }

  async function loginWithWechat(code: string) {
    loading.value = true
    try {
      const res = await apiWechatLogin({ code })
      saveUser(res)
      return res
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await apiLogout()
    } finally {
      saveUser(null)
    }
  }

  async function fetchCurrentUser() {
    try {
      const res = await getCurrentUser()
      saveUser(res)
      return res
    } catch {
      saveUser(null)
      return null
    }
  }

  return {
    user,
    loading,
    isLoggedIn,
    nickname,
    avatar,
    login,
    loginWithWechat,
    logout,
    fetchCurrentUser,
  }
})
