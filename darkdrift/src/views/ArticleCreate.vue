<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { addArticle } from '@/api/article'
import { listCategory } from '@/api/category'
import { listTag } from '@/api/tag'
import type { CategoryVO, TagVO } from '@/types'

const router = useRouter()

const categories = ref<CategoryVO[]>([])
const tags = ref<TagVO[]>([])

const form = reactive({
  title: '',
  summary: '',
  cover: '',
  content: '',
  categoryId: undefined as number | undefined,
  isTop: 0,
  isOriginal: 1,
  tagIds: [] as number[],
})

const errors = reactive({
  title: '',
  summary: '',
  cover: '',
  content: '',
  categoryId: '',
})

const submitting = ref(false)
const globalError = ref('')
const success = ref('')

const contentLength = computed(() => form.content.length)
const summaryLength = computed(() => form.summary.length)

async function loadOptions() {
  try {
    const [catRes, tagRes] = await Promise.all([
      listCategory({ current: 1, pageSize: 100 }),
      listTag({ current: 1, pageSize: 100 }),
    ])
    categories.value = catRes.records || []
    tags.value = tagRes.records || []
  } catch {
    // 选项加载失败不阻塞表单
  }
}

function toggleTag(id: number) {
  const idx = form.tagIds.indexOf(id)
  if (idx >= 0) form.tagIds.splice(idx, 1)
  else form.tagIds.push(id)
}

function validate() {
  errors.title = ''
  errors.summary = ''
  errors.cover = ''
  errors.content = ''
  errors.categoryId = ''
  let ok = true
  if (!form.title.trim()) {
    errors.title = '请输入文章标题'
    ok = false
  } else if (form.title.trim().length > 200) {
    errors.title = '标题不能超过 200 个字符'
    ok = false
  }
  if (form.summary && form.summary.length > 500) {
    errors.summary = '摘要不能超过 500 个字符'
    ok = false
  }
  if (form.cover && form.cover.length > 500) {
    errors.cover = '封面链接过长'
    ok = false
  }
  if (!form.content.trim()) {
    errors.content = '请输入文章内容'
    ok = false
  }
  return ok
}

async function submit(status: number) {
  globalError.value = ''
  success.value = ''
  if (!validate()) return
  submitting.value = true
  try {
    const id = await addArticle({
      title: form.title.trim(),
      summary: form.summary.trim() || undefined,
      cover: form.cover.trim() || undefined,
      content: form.content,
      categoryId: form.categoryId,
      status,
      isTop: form.isTop,
      isOriginal: form.isOriginal,
      tagIds: form.tagIds,
    })
    success.value = status === 1 ? '发布成功！即将跳转文章详情...' : '草稿已保存！即将跳转文章详情...'
    setTimeout(() => {
      router.replace(`/article/${id}`)
    }, 1000)
  } catch (e: any) {
    globalError.value = e?.message || '保存失败'
  } finally {
    submitting.value = false
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

onMounted(() => {
  loadOptions()
})
</script>

<template>
  <div class="create-page">
    <button class="btn btn-outline btn-sm mb-16" @click="goBack">← 返回</button>

    <div class="card">
      <h1 class="page-title">新增文章</h1>
      <p class="page-subtitle">填写以下信息发布一篇新文章</p>

      <div v-if="globalError" class="banner banner-error">⚠️ {{ globalError }}</div>
      <div v-if="success" class="banner banner-success">✅ {{ success }}</div>

      <div class="form-item">
        <label class="form-label">文章标题 <span class="required">*</span></label>
        <input
          v-model="form.title"
          class="form-input"
          placeholder="请输入文章标题（最多 200 字）"
          maxlength="200"
        />
        <div v-if="errors.title" class="form-error">{{ errors.title }}</div>
      </div>

      <div class="form-item">
        <label class="form-label">摘要</label>
        <textarea
          v-model="form.summary"
          class="form-textarea"
          placeholder="一句话概括文章内容（可选，最多 500 字）"
          rows="3"
          maxlength="500"
        ></textarea>
        <div class="field-meta">
          <span v-if="errors.summary" class="form-error">{{ errors.summary }}</span>
          <span class="counter">{{ summaryLength }}/500</span>
        </div>
      </div>

      <div class="form-item">
        <label class="form-label">封面图片链接</label>
        <input
          v-model="form.cover"
          class="form-input"
          placeholder="https://... （可选）"
        />
        <div v-if="errors.cover" class="form-error">{{ errors.cover }}</div>
      </div>

      <div class="form-row flex gap-16 flex-wrap">
        <div class="form-item flex-1" style="min-width: 200px">
          <label class="form-label">分类</label>
          <select v-model="form.categoryId" class="form-select">
            <option :value="undefined">请选择分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>

        <div class="form-item" style="min-width: 200px">
          <label class="form-label">属性</label>
          <div class="check-group">
            <label class="check-item">
              <input
                type="checkbox"
                :checked="form.isOriginal === 1"
                @change="form.isOriginal = ($event.target as HTMLInputElement).checked ? 1 : 0"
              />
              <span>原创</span>
            </label>
            <label class="check-item">
              <input
                type="checkbox"
                :checked="form.isTop === 1"
                @change="form.isTop = ($event.target as HTMLInputElement).checked ? 1 : 0"
              />
              <span>置顶</span>
            </label>
          </div>
        </div>
      </div>

      <div class="form-item">
        <label class="form-label">标签</label>
        <div v-if="tags.length === 0" class="empty-tags">暂无标签可选</div>
        <div v-else class="tag-picker">
          <button
            v-for="t in tags"
            :key="t.id"
            type="button"
            class="tag-chip"
            :class="{ active: form.tagIds.includes(t.id) }"
            @click="toggleTag(t.id)"
          >
            {{ t.name }}
          </button>
        </div>
      </div>

      <div class="form-item">
        <label class="form-label">
          正文内容 <span class="required">*</span>
          <span class="hint">支持 Markdown 语法</span>
        </label>
        <textarea
          v-model="form.content"
          class="form-textarea content-editor"
          placeholder="在此输入正文内容..."
          rows="18"
        ></textarea>
        <div class="field-meta">
          <span v-if="errors.content" class="form-error">{{ errors.content }}</span>
          <span class="counter">{{ contentLength }} 字</span>
        </div>
      </div>

      <div class="action-bar flex gap-12 flex-wrap">
        <button
          class="btn btn-primary"
          type="button"
          :disabled="submitting"
          @click="submit(1)"
        >
          {{ submitting ? '提交中...' : '✍️ 发布文章' }}
        </button>
        <button
          class="btn btn-outline"
          type="button"
          :disabled="submitting"
          @click="submit(0)"
        >
          存为草稿
        </button>
        <button class="btn btn-outline" type="button" :disabled="submitting" @click="goBack">
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 24px;
}

.required {
  color: var(--danger);
}

.hint {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-tertiary);
  margin-left: 6px;
}

.form-row {
  align-items: flex-start;
}

.check-group {
  display: flex;
  gap: 16px;
  padding-top: 6px;
}

.check-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
}

.check-item input {
  cursor: pointer;
}

.tag-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 4px 12px;
  border: 1px solid var(--border-base);
  border-radius: 14px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.tag-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.tag-chip.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.empty-tags {
  font-size: 13px;
  color: var(--text-tertiary);
}

.content-editor {
  min-height: 320px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  line-height: 1.6;
}

.field-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.counter {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: auto;
}

.action-bar {
  padding-top: 16px;
  border-top: 1px solid var(--border-lighter);
  margin-top: 8px;
}

.banner {
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 16px;
}

.banner-error {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.banner-success {
  background: var(--accent-bg);
  color: var(--accent);
  border: 1px solid var(--accent-border);
}
</style>
