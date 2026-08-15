<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const code = route.query.code as string | undefined
  const state = (route.query.state as string | undefined) || '/'
  if (!code) {
    error.value = '缺少微信授权码，请重新登录'
    loading.value = false
    return
  }
  try {
    await userStore.loginWithWechat(code)
    const target = state.startsWith('/') && !state.startsWith('//') ? state : '/'
    router.replace(target)
  } catch (e: any) {
    error.value = e?.message || '微信登录失败'
    loading.value = false
  }
})
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">🌙 NightGlow</div>
        <h1 class="auth-title">微信登录</h1>
      </div>

      <div v-if="loading" class="loading">正在登录...</div>
      <div v-else class="callback-error">
        <p>⚠️ {{ error }}</p>
        <div class="actions">
          <router-link class="btn btn-primary" to="/login">账号登录</router-link>
          <router-link class="btn btn-outline" to="/">返回首页</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, var(--bg-auth-grad-1) 0%, var(--bg-auth-grad-2) 100%);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: var(--shadow-auth);
  border: 1px solid var(--border-lighter);
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 12px;
}

.auth-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.loading {
  text-align: center;
  padding: 24px 0;
  color: var(--text-tertiary);
}

.callback-error {
  text-align: center;
  color: var(--danger);
  font-size: 14px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}
</style>
