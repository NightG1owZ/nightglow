<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  /** 是否显示返回顶部按钮 */
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'go-top'): void
}>()

/** 按钮按下态，用于提供点击反馈 */
const pressed = ref(false)
/** 滚动过程中的「显示/隐藏」只做 CSS 过渡，卸载时直接跳变避免动画残留 */
const mounted = ref(true)

function handleClick() {
  pressed.value = true
  setTimeout(() => (pressed.value = false), 180)
  emit('go-top')
}

// 提示快捷键：Ctrl / ⌘ + Shift + ↑
const tooltipVisible = ref(false)
let tipTimer: ReturnType<typeof setTimeout> | null = null

function showTooltip() {
  tooltipVisible.value = true
  if (tipTimer) clearTimeout(tipTimer)
  tipTimer = setTimeout(() => (tooltipVisible.value = false), 1800)
}

watch(
  () => props.visible,
  (v) => {
    if (v) showTooltip()
  },
  { once: true },
)

import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  mounted.value = false
  if (tipTimer) clearTimeout(tipTimer)
})
</script>

<template>
  <transition name="btt-fade">
    <button
      v-if="mounted && visible"
      type="button"
      class="back-to-top"
      :class="{ pressed }"
      :title="'返回顶部 ( Ctrl / ⌘ + Shift + ↑ )'"
      aria-label="返回顶部"
      @click="handleClick"
    >
      <span class="btt-icon">↑</span>
      <transition name="btt-tip">
        <span v-if="tooltipVisible" class="btt-tooltip">
          Ctrl/⌘ + Shift + ↑
        </span>
      </transition>
    </button>
  </transition>
</template>

<style scoped>
.back-to-top {
  position: fixed;
  right: 20px;
  bottom: 64px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--border-base);
  background: var(--bg-card);
  color: var(--accent);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-card);
  z-index: 50;
  transition:
    transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1),
    background-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease;
}

.back-to-top:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  box-shadow: var(--shadow-hover);
  transform: translateY(-3px);
}

.back-to-top.pressed {
  transform: translateY(0) scale(0.94);
}

.btt-icon {
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.btt-tooltip {
  position: absolute;
  right: 52px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--text-primary);
  color: var(--bg-card);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: var(--shadow-card);
}

.btt-tooltip::after {
  content: '';
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%) rotate(45deg);
  width: 8px;
  height: 8px;
  background: var(--text-primary);
}

.btt-fade-enter-active,
.btt-fade-leave-active {
  transition:
    opacity 0.28s ease,
    transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.btt-fade-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.92);
}
.btt-fade-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.92);
}

.btt-tip-enter-active,
.btt-tip-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.btt-tip-enter-from,
.btt-tip-leave-to {
  opacity: 0;
  transform: translate(6px, -50%);
}

@media (min-width: 1024px) {
  .back-to-top {
    right: 32px;
    bottom: 80px;
    width: 48px;
    height: 48px;
  }
  .btt-icon {
    font-size: 20px;
  }
}
</style>
