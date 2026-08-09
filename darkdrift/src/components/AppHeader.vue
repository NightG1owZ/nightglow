<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const { isLoggedIn, nickname, avatar, user } = storeToRefs(userStore)

// 仅当前登录用户 id=1 时显示「文章管理」入口
const canManage = computed(() => !!user.value && user.value.id === 1)

const navItems = [
  { path: '/', label: '首页' },
  { path: '/categories', label: '分类' },
  { path: '/tags', label: '标签' },
  { path: '/about', label: '关于' },
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

function goManager() {
  router.push('/manager')
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
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="user-area">
        <template v-if="isLoggedIn">
          <button v-if="canManage" class="btn btn-primary btn-sm" @click="goManager">
            管理
          </button>
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
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease;
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
  cursor: pointer;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
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
  color: var(--text-secondary);
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--bg-subtle);
  color: var(--accent);
  text-decoration: none;
}

.nav-item.active {
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
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
  border: 2px solid var(--border-light);
}

.avatar-fallback {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.user-nickname {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .header-inner {
    gap: 6px;
    padding: 0 12px;
    height: 56px;
  }

  .logo-text {
    font-size: 15px;
  }

  .nav {
    gap: 2px;
  }

  .nav-item {
    padding: 6px 8px;
    font-size: 13px;
  }

  .user-nickname {
    display: none;
  }
}
</style>
