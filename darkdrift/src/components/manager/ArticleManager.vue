<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppPagination from '@/components/AppPagination.vue'
import ArticleCreate from '@/views/ArticleCreate.vue'
import { listArticle, deleteArticle } from '@/api/article'
import { listCategory } from '@/api/category'
import type { ArticleVO, CategoryVO } from '@/types'

const router = useRouter()

const articles = ref<ArticleVO[]>([])
const categories = ref<CategoryVO[]>([])
const loading = ref(false)
const error = ref('')
const toast = ref('')

const current = ref(1)
const pageSize = ref(10)
const total = ref(0)
const keyword = ref('')
const statusFilter = ref<number | undefined>(undefined)
const categoryFilter = ref<number | undefined>(undefined)

// 编辑状态
const editingId = ref<number | null>(null)
// 删除确认
const deletingId = ref<number | null>(null)
const deletingArticle = computed(() =>
  deletingId.value !== null ? articles.value.find((a) => a.id === deletingId.value) : null,
)

const STATUS_OPTIONS = [
  { value: undefined, label: '全部状态' },
  { value: 1, label: '已发布' },
  { value: 0, label: '草稿' },
]

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => {
    toast.value = ''
  }, 2500)
}

async function loadCategories() {
  try {
    const res = await listCategory({ current: 1, pageSize: 100 })
    categories.value = res.records || []
  } catch {
    // ignore
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await listArticle({
      current: current.value,
      pageSize: pageSize.value,
      title: keyword.value || undefined,
      status: statusFilter.value,
      categoryId: categoryFilter.value,
      sortField: 'createTime',
      sortOrder: 'descend',
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
  load()
}

function resetSearch() {
  keyword.value = ''
  statusFilter.value = undefined
  categoryFilter.value = undefined
  onSearch()
}

function onPageChange(page: number) {
  current.value = page
  load()
}

function statusText(s: number) {
  return s === 1 ? '已发布' : '草稿'
}

function statusClass(s: number) {
  return s === 1 ? 'status-published' : 'status-draft'
}

function categoryName(id?: number) {
  if (!id) return '未分类'
  const c = categories.value.find((x) => x.id === id)
  return c ? c.name : `#${id}`
}

function formatDate(s?: string) {
  if (!s) return '—'
  const d = new Date(s)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(
    d.getMinutes(),
  )}`
}

function viewDetail(id: number) {
  router.push(`/article/${id}`)
}

function startEdit(id: number) {
  editingId.value = id
}

function cancelEdit() {
  editingId.value = null
}

function onEditSuccess() {
  showToast('文章已保存')
  editingId.value = null
  load()
}

async function confirmDelete() {
  if (deletingId.value === null) return
  const id = deletingId.value
  loading.value = true
  try {
    await deleteArticle(id)
    showToast('文章已删除')
    deletingId.value = null
    if (articles.value.length <= 1 && current.value > 1) {
      current.value -= 1
    }
    await load()
  } catch (e: any) {
    error.value = e?.message || '删除失败'
    deletingId.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  load()
})
</script>

<template>
  <div class="article-manager">
    <div v-if="toast" class="toast toast-success">✅ {{ toast }}</div>

    <!-- 编辑模式：嵌入 ArticleCreate -->
    <div v-if="editingId !== null" class="edit-panel">
      <div class="edit-header flex items-center justify-between mb-16">
        <h3 class="section-title">📝 编辑文章 #{{ editingId }}</h3>
        <button class="btn btn-outline btn-sm" @click="cancelEdit">← 返回列表</button>
      </div>
      <ArticleCreate
        :key="editingId"
        :article-id="editingId"
        embedded
        @success="onEditSuccess"
        @cancel="cancelEdit"
      />
    </div>

    <!-- 列表模式 -->
    <template v-else>
      <div v-if="error" class="banner banner-error mb-16">⚠️ {{ error }}</div>

      <!-- 搜索过滤 -->
      <div class="card mb-24">
        <div class="flex gap-12 flex-wrap items-center">
          <div class="form-item flex-1" style="margin-bottom: 0; min-width: 200px">
            <input
              v-model="keyword"
              class="form-input"
              placeholder="搜索文章标题..."
              @keyup.enter="onSearch"
            />
          </div>
          <select v-model="statusFilter" class="form-select" style="width: auto">
            <option
              v-for="opt in STATUS_OPTIONS"
              :key="String(opt.value)"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>
          <select v-model="categoryFilter" class="form-select" style="width: auto">
            <option :value="undefined">全部分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <button class="btn btn-primary" :disabled="loading" @click="onSearch">搜索</button>
          <button class="btn btn-outline" :disabled="loading" @click="resetSearch">重置</button>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="card">
        <div class="flex justify-between items-center mb-16">
          <h3 class="section-title">📚 文章列表 ({{ total }})</h3>
        </div>

        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="articles.length === 0" class="empty">暂无文章</div>

        <div v-else class="article-table">
          <div class="article-row article-row-header">
            <div class="col-id">ID</div>
            <div class="col-title">标题</div>
            <div class="col-category">分类</div>
            <div class="col-status">状态</div>
            <div class="col-stats">浏览/点赞</div>
            <div class="col-time">发布时间</div>
            <div class="col-actions">操作</div>
          </div>
          <div v-for="a in articles" :key="a.id" class="article-row">
            <div class="col-id">{{ a.id }}</div>
            <div class="col-title">
              <span class="article-title-text" :title="a.title">{{ a.title }}</span>
              <span v-if="a.isTop" class="badge badge-top">置顶</span>
              <span v-if="!a.isOriginal" class="badge badge-reprint">转载</span>
            </div>
            <div class="col-category">{{ categoryName(a.categoryId) }}</div>
            <div class="col-status">
              <span class="status-badge" :class="statusClass(a.status)">
                {{ statusText(a.status) }}
              </span>
            </div>
            <div class="col-stats">
              <span>👁️ {{ a.viewCount || 0 }}</span>
              <span>❤️ {{ a.likeCount || 0 }}</span>
            </div>
            <div class="col-time">{{ formatDate(a.publishTime || a.createTime) }}</div>
            <div class="col-actions">
              <button class="btn btn-outline btn-sm" @click="viewDetail(a.id)">查看</button>
              <button class="btn btn-primary btn-sm" @click="startEdit(a.id)">编辑</button>
              <button class="btn btn-danger btn-sm" @click="deletingId = a.id">删除</button>
            </div>
          </div>
        </div>

        <AppPagination
          :current="current"
          :page-size="pageSize"
          :total="total"
          @change="onPageChange"
        />
      </div>
    </template>

    <!-- 删除确认弹窗 -->
    <div v-if="deletingId !== null" class="modal-mask" @click.self="deletingId = null">
      <div class="modal card">
        <h3 class="modal-title">确认删除</h3>
        <p class="modal-body">
          确认删除文章
          <strong>「{{ deletingArticle?.title }}」</strong>吗？此操作不可撤销。
        </p>
        <div class="modal-actions">
          <button class="btn btn-outline" :disabled="loading" @click="deletingId = null">
            取消
          </button>
          <button class="btn btn-danger" :disabled="loading" @click="confirmDelete">
            {{ loading ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.edit-header {
  flex-wrap: wrap;
  gap: 8px;
}

.loading,
.empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.article-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.article-row {
  display: grid;
  grid-template-columns: 50px 2fr 1fr 90px 120px 150px auto;
  align-items: center;
  gap: 12px;
  padding: 12px 8px;
  border-bottom: 1px solid var(--border-lighter);
  font-size: 13px;
}

.article-row:last-child {
  border-bottom: none;
}

.article-row-header {
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-subtle);
  border-radius: 6px;
  padding: 10px 8px;
}

.col-title {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.article-title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  font-weight: 500;
}

.badge {
  flex-shrink: 0;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.badge-top {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.badge-reprint {
  background: var(--bg-subtle);
  color: var(--text-tertiary);
  border: 1px solid var(--border-base);
}

.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-published {
  background: rgba(103, 194, 58, 0.15);
  color: var(--success);
  border: 1px solid rgba(103, 194, 58, 0.4);
}

.status-draft {
  background: var(--bg-subtle);
  color: var(--text-tertiary);
  border: 1px solid var(--border-base);
}

.col-stats {
  display: flex;
  gap: 10px;
  color: var(--text-tertiary);
}

.col-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.banner-error {
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.toast {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 200;
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 14px;
  box-shadow: var(--shadow-hover);
  animation: toast-in 0.25s ease;
}

.toast-success {
  background: var(--success);
  color: #fff;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
  padding: 16px;
}

.modal {
  width: 100%;
  max-width: 440px;
  padding: 24px;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.modal-body {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 1024px) {
  .article-row {
    grid-template-columns: 40px 1.5fr 90px 120px auto;
  }
  .col-category,
  .col-time {
    display: none;
  }
}

@media (max-width: 640px) {
  .article-row {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .article-row-header {
    display: none;
  }
  .col-id {
    grid-column: span 2;
    color: var(--text-tertiary);
    font-size: 12px;
  }
  .col-title {
    grid-column: span 2;
  }
  .col-stats {
    grid-column: span 2;
  }
  .col-actions {
    grid-column: span 2;
  }
}
</style>
