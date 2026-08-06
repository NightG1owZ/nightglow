<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <div class="app-layout">
    <AppHeader />
    <main class="main">
      <div class="container main-inner">
        <div class="content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
        <aside class="sidebar hide-sm">
          <slot name="sidebar">
            <div class="card sidebar-card">
              <h3 class="sidebar-title">🌙 NightGlow</h3>
              <p class="sidebar-desc">
                欢迎访问我的个人博客，这里会分享技术文章与生活感悟。
              </p>
            </div>
          </slot>
        </aside>
      </div>
    </main>
    <footer class="site-footer">
      <div class="container footer-inner">
        <p>© 2026 NightGlow Blog · Built with Vue & FastAPI</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main {
  flex: 1;
  padding: 24px 0;
}

.main-inner {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.content {
  flex: 1;
  min-width: 0;
}

.sidebar {
  width: 300px;
  flex-shrink: 0;
}

.sidebar-card {
  position: sticky;
  top: 88px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.sidebar-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.site-footer {
  background: var(--bg-header);
  border-top: 1px solid var(--border-light);
  padding: 20px 0;
  margin-top: auto;
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease;
}

.footer-inner {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 992px) {
  .sidebar {
    width: 260px;
  }
}

@media (max-width: 768px) {
  .main {
    padding: 16px 0;
  }

  .main-inner {
    flex-direction: column;
    gap: 16px;
  }

  .sidebar {
    width: 100%;
  }

  .sidebar-card {
    position: static;
  }
}
</style>
