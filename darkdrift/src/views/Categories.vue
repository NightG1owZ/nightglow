<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getTagTree } from '@/api/tag'
import type { TagTreeVO, TagArticleVO } from '@/types'

const tree = ref<TagTreeVO[]>([])
const loading = ref(false)
const error = ref('')
const expandedIds = ref<number[]>([])

type DisplayEntry =
  | { type: 'tag'; tag: TagTreeVO; depth: number }
  | { type: 'article'; article: TagArticleVO; depth: number }

const total = computed(() => {
  let count = 0
  const walk = (nodes: TagTreeVO[]) => {
    for (const n of nodes) {
      count += 1
      if (n.children.length) walk(n.children)
    }
  }
  walk(tree.value)
  return count
})

// 按展开状态展平为可见行：标签节点 + 其下关联的文章条目
const entries = computed<DisplayEntry[]>(() => {
  const result: DisplayEntry[] = []
  const walk = (nodes: TagTreeVO[], depth: number) => {
    for (const n of nodes) {
      result.push({ type: 'tag', tag: n, depth })
      if (expandedIds.value.includes(n.id)) {
        for (const a of n.articles) {
          result.push({ type: 'article', article: a, depth: depth + 1 })
        }
        if (n.children.length) walk(n.children, depth + 1)
      }
    }
  }
  walk(tree.value, 0)
  return result
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    tree.value = await getTagTree()
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function isExpanded(id: number) {
  return expandedIds.value.includes(id)
}

function toggle(id: number) {
  const i = expandedIds.value.indexOf(id)
  if (i >= 0) expandedIds.value.splice(i, 1)
  else expandedIds.value.push(id)
}

function entryKey(entry: DisplayEntry) {
  return entry.type === 'tag' ? `tag-${entry.tag.id}` : `article-${entry.article.id}`
}

function formatDate(s?: string) {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

const TAG_PALETTE = ['#4a90d9', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#8e6ddc']

function tagStyle(tag: TagTreeVO) {
  const color = tag.color || TAG_PALETTE[(tag.level - 1) % TAG_PALETTE.length]
  return {
    background: `${color}22`,
    color,
    borderColor: `${color}66`,
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header card mb-24">
      <h1 class="page-title">🗂️ 文章分类</h1>
      <p class="page-subtitle">共 {{ total }} 个标签，展开查看标签层级及其关联文章</p>
    </div>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="load">重试</button>
    </div>

    <div v-else-if="loading" class="card">
      <div class="loading">加载中...</div>
    </div>

    <div v-else-if="tree.length === 0" class="card">
      <div class="empty">暂无标签</div>
    </div>

    <div v-else class="card">
      <div class="tag-tree">
        <div
          v-for="entry in entries"
          :key="entryKey(entry)"
          class="tree-row"
          :style="{ paddingLeft: `${12 + entry.depth * 20}px` }"
        >
          <!-- 标签节点 -->
          <div
            v-if="entry.type === 'tag'"
            class="tag-row"
            role="button"
            :aria-expanded="isExpanded(entry.tag.id)"
            @click="toggle(entry.tag.id)"
          >
            <span class="toggle">{{ isExpanded(entry.tag.id) ? '▾' : '▸' }}</span>
            <span class="tag-name" :style="tagStyle(entry.tag)"># {{ entry.tag.name }}</span>
            <span class="tag-count">{{ entry.tag.articleCount }} 篇</span>
          </div>

          <!-- 关联文章条目 -->
          <router-link
            v-else
            :to="`/article/${entry.article.id}`"
            class="article-row"
            :title="entry.article.title"
          >
            <span class="article-title">{{ entry.article.title }}</span>
            <span class="article-date">{{ formatDate(entry.article.publishTime || entry.article.createTime) }}</span>
          </router-link>
        </div>
      </div>
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

.tag-tree {
  display: flex;
  flex-direction: column;
}

.tree-row {
  border-bottom: 1px solid var(--border-lighter);
}

.tree-row:last-child {
  border-bottom: none;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  cursor: pointer;
  min-width: 0;
}

.tag-row:hover .tag-name {
  opacity: 0.8;
}

.toggle {
  width: 22px;
  flex-shrink: 0;
  color: var(--text-tertiary);
  font-size: 14px;
  text-align: center;
}

.tag-name {
  display: inline-block;
  padding: 3px 12px;
  border: 1px solid;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.tag-count {
  font-size: 12px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.article-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 12px;
  margin: 0 0 0 22px;
  border-radius: 6px;
  text-decoration: none;
  transition: background-color 0.15s ease;
}

.article-row:hover {
  background: var(--bg-subtle);
  text-decoration: none;
}

.article-title {
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.article-date {
  font-size: 12px;
  color: var(--text-tertiary);
  flex-shrink: 0;
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
