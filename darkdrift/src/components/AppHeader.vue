<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { isLoggedIn, nickname, avatar } = storeToRefs(userStore)

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/categories', label: '分类', icon: '📁' },
  { path: '/tags', label: '标签', icon: '🏷️' },
  { path: '/about', label: '关于', icon: 'ℹ️' },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function goLogin() {
  router.push('/login')
}

function goRegister() {
  router.push('/register')
}

async function handleLogout() {
  await userStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <div class="logo" @click="router.push('/')">
        <span class="logo-icon">🌙</span>
        <span class="logo-text">NightGlow Blog</span>
      </div>

      <nav class="nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="user-area">
        <template v-if="isLoggedIn">
          <div class="user-info">
            <img v-if="avatar" :src="avatar" class="avatar" alt="avatar" />
            <div v-else class="avatar-fallback">{{ nickname.slice(0, 1) }}</div>
            <span class="user-nickname">{{ nickname }}</span>
          </div>
          <button class="btn btn-outline btn-sm" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <button class="btn btn-outline btn-sm" @click="goLogin">登录</button>
          <button class="btn btn-primary btn-sm" @click="goRegister">注册</button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: 0.5px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.nav-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 14px;
  color: #606266;
  transition: all 0.2s ease;
  text-decoration: none;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #4a90d9;
  text-decoration: none;
}

.nav-item.active {
  background: #ecf5ff;
  color: #4a90d9;
  font-weight: 500;
}

.nav-icon {
  font-size: 14px;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 4px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ebeef5;
}

.avatar-fallback {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4a90d9, #67a7e0);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.user-nickname {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .header-inner {
    gap: 8px;
    padding: 0 12px;
    height: 56px;
  }

  .logo-text {
    display: none;
  }

  .nav-label {
    display: none;
  }

  .nav-item {
    padding: 6px 10px;
  }

  .user-nickname {
    display: none;
  }
}
</style>
