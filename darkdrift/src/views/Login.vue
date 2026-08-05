<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { loading } = storeToRefs(userStore)

const form = reactive({
  username: '',
  password: '',
})

const error = ref('')

async function onSubmit() {
  error.value = ''
  if (!form.username.trim()) {
    error.value = '请输入用户名'
    return
  }
  if (!form.password) {
    error.value = '请输入密码'
    return
  }
  try {
    await userStore.login({
      username: form.username.trim(),
      password: form.password,
    })
    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (e: any) {
    error.value = e?.message || '登录失败'
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">🌙 NightGlow</div>
        <h1 class="auth-title">欢迎回来</h1>
        <p class="auth-subtitle">登录以继续访问博客管理功能</p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <div v-if="error" class="form-error">{{ error }}</div>

        <div class="form-item">
          <label class="form-label">用户名</label>
          <input
            v-model="form.username"
            class="form-input"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>

        <div class="form-item">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="请输入密码"
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          />
        </div>

        <button class="btn btn-primary btn-block" type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="auth-footer">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
        <span class="divider">·</span>
        <router-link to="/">返回首页</router-link>
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
  background: linear-gradient(135deg, #eef4fb 0%, #f8fafc 100%);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.auth-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: #4a90d9;
  margin-bottom: 16px;
}

.auth-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2d3d;
  margin-bottom: 6px;
}

.auth-subtitle {
  font-size: 13px;
  color: #909399;
}

.btn-block {
  width: 100%;
  height: 40px;
  font-size: 15px;
  margin-top: 8px;
}

.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: #606266;
}

.auth-footer .divider {
  margin: 0 6px;
  color: #dcdfe6;
}
</style>
