<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore, type ThemeMode, type MouseEffect } from '@/stores/settings'

const store = useSettingsStore()
const { theme, mouseEffect } = storeToRefs(store)

const open = ref(false)

// 优先级顺序：系统默认 > 白天 > 黑夜 > 护眼
const themeOptions: { key: ThemeMode; label: string; icon: string }[] = [
  { key: 'system', label: '跟随系统', icon: 'monitor' },
  { key: 'light', label: '白天', icon: 'sun' },
  { key: 'dark', label: '黑夜', icon: 'moon' },
  { key: 'eye-care', label: '护眼', icon: 'leaf' },
]

const effectOptions: { key: MouseEffect; label: string; icon: string }[] = [
  { key: 'trail', label: '星星拖尾', icon: 'trail' },
  { key: 'click', label: '点击散花', icon: 'click' },
  { key: 'off', label: '关闭特效', icon: 'off' },
]
</script>

<template>
  <div class="control-panel" :class="{ open }">
    <transition name="panel-pop">
      <div v-if="open" class="panel-body">
        <!-- 主题选择器 -->
        <div class="selector selector-theme">
          <div class="selector-label">主题</div>
          <div class="option-row">
            <button
              v-for="opt in themeOptions"
              :key="opt.key"
              class="option-btn"
              :class="{ active: theme === opt.key }"
              :title="opt.label"
              :aria-label="opt.label"
              :aria-pressed="theme === opt.key"
              @click="store.setTheme(opt.key)"
            >
              <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  v-if="opt.icon === 'sun'"
                  d="M12 7a5 5 0 100 10 5 5 0 000-10zm0-5a1 1 0 011 1v2a1 1 0 11-2 0V3a1 1 0 011-1zm0 17a1 1 0 011 1v2a1 1 0 11-2 0v-2a1 1 0 011-1zM4.2 4.2a1 1 0 011.4 0l1.5 1.5a1 1 0 11-1.4 1.4L4.2 5.6a1 1 0 010-1.4zm12.7 12.7a1 1 0 011.4 0l1.5 1.5a1 1 0 01-1.4 1.4l-1.5-1.5a1 1 0 010-1.4zM2 12a1 1 0 011-1h2a1 1 0 110 2H3a1 1 0 01-1-1zm17 0a1 1 0 011-1h2a1 1 0 110 2h-2a1 1 0 01-1-1zM4.2 19.8a1 1 0 010-1.4l1.5-1.5a1 1 0 11 1.4 1.4l-1.5 1.5a1 1 0 01-1.4 0zm12.7-12.7a1 1 0 010-1.4l1.5-1.5a1 1 0 111.4 1.4l-1.5 1.5a1 1 0 01-1.4 0z"
                />
                <path
                  v-else-if="opt.icon === 'moon'"
                  d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"
                />
                <path
                  v-else-if="opt.icon === 'monitor'"
                  d="M4 4h16a1 1 0 011 1v10a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1zm1 2v8h14V6H5zm5 12h4l1 2H9l1-2z"
                />
                <path
                  v-else-if="opt.icon === 'leaf'"
                  d="M5 20c0-7 5-12 14-13 0 9-5 14-12 14H5v-1zm3.5-3.5c4-1 6.5-3.7 7.3-7.3-3.6.8-6.3 3.3-7.3 7.3z"
                />
              </svg>
              <span class="option-text">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <!-- 鼠标特效选择器 -->
        <div class="selector selector-effect">
          <div class="selector-label">鼠标特效</div>
          <div class="option-row">
            <button
              v-for="opt in effectOptions"
              :key="opt.key"
              class="option-btn"
              :class="{ active: mouseEffect === opt.key }"
              :title="opt.label"
              :aria-label="opt.label"
              :aria-pressed="mouseEffect === opt.key"
              @click="store.setMouseEffect(opt.key)"
            >
              <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  v-if="opt.icon === 'trail'"
                  d="M12 2l2.4 5.6L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.6-1.4L12 2z"
                />
                <path
                  v-else-if="opt.icon === 'click'"
                  d="M9 2l1.8 4.2L15 8l-4 1.8L9 14l-1.8-4.2L3 8l4.2-1.8L9 2zm7 9l1.2 2.8L20 15l-2.8 1.2L16 19l-1.2-2.8L12 15l2.8-1.2L16 11z"
                />
                <path
                  v-else
                  d="M6 6l12 12M18 6L6 18"
                  stroke="currentColor"
                  stroke-width="2"
                  fill="none"
                  stroke-linecap="round"
                />
              </svg>
              <span class="option-text">{{ opt.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <button
      class="toggle-btn"
      :class="{ active: open }"
      :aria-label="open ? '收起控制面板' : '展开控制面板'"
      :aria-expanded="open"
      @click="open = !open"
    >
      <svg class="toggle-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path
          d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 2a8 8 0 010 16V4zm-7.5 7h3a14 14 0 011.2-5.3A8 8 0 004.5 13zm0-2a8 8 0 014.2-5.3A14 14 0 019.5 11h-5zm7.5 9v-5h-2.6A12 12 0 0012 20zm0-7h2.6A12 12 0 0012 8v5zm0-7v5h2.6A12 12 0 0012 6z"
        />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.control-panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 10000;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  --panel-bg: color-mix(in srgb, var(--bg-card) 88%, transparent);
}

.panel-body {
  display: flex;
  align-items: stretch;
  gap: 8px;
  padding: 10px;
  border-radius: 14px;
  background: var(--panel-bg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-hover);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.selector {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.selector-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  letter-spacing: 0.5px;
  padding: 0 2px;
}

.option-row {
  display: flex;
  gap: 4px;
}

.option-btn {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 6px 8px;
  min-width: 48px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  background: var(--bg-subtle);
  color: var(--text-secondary);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    transform 0.15s ease;
}

.option-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  transform: translateY(-1px);
}

.option-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 40%, transparent);
}

.icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.option-text {
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

.toggle-btn {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-light);
  border-radius: 50%;
  background: var(--panel-bg);
  color: var(--accent);
  cursor: pointer;
  box-shadow: var(--shadow-hover);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition:
    transform 0.25s ease,
    background-color 0.2s ease,
    color 0.2s ease;
}

.toggle-btn:hover {
  transform: rotate(45deg) scale(1.05);
}

.toggle-btn.active {
  background: var(--accent);
  color: #fff;
  transform: rotate(45deg);
}

.toggle-icon {
  width: 22px;
  height: 22px;
  fill: currentColor;
}

.panel-pop-enter-active,
.panel-pop-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.22s ease;
}

.panel-pop-enter-from,
.panel-pop-leave-to {
  opacity: 0;
  transform: translateX(8px) scale(0.96);
}

@media (max-width: 480px) {
  .control-panel {
    right: 12px;
    bottom: 12px;
  }

  .option-btn {
    min-width: 42px;
    padding: 5px 6px;
  }

  .option-text {
    font-size: 9px;
  }
}
</style>
