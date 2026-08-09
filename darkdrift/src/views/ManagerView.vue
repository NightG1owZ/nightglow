<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import ArticleCreate from '@/views/ArticleCreate.vue'
import ArticleManager from '@/components/manager/ArticleManager.vue'
import TagManager from '@/components/manager/TagManager.vue'

const router = useRouter()
const userStore = useUserStore()
const { isLoggedIn, nickname, avatar } = storeToRefs(userStore)

type TabKey = 'create' | 'articles' | 'tags'

const activeTab = ref<TabKey>('create')

const tabs = [
  { key: 'create' as TabKey, label: '新增文章', icon: '✍️' },
  { key: 'articles' as TabKey, label: '文章管理', icon: '📚' },
  { key: 'tags' as TabKey, label: '标签管理', icon: '🏷️' },
]

// 新增文章成功后切换到文章管理
function onCreateSuccess(articleId: number, status: number) {
  activeTab.value = 'articles'
  // 提示信息由 ArticleManager 内部处理，这里可扩展
  void articleId
  void status
}

function goHome() {
  router.push('/')
}

const currentUserName = computed(() => nickname.value)
</script>

<template>
  <div class="manager-layout">
    <!-- 独立头部：仅保留 Logo + 返回首页 + 用户信息，隐藏主导航 -->
    <header class="manager-header">
      <div class="container header-inner">
        <div class="header-left">
          <button class="btn btn-outline btn-sm" @click="goHome">
            ← 返回首页
          </button>
          <div class="brand">
            <span class="brand-icon">🛠️</span>
            <span class="brand-text">文章管理后台</span>
          </div>
        </div>
        <div class="header-right">
          <div v-if="isLoggedIn" class="user-info">
            <img v-if="avatar" :src="avatar" class="avatar" alt="avatar" />
            <div v-else class="avatar-fallback">{{ currentUserName.slice(0, 1) }}</div>
            <span class="user-nickname">{{ currentUserName }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 标签页导航 -->
    <nav class="tab-nav">
      <div class="container tab-inner">
        <button
          v-for="t in tabs"
          :key="t.key"
          class="tab-item"
          :class="{ active: activeTab === t.key }"
          @click="activeTab = t.key"
        >
          <span class="tab-icon">{{ t.icon }}</span>
          <span class="tab-label">{{ t.label }}</span>
        </button>
      </div>
    </nav>

    <!-- 内容区 -->
    <main class="main">
      <div class="container main-inner">
        <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'create'" key="create" class="tab-panel">
            <ArticleCreate embedded @success="onCreateSuccess" />
          </div>
          <div v-else-if="activeTab === 'articles'" key="articles" class="tab-panel">
            <ArticleManager />
          </div>
          <div v-else key="tags" class="tab-panel">
            <TagManager />
          </div>
        </transition>
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <p>© 2026 NightGlow Blog · 管理后台</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.manager-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-page);
}

.manager-header {
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  font-size: 20px;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
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
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tab-nav {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 64px;
  z-index: 90;
}

.tab-inner {
  display: flex;
  gap: 4px;
  padding: 0 16px;
  overflow-x: auto;
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 12px 18px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition:
    color 0.2s ease,
    border-color 0.2s ease,
    background-color 0.2s ease;
}

.tab-item:hover {
  color: var(--accent);
  background: var(--bg-subtle);
}

.tab-item.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.tab-icon {
  font-size: 14px;
}

.main {
  flex: 1;
  padding: 24px 0;
}

.main-inner {
  width: 100%;
}

.tab-panel {
  width: 100%;
}

.site-footer {
  background: var(--bg-header);
  border-top: 1px solid var(--border-light);
  padding: 16px 0;
  margin-top: auto;
}

.footer-inner {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .header-inner {
    height: 56px;
    gap: 8px;
    padding: 0 12px;
  }

  .brand-text {
    display: none;
  }

  .user-nickname {
    display: none;
  }

  .tab-inner {
    padding: 0 12px;
  }

  .tab-item {
    padding: 10px 14px;
  }

  .main {
    padding: 16px 0;
  }
}
</style>
