<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

const progress = ref(0)
const visible = ref(false)

let rafId: number | null = null

function updateProgress() {
  const scrollTop = window.scrollY || 0
  const docHeight = document.documentElement.scrollHeight
  const viewHeight = window.innerHeight
  const scrollable = docHeight - viewHeight

  if (scrollable <= 0) {
    progress.value = 0
    visible.value = false
    return
  }

  const p = Math.min(1, Math.max(0, scrollTop / scrollable))
  progress.value = p
  visible.value = scrollTop > 4
}

function onScroll() {
  if (rafId !== null) return
  rafId = requestAnimationFrame(() => {
    rafId = null
    updateProgress()
  })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  updateProgress()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  if (rafId !== null) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div class="reading-progress-bar" :class="{ visible }" aria-hidden="true">
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: `${Math.round(progress * 100)}%` }">
        <span class="progress-glow" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.reading-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  z-index: 9999;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.reading-progress-bar.visible {
  opacity: 1;
}

.progress-track {
  width: 100%;
  height: 100%;
  background: var(--border-lighter);
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-hover));
  border-radius: 0 2px 2px 0;
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 0 0 8px rgba(74, 144, 217, 0.5);
}

.progress-glow {
  position: absolute;
  right: 0;
  top: 0;
  width: 24px;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.8),
    transparent
  );
  filter: blur(3px);
  animation: progress-glow 2s ease-in-out infinite;
}

@keyframes progress-glow {
  0%,
  100% {
    opacity: 0.3;
    transform: translateX(-100%);
  }
  50% {
    opacity: 0.8;
    transform: translateX(0%);
  }
}

@media (max-width: 768px) {
  .reading-progress-bar {
    height: 3px;
  }
}
</style>