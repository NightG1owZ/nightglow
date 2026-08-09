<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { TocItem } from '@/composables/useTableOfContents'

interface Props {
  items: TocItem[]
  activeId: string | null
  /** 为 null 表示不显示（文章没有任何标题） */
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'jump', id: string): void
}>()

const mobileOpen = ref(false)
const scrollerRef = ref<HTMLElement | null>(null)

/**
 * 点击目录项：通知父组件平滑滚动，移动端关闭抽屉。
 */
function handleJump(id: string) {
  emit('jump', id)
  mobileOpen.value = false
}

/**
 * 激活态变化时，将当前条目滚动到侧边栏可视区中央。
 * 这使用容器的 scrollIntoView 而不是整页滚动，避免干扰文章滚动。
 */
watch(
  () => props.activeId,
  async (id) => {
    if (!id || !props.visible) return
    await nextTick()
    const el = scrollerRef.value?.querySelector<HTMLElement>(`[data-toc-id="${id}"]`)
    if (el && scrollerRef.value) {
      const c = scrollerRef.value
      const elTop = el.offsetTop
      const elBottom = elTop + el.offsetHeight
      const viewTop = c.scrollTop
      const viewBottom = viewTop + c.clientHeight
      if (elTop < viewTop + 8 || elBottom > viewBottom - 8) {
        const target = Math.max(0, elTop - c.clientHeight / 2 + el.offsetHeight / 2)
        c.scrollTo({ top: target, behavior: 'smooth' })
      }
    }
  },
)

// 抽屉打开/关闭时禁止 body 滚动，避免移动端双滚动冲突
watch(mobileOpen, (v) => {
  if (typeof document === 'undefined') return
  document.body.style.overflow = v ? 'hidden' : ''
})
</script>

<template>
  <aside v-if="visible" class="toc">
    <!-- 桌面端：固定侧边栏 -->
    <div class="toc-desktop card">
      <div class="toc-header">
        <span class="toc-icon">📑</span>
        <span class="toc-title">目录</span>
      </div>
      <div ref="scrollerRef" class="toc-list">
        <button
          v-for="item in items"
          :key="item.id"
          type="button"
          :data-toc-id="item.id"
          class="toc-item"
          :class="{ active: activeId === item.id }"
          :style="{ paddingLeft: 8 + (item.level - 1) * 12 + 'px' }"
          :title="item.text"
          @click="handleJump(item.id)"
        >
          <span class="toc-bullet" />
          <span class="toc-text">{{ item.text }}</span>
        </button>
      </div>
    </div>

    <!-- 移动端：悬浮触发按钮 + 抽屉 -->
    <button class="toc-mobile-fab" type="button" title="目录" @click="mobileOpen = true">
      📑
    </button>

    <div
      v-if="mobileOpen"
      class="toc-mobile-mask"
      @click.self="mobileOpen = false"
      @keyup.esc="mobileOpen = false"
    >
      <div class="toc-mobile-drawer card" role="dialog" aria-label="文章目录">
        <div class="toc-header">
          <span class="toc-icon">📑</span>
          <span class="toc-title">目录</span>
          <button class="toc-close" type="button" title="关闭" @click="mobileOpen = false">
            ×
          </button>
        </div>
        <div ref="scrollerRef" class="toc-list">
          <button
            v-for="item in items"
            :key="item.id"
            type="button"
            :data-toc-id="item.id"
            class="toc-item"
            :class="{ active: activeId === item.id }"
            :style="{ paddingLeft: 8 + (item.level - 1) * 12 + 'px' }"
            :title="item.text"
            @click="handleJump(item.id)"
          >
            <span class="toc-bullet" />
            <span class="toc-text">{{ item.text }}</span>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ========== 公共样式 ========== */
.toc-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 4px 12px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--border-lighter);
}

.toc-icon {
  font-size: 14px;
}

.toc-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.toc-list {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 100%;
}

.toc-list::-webkit-scrollbar {
  width: 6px;
}
.toc-list::-webkit-scrollbar-thumb {
  background: var(--border-base);
  border-radius: 3px;
}

.toc-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.45;
  text-align: left;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    color 0.2s ease,
    padding-left 0.2s ease;
  word-break: break-word;
  position: relative;
}

.toc-item:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.toc-item.active {
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 500;
}

.toc-item.active .toc-bullet {
  background: var(--accent);
  transform: scale(1.4);
}

.toc-bullet {
  flex-shrink: 0;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--border-base);
  transition:
    background-color 0.2s ease,
    transform 0.2s ease;
}

.toc-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ========== 桌面端侧边栏（>= 768px 显示） ========== */
.toc-desktop {
  display: none;
  position: sticky;
  top: 80px;
  width: 100%;
  padding: 20px 16px;
  max-height: calc(100vh - 120px);
  overflow: hidden;
  flex-direction: column;
}

@media (min-width: 768px) {
  .toc-desktop {
    display: flex;
  }
}

/* ========== 移动端浮标 + 抽屉（< 768px 启用） ========== */
.toc-mobile-fab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  right: 16px;
  bottom: 120px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--border-base);
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
  box-shadow: var(--shadow-card);
  z-index: 40;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease;
}

.toc-mobile-fab:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background: var(--accent-bg);
  color: var(--accent);
}

@media (min-width: 768px) {
  .toc-mobile-fab {
    display: none;
  }
}

.toc-mobile-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 80;
  display: flex;
  justify-content: flex-end;
  animation: toc-fade-in 0.2s ease;
}

@keyframes toc-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.toc-mobile-drawer {
  width: min(78vw, 320px);
  height: 100vh;
  padding: 20px 16px;
  border-radius: 0;
  box-shadow: var(--shadow-hover);
  display: flex;
  flex-direction: column;
  animation: toc-slide-in 0.25s ease;
}

@keyframes toc-slide-in {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}

.toc-close {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 22px;
  line-height: 1;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.toc-close:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

@media (min-width: 768px) {
  .toc-mobile-mask {
    display: none;
  }
}
</style>
