<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppPagination from '@/components/AppPagination.vue'
import { listArticle } from '@/api/article'
import { listCategory } from '@/api/category'
import type { ArticleVO, CategoryVO } from '@/types'

const router = useRouter()
const route = useRoute()

const articles = ref<ArticleVO[]>([])
const categories = ref<CategoryVO[]>([])
const loading = ref(false)
const searching = ref(false)
const error = ref('')

const current = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const categoryId = ref<number | undefined>()

// 实时搜索防抖配置
const DEBOUNCE_DELAY = 400
let searchTimer: ReturnType<typeof setTimeout> | null = null
// 请求令牌：用于取消过期的搜索请求，避免快速输入时旧结果覆盖新结果
let searchToken = 0

function readQueryParams() {
  const q = route.query
  if (q.page) current.value = parseInt(String(q.page), 10) || 1
  if (q.size) pageSize.value = parseInt(String(q.size), 10) || 10
  if (q.keyword) keyword.value = String(q.keyword)
  if (q.categoryId) categoryId.value = parseInt(String(q.categoryId), 10) || undefined
}

async function loadCategories() {
  try {
    const res = await listCategory({ current: 1, pageSize: 100 })
    categories.value = res.records || []
  } catch (e) {
    // ignore
  }
}

async function loadArticles() {
  // 递增令牌，使任何在途的旧请求结果失效
  const myToken = ++searchToken
  loading.value = true
  searching.value = true
  error.value = ''
  try {
    const res = await listArticle({
      current: current.value,
      pageSize: pageSize.value,
      title: keyword.value || undefined,
      categoryId: categoryId.value,
      sortField: 'publishTime',
      sortOrder: 'descend',
      status: 1,
    })
    // 仅当本次请求仍是最新时才应用结果，防止快速输入时旧结果覆盖新结果
    if (myToken !== searchToken) return
    articles.value = res.records || []
    total.value = res.total || 0
  } catch (e: any) {
    if (myToken !== searchToken) return
    error.value = e?.message || '加载失败'
    articles.value = []
    total.value = 0
  } finally {
    if (myToken === searchToken) {
      loading.value = false
      searching.value = false
    }
  }
}

function cancelPendingSearch() {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
}

function onSearch() {
  // 立即触发搜索时取消任何挂起的防抖搜索，避免重复请求
  cancelPendingSearch()
  current.value = 1
  syncUrlAndLoad()
}

function resetSearch() {
  cancelPendingSearch()
  keyword.value = ''
  categoryId.value = undefined
  current.value = 1
  syncUrlAndLoad()
}

// 清空搜索框：watch 会触发防抖搜索并加载默认文章列表
function clearKeyword() {
  keyword.value = ''
}

function onSelectCategory(id?: number) {
  categoryId.value = id
  current.value = 1
  syncUrlAndLoad()
}

function onPageChange(page: number) {
  current.value = page
  syncUrlAndLoad()
}

// 标记 URL 变更由内部触发，避免 route watcher 与 syncUrlAndLoad 重复加载
let internalUrlChange = false

function syncUrlAndLoad() {
  const query: any = {}
  if (current.value !== 1) query.page = current.value
  if (pageSize.value !== 10) query.size = pageSize.value
  if (keyword.value) query.keyword = keyword.value
  if (categoryId.value) query.categoryId = categoryId.value
  internalUrlChange = true
  router.replace({ path: '/', query })
  loadArticles()
}

function goDetail(id: number) {
  router.push(`/article/${id}`)
}

function formatDate(s?: string) {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// 实时搜索：监听关键词变化，防抖触发搜索
// - 400ms 防抖延迟，避免频繁输入产生过多 API 请求
// - 搜索框清空时也会触发，加载默认文章列表（title=undefined）
watch(keyword, () => {
  cancelPendingSearch()
  searchTimer = setTimeout(() => {
    searchTimer = null
    current.value = 1
    syncUrlAndLoad()
  }, DEBOUNCE_DELAY)
})

onMounted(() => {
  readQueryParams()
  loadCategories()
  loadArticles()
})

watch(
  () => route.fullPath,
  () => {
    // 内部触发的 URL 变更已由 syncUrlAndLoad 加载，跳过避免重复请求
    if (internalUrlChange) {
      internalUrlChange = false
      return
    }
    readQueryParams()
    loadArticles()
  },
)

// 组件卸载时清理防抖定时器，避免内存泄漏与卸载后 setState
onBeforeUnmount(() => {
  cancelPendingSearch()
})
</script>

<template>
  <div class="home-page">
    <div class="card search-card mb-24">
      <div class="flex gap-12 flex-wrap items-center">
        <div class="form-item flex-1" style="margin-bottom: 0; min-width: 200px">
          <div class="search-input-wrap">
            <input
              v-model="keyword"
              class="form-input search-input"
              type="search"
              inputmode="search"
              autocomplete="off"
              placeholder="输入关键词实时搜索文章标题..."
              @keyup.enter="onSearch"
            />
            <button
              v-if="keyword && !searching"
              class="search-clear"
              type="button"
              aria-label="清空搜索"
              @click="clearKeyword"
            >
              ×
            </button>
            <span v-if="searching" class="search-spinner" aria-label="搜索中"></span>
          </div>
        </div>
        <button class="btn btn-primary" :disabled="loading" @click="onSearch">搜索</button>
        <button class="btn btn-outline" :disabled="loading" @click="resetSearch">重置</button>
      </div>

      <div class="category-filter mt-16" v-if="categories.length > 0">
        <div class="flex gap-8 flex-wrap">
          <button
            class="btn btn-sm"
            :class="categoryId === undefined ? 'btn-primary' : 'btn-outline'"
            @click="onSelectCategory(undefined)"
          >
            全部
          </button>
          <button
            v-for="c in categories"
            :key="c.id"
            class="btn btn-sm"
            :class="categoryId === c.id ? 'btn-primary' : 'btn-outline'"
            @click="onSelectCategory(c.id)"
          >
            {{ c.name }} ({{ c.article_count }})
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="loadArticles">重试</button>
    </div>

    <div v-else-if="loading" class="card">
      <div class="loading">{{ keyword ? '搜索中...' : '加载中...' }}</div>
    </div>

    <div v-else-if="articles.length === 0" class="card">
      <div class="empty">
        {{ keyword ? `未找到与"${keyword}"匹配的文章` : '暂无文章' }}
      </div>
    </div>

    <div v-else class="article-list">
      <article
        v-for="item in articles"
        :key="item.id"
        class="card article-item"
        @click="goDetail(item.id)"
      >
        <div class="flex gap-16" style="align-items: stretch">
          <div v-if="item.cover" class="cover-wrap">
            <img :src="item.cover" alt="cover" class="cover-img" />
          </div>
          <div class="flex-1 article-main">
            <h2 class="article-title">{{ item.title }}</h2>
            <p v-if="item.summary" class="article-summary">{{ item.summary }}</p>
            <div class="article-meta flex gap-16 wrap">
              <span>📅 {{ formatDate(item.publishTime || item.createTime) }}</span>
              <span>👁️ {{ item.viewCount || 0 }}</span>
              <span>❤️ {{ item.likeCount || 0 }}</span>
              <span>💬 {{ item.commentCount || 0 }}</span>
              <span
                v-if="item.isTop"
                class="tag"
                style="
                  background: var(--danger-bg);
                  color: var(--danger);
                  border-color: var(--danger-border);
                "
                >置顶</span
              >
              <span v-if="!item.isOriginal" class="tag">转载</span>
            </div>
          </div>
        </div>
      </article>

      <AppPagination
        :current="current"
        :page-size="pageSize"
        :total="total"
        @change="onPageChange"
      />
    </div>
  </div>
</template>

<style scoped>
.search-card {
  background: var(--bg-card);
}

/* 实时搜索输入框容器 */
.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  /* 为右侧清空按钮和加载图标预留空间 */
  padding-right: 40px;
}

/* 去除浏览器原生 search 输入框的清除按钮，避免与自定义按钮重复 */
.search-input::-webkit-search-decoration,
.search-input::-webkit-search-cancel-button,
.search-input::-webkit-search-results-button,
.search-input::-webkit-search-results-decoration {
  -webkit-appearance: none;
  appearance: none;
}

/* 清空按钮 */
.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: var(--bg-subtle);
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.search-clear:hover {
  background: var(--border-light);
  color: var(--text-primary);
}

/* 加载旋转图标 */
.search-spinner {
  position: absolute;
  right: 12px;
  top: 50%;
  margin-top: -8px;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-light);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: search-spin 0.8s linear infinite;
}

@keyframes search-spin {
  to {
    transform: rotate(360deg);
  }
}

.category-filter {
  padding-top: 8px;
  border-top: 1px solid var(--border-lighter);
}

.article-item {
  cursor: pointer;
  margin-bottom: 16px;
}

.article-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.cover-wrap {
  width: 200px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-subtle);
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  min-height: 140px;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.article-summary {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  font-size: 13px;
  color: var(--text-tertiary);
}

.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
  font-size: 14px;
}

.error-box {
  color: var(--danger);
  font-size: 14px;
}

@media (max-width: 640px) {
  .article-item > div {
    flex-direction: column;
  }

  .cover-wrap {
    width: 100%;
    height: 160px;
  }
}
</style>
