<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppPagination from '@/components/AppPagination.vue'
import { listCategory } from '@/api/category'
import { listArticle } from '@/api/article'
import type { CategoryVO } from '@/types'

const router = useRouter()

const categories = ref<CategoryVO[]>([])
const loading = ref(false)
const error = ref('')
const current = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await listCategory({
      current: current.value,
      pageSize: pageSize.value,
      sortField: 'sort',
      sortOrder: 'ascend',
    })
    categories.value = res.records || []
    total.value = res.total || 0
  } catch (e: any) {
    error.value = e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function goCategoryArticles(categoryId: number, categoryName: string) {
  router.push({
    path: '/',
    query: { categoryId, keyword: '' },
  })
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header card mb-24">
      <h1 class="page-title">📁 文章分类</h1>
      <p class="page-subtitle">共 {{ total }} 个分类，浏览感兴趣的主题</p>
    </div>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="load">重试</button>
    </div>

    <div v-else-if="loading" class="card">
      <div class="loading">加载中...</div>
    </div>

    <div v-else-if="categories.length === 0" class="card">
      <div class="empty">暂无分类</div>
    </div>

    <div v-else class="category-grid">
      <div
        v-for="c in categories"
        :key="c.id"
        class="card category-card"
        @click="goCategoryArticles(c.id, c.name)"
      >
        <div class="category-header flex justify-between items-center">
          <h3 class="category-name">{{ c.name }}</h3>
          <span class="tag">{{ c.article_count }} 篇</span>
        </div>
        <p v-if="c.description" class="category-desc mt-8">{{ c.description }}</p>
        <div class="category-footer mt-16">
          <span>排序：{{ c.sort }}</span>
          <span class="view-link">查看文章 →</span>
        </div>
      </div>

      <AppPagination
        :current="current"
        :page-size="pageSize"
        :total="total"
        @change="(p) => { current = p; load() }"
      />
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2d3d;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.category-card {
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.category-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2d3d;
}

.category-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  flex: 1;
}

.category-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
  padding-top: 12px;
  border-top: 1px solid #f2f6fc;
}

.view-link {
  color: #4a90d9;
  font-weight: 500;
}

.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.error-box {
  color: #f56c6c;
}
</style>
