<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppPagination from '@/components/AppPagination.vue'
import { listTag } from '@/api/tag'
import type { TagVO } from '@/types'

const router = useRouter()

const tags = ref<TagVO[]>([])
const loading = ref(false)
const error = ref('')
const current = ref(1)
const pageSize = ref(50)
const total = ref(0)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await listTag({
      current: current.value,
      pageSize: pageSize.value,
      sortField: 'createTime',
      sortOrder: 'descend',
    })
    tags.value = res.records || []
    total.value = res.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

const TAG_PALETTE = ['#4a90d9', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#8e6ddc']

function getTagStyle(t: TagVO, i: number) {
  const color: string = t.color || TAG_PALETTE[i % TAG_PALETTE.length] || '#4a90d9'
  const count = t.article_count || 0
  return {
    // 半透明背景与边框，使其在各主题下均能自然融合
    background: `${color}22`,
    color,
    borderColor: `${color}66`,
    fontSize: Math.max(12, Math.min(20, 12 + Math.log2(count + 1) * 2)) + 'px',
    padding:
      Math.max(4, Math.min(10, 4 + count)) + 'px ' + Math.max(10, Math.min(18, 10 + count)) + 'px',
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header card mb-24">
      <h1 class="page-title">🏷️ 文章标签</h1>
      <p class="page-subtitle">共 {{ total }} 个标签，快速定位相关文章</p>
    </div>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="load">重试</button>
    </div>

    <div v-else-if="loading" class="card">
      <div class="loading">加载中...</div>
    </div>

    <div v-else-if="tags.length === 0" class="card">
      <div class="empty">暂无标签</div>
    </div>

    <div v-else class="card">
      <div class="tag-cloud">
        <router-link
          v-for="(t, i) in tags"
          :key="t.id"
          :to="{ path: '/', query: { keyword: '' } }"
          class="tag-item"
          :style="getTagStyle(t, i)"
          :title="`${t.name} - ${t.article_count || 0} 篇`"
        >
          #{{ t.name }}
          <span class="tag-count">{{ t.article_count }}</span>
        </router-link>
      </div>

      <AppPagination
        :current="current"
        :page-size="pageSize"
        :total="total"
        @change="
          (p) => {
            current = p
            load()
          }
        "
      />
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  padding: 16px 0;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid;
  border-radius: 20px;
  font-weight: 500;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  cursor: pointer;
}

.tag-item:hover {
  transform: scale(1.08);
  text-decoration: none;
  box-shadow: var(--shadow-hover);
}

.tag-count {
  font-size: 0.75em;
  opacity: 0.7;
}

.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.error-box {
  color: var(--danger);
}
</style>
