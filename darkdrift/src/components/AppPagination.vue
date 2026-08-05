<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: number
  pageSize: number
  total: number
}>()

const emit = defineEmits<{
  (e: 'change', page: number): void
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const pages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const cur = props.current
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 4) pages.push('...')
    const start = Math.max(2, cur - 2)
    const end = Math.min(total - 1, cur + 2)
    for (let i = start; i <= end; i++) pages.push(i)
    if (cur < total - 3) pages.push('...')
    pages.push(total)
  }
  return pages
})

function jumpTo(page: number | string) {
  if (typeof page !== 'number' || page < 1 || page > totalPages.value) return
  if (page === props.current) return
  emit('change', page)
}
</script>

<template>
  <div class="pagination" v-if="total > 0">
    <button class="pagination-btn" :disabled="current <= 1" @click="jumpTo(current - 1)">
      上一页
    </button>
    <template v-for="p in pages" :key="p">
      <button
        v-if="p !== '...'"
        class="pagination-btn"
        :class="{ active: p === current }"
        @click="jumpTo(p)"
      >
        {{ p }}
      </button>
      <span v-else class="pagination-info">...</span>
    </template>
    <button
      class="pagination-btn"
      :disabled="current >= totalPages"
      @click="jumpTo(current + 1)"
    >
      下一页
    </button>
    <span class="pagination-info">共 {{ total }} 条</span>
  </div>
</template>
