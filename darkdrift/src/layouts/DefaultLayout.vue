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
  display: block;
}

.content {
  width: 100%;
  min-width: 0;
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

@media (max-width: 768px) {
  .main {
    padding: 16px 0;
  }
}
</style>
