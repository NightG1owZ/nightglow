<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/user'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  checkPassword: '',
})

const submitting = ref(false)
const error = ref('')
const success = ref('')

async function onSubmit() {
  error.value = ''
  success.value = ''
  if (!form.username.trim()) {
    error.value = '请输入用户名'
    return
  }
  if (form.username.trim().length < 3) {
    error.value = '用户名至少 3 个字符'
    return
  }
  if (!form.password) {
    error.value = '请输入密码'
    return
  }
  if (form.password.length < 8) {
    error.value = '密码至少 8 位'
    return
  }
  if (form.password !== form.checkPassword) {
    error.value = '两次密码输入不一致'
    return
  }
  submitting.value = true
  try {
    await register({
      username: form.username.trim(),
      password: form.password,
      checkPassword: form.checkPassword,
    })
    success.value = '注册成功！即将跳转登录页...'
    setTimeout(() => {
      router.replace({ path: '/login', query: { username: form.username } })
    }, 1200)
  } catch (e: any) {
    error.value = e?.message || '注册失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo">🌙 NightGlow</div>
        <h1 class="auth-title">创建新账号</h1>
        <p class="auth-subtitle">加入我们，开始你的创作之旅</p>
      </div>

      <form class="auth-form" @submit.prevent="onSubmit">
        <div v-if="error" class="form-error">{{ error }}</div>
        <div v-if="success" style="color: #67c23a; font-size: 13px; margin-bottom: 12px">
          ✅ {{ success }}
        </div>

        <div class="form-item">
          <label class="form-label">用户名</label>
          <input
            v-model="form.username"
            class="form-input"
            placeholder="至少 3 个字符"
            autocomplete="username"
          />
        </div>

        <div class="form-item">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="至少 8 位"
            autocomplete="new-password"
          />
        </div>

        <div class="form-item">
          <label class="form-label">确认密码</label>
          <input
            v-model="form.checkPassword"
            type="password"
            class="form-input"
            placeholder="再次输入密码"
            autocomplete="new-password"
            @keyup.enter="onSubmit"
          />
        </div>

        <button class="btn btn-primary btn-block" type="submit" :disabled="submitting">
          {{ submitting ? '注册中...' : '注 册' }}
        </button>
      </form>

      <div class="auth-footer">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
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
  background: linear-gradient(135deg, #fdf2f8 0%, #f8fafc 100%);
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
