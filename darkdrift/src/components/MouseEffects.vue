<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/stores/settings'

const store = useSettingsStore()
const { mouseEffect } = storeToRefs(store)

const canvasEl = ref<HTMLCanvasElement | null>(null)

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  gravity: number
  life: number
  maxLife: number
  size: number
  color: string
  rotation: number
  vr: number
  type: 'trail' | 'click'
}

// 多彩星星调色板，保证视觉多样性
const STAR_COLORS = [
  '#ffd700',
  '#ff6b9d',
  '#7c5cff',
  '#5fe3ff',
  '#5eff8f',
  '#ff8c5a',
  '#ff5a8c',
  '#c2a8ff',
  '#ffe066',
  '#66e0c3',
]

let ctx: CanvasRenderingContext2D | null = null
let particles: Particle[] = []
let rafId = 0
let dpr = 1
let lastTrailAt = 0
const MAX_PARTICLES = 240

function resize() {
  const canvas = canvasEl.value
  if (!canvas) return
  dpr = window.devicePixelRatio || 1
  canvas.width = Math.floor(window.innerWidth * dpr)
  canvas.height = Math.floor(window.innerHeight * dpr)
  canvas.style.width = window.innerWidth + 'px'
  canvas.style.height = window.innerHeight + 'px'
  ctx = canvas.getContext('2d')
  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
}

function rand(min: number, max: number) {
  return min + Math.random() * (max - min)
}

function pickColor() {
  return STAR_COLORS[(Math.random() * STAR_COLORS.length) | 0] ?? '#ffd700'
}

/** 在 Canvas 上绘制一颗五角星 */
function drawStar(
  x: number,
  y: number,
  size: number,
  color: string,
  rotation: number,
  alpha: number,
) {
  if (!ctx) return
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(rotation)
  ctx.globalAlpha = alpha
  ctx.fillStyle = color
  ctx.shadowColor = color
  ctx.shadowBlur = size * 0.8
  ctx.beginPath()
  const spikes = 5
  const outer = size
  const inner = size * 0.42
  for (let i = 0; i < spikes * 2; i++) {
    const r = i % 2 === 0 ? outer : inner
    const ang = (Math.PI / spikes) * i - Math.PI / 2
    const px = Math.cos(ang) * r
    const py = Math.sin(ang) * r
    if (i === 0) ctx.moveTo(px, py)
    else ctx.lineTo(px, py)
  }
  ctx.closePath()
  ctx.fill()
  ctx.restore()
}

function spawnTrail(x: number, y: number) {
  if (particles.length > MAX_PARTICLES) return
  particles.push({
    x,
    y,
    vx: rand(-0.4, 0.4),
    vy: rand(-0.6, -0.1), // 微微上飘
    gravity: 0,
    life: 1,
    maxLife: rand(0.6, 0.9),
    size: rand(4, 8),
    color: pickColor(),
    rotation: rand(0, Math.PI * 2),
    vr: rand(-0.08, 0.08),
    type: 'trail',
  })
}

function spawnClickBurst(x: number, y: number) {
  // 每次点击生成 8-12 个随机数量的星星
  const count = 8 + ((Math.random() * 5) | 0)
  for (let i = 0; i < count; i++) {
    const angle = rand(0, Math.PI * 2)
    const speed = rand(2.5, 6)
    particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - rand(1, 3), // 整体偏上抛出
      gravity: 0.18, // 重力，模拟自然掉落
      life: 1,
      maxLife: rand(0.9, 1.4),
      size: rand(7, 13),
      color: pickColor(),
      rotation: rand(0, Math.PI * 2),
      vr: rand(-0.25, 0.25),
      type: 'click',
    })
  }
}

function step() {
  if (!ctx || !canvasEl.value) {
    rafId = 0
    return
  }
  const w = window.innerWidth
  const h = window.innerHeight
  ctx.clearRect(0, 0, w, h)

  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i]
    if (!p) continue
    p.vy += p.gravity
    p.x += p.vx
    p.y += p.vy
    p.rotation += p.vr
    p.life -= 1 / (p.maxLife * 60)
    if (p.life <= 0 || p.y > h + 60 || p.x < -60 || p.x > w + 60) {
      particles.splice(i, 1)
      continue
    }
    const alpha = Math.max(0, Math.min(1, p.life))
    drawStar(p.x, p.y, p.size, p.color, p.rotation, alpha)
  }

  rafId = requestAnimationFrame(step)
}

function startLoop() {
  if (rafId) return
  rafId = requestAnimationFrame(step)
}

function stopLoop() {
  if (rafId) cancelAnimationFrame(rafId)
  rafId = 0
  particles = []
  if (ctx && canvasEl.value) {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)
  }
}

function onMouseMove(e: MouseEvent) {
  if (mouseEffect.value !== 'trail') return
  const now = performance.now()
  if (now - lastTrailAt < 26) return // 节流，避免过度生成
  lastTrailAt = now
  spawnTrail(e.clientX, e.clientY)
}

function onClick(e: MouseEvent) {
  if (mouseEffect.value !== 'click') return
  spawnClickBurst(e.clientX, e.clientY)
}

function onVisibility() {
  if (document.hidden) {
    stopLoop()
  } else if (mouseEffect.value !== 'off') {
    startLoop()
  }
}

watch(
  mouseEffect,
  (val) => {
    if (val === 'off') {
      stopLoop()
    } else {
      startLoop()
    }
  },
  { immediate: false },
)

onMounted(() => {
  resize()
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  window.addEventListener('click', onClick, { passive: true })
  document.addEventListener('visibilitychange', onVisibility)
  if (mouseEffect.value !== 'off') startLoop()
})

onUnmounted(() => {
  stopLoop()
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('click', onClick)
  document.removeEventListener('visibilitychange', onVisibility)
})
</script>

<template>
  <canvas ref="canvasEl" class="mouse-fx-canvas" aria-hidden="true"></canvas>
</template>

<style scoped>
.mouse-fx-canvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9990;
}
</style>
