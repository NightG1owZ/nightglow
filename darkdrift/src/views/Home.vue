<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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
const error = ref('')

const current = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const categoryId = ref<number | undefined>()

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
  loading.value = true
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
    articles.value = res.records || []
    total.value = res.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载失败'
    articles.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  current.value = 1
  syncUrlAndLoad()
}

function resetSearch() {
  keyword.value = ''
  categoryId.value = undefined
  onSearch()
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

function syncUrlAndLoad() {
  const query: any = {}
  if (current.value !== 1) query.page = current.value
  if (pageSize.value !== 10) query.size = pageSize.value
  if (keyword.value) query.keyword = keyword.value
  if (categoryId.value) query.categoryId = categoryId.value
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

onMounted(() => {
  readQueryParams()
  loadCategories()
  loadArticles()
})

watch(
  () => route.fullPath,
  () => {
    readQueryParams()
    loadArticles()
  },
)
</script>

<template>
  <div class="home-page">
    <div class="card search-card mb-24">
      <div class="flex gap-12 flex-wrap items-center">
        <div class="form-item flex-1" style="margin-bottom: 0; min-width: 200px">
          <input
            v-model="keyword"
            class="form-input"
            placeholder="搜索文章标题..."
            @keyup.enter="onSearch"
          />
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
      <div class="loading">加载中...</div>
    </div>

    <div v-else-if="articles.length === 0" class="card">
      <div class="empty">暂无文章</div>
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
