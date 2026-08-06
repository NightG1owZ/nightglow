<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="notfound">
    <div class="notfound-card">
      <div class="notfound-code">404</div>
      <h1 class="notfound-title">页面走丢了 🌙</h1>
      <p class="notfound-desc">你访问的页面不存在，或者已被移除。</p>
      <div class="flex gap-12 justify-center mt-24">
        <button class="btn btn-primary" @click="router.push('/')">返回首页</button>
        <button class="btn btn-outline" @click="router.back()">返回上一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notfound {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, var(--bg-404-grad-1) 0%, var(--bg-404-grad-2) 100%);
  transition: background 0.4s ease;
}

.notfound-card {
  text-align: center;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 60px 48px;
  box-shadow: var(--shadow-auth);
  border: 1px solid var(--border-lighter);
}

.notfound-code {
  font-size: 96px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--accent), #8e6ddc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 20px;
}

.notfound-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.notfound-desc {
  font-size: 14px;
  color: var(--text-tertiary);
}
</style>
