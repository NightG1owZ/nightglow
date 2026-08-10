<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle, likeArticle, cancelLikeArticle } from '@/api/article'
import { addComment, listComment } from '@/api/comment'
import type { ArticleVO, CommentVO } from '@/types'
import AppPagination from '@/components/AppPagination.vue'
import TocSidebar from '@/components/TocSidebar.vue'
import BackToTop from '@/components/BackToTop.vue'
import ReadingProgressBar from '@/components/ReadingProgressBar.vue'
import { renderMarkdown } from '@/utils/markdown'
import { useTableOfContents } from '@/composables/useTableOfContents'

const route = useRoute()
const router = useRouter()

const articleId = computed(() => parseInt(String(route.params.id), 10) || 0)

const article = ref<ArticleVO | null>(null)

// 将文章正文 Markdown 渲染为已净化的 HTML
const renderedContent = computed(() =>
  article.value ? renderMarkdown(article.value.content || '') : '',
)

// Markdown 容器引用 —— 供 TOC 提取标题和锚点（包含文章 H1 标题 + Markdown 渲染内容中的 H1-H6）
const contentRef = ref<HTMLElement | null>(null)

const { tocItems, activeId, showBackToTop, rebuild, scrollToId, scrollToTop } =
  useTableOfContents(() => contentRef.value)

const tocVisible = computed(() => tocItems.value.length > 0)

// 每当文章内容渲染完成（DOM 更新完毕），重新生成目录
watch(
  [article, renderedContent],
  async () => {
    if (!article.value || !renderedContent.value) return
    // 等下一次 DOM 渲染完成，v-html 已将 heading 节点挂好
    await nextTick()
    // 再给一次保险等待（图片加载 / highlight.js DOM 变更）
    requestAnimationFrame(() => {
      requestAnimationFrame(() => rebuild())
    })
  },
  { flush: 'post' },
)

function handleTocJump(id: string) {
  scrollToId(id)
}

const loading = ref(false)
const error = ref('')
const liked = ref(false)
const likeLoading = ref(false)

const comments = ref<CommentVO[]>([])
const commentPage = ref(1)
const commentSize = ref(10)
const commentTotal = ref(0)
const commentLoading = ref(false)

const commentForm = reactive({
  nickname: '',
  email: '',
  avatar: '',
  content: '',
})
const commentSubmitting = ref(false)
const commentError = ref('')

async function loadArticle() {
  if (!articleId.value) {
    error.value = '无效的文章ID'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await getArticle(articleId.value)
    article.value = res
  } catch (e: any) {
    error.value = e?.message || '文章加载失败'
    article.value = null
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  if (!articleId.value) return
  commentLoading.value = true
  try {
    const res = await listComment({
      current: commentPage.value,
      pageSize: commentSize.value,
      articleId: articleId.value,
      status: 1,
      sortField: 'createTime',
      sortOrder: 'descend',
    })
    comments.value = res.records || []
    commentTotal.value = res.total || 0
  } catch {
    comments.value = []
  } finally {
    commentLoading.value = false
  }
}

async function toggleLike() {
  if (!articleId.value || likeLoading.value) return
  likeLoading.value = true
  try {
    if (liked.value) {
      await cancelLikeArticle({ articleId: articleId.value })
      liked.value = false
      if (article.value) article.value.likeCount = Math.max(0, (article.value.likeCount || 0) - 1)
    } else {
      await likeArticle({ articleId: articleId.value })
      liked.value = true
      if (article.value) article.value.likeCount = (article.value.likeCount || 0) + 1
    }
  } catch (e: any) {
    alert(e?.message || '操作失败')
  } finally {
    likeLoading.value = false
  }
}

async function submitComment() {
  if (!commentForm.nickname.trim()) {
    commentError.value = '请输入昵称'
    return
  }
  if (!commentForm.content.trim()) {
    commentError.value = '请输入评论内容'
    return
  }
  commentError.value = ''
  commentSubmitting.value = true
  try {
    await addComment({
      articleId: articleId.value,
      nickname: commentForm.nickname.trim(),
      email: commentForm.email.trim() || undefined,
      avatar: commentForm.avatar.trim() || undefined,
      content: commentForm.content.trim(),
    })
    commentForm.content = ''
    commentPage.value = 1
    loadComments()
    if (article.value) article.value.commentCount = (article.value.commentCount || 0) + 1
  } catch (e: any) {
    commentError.value = e?.message || '评论失败'
  } finally {
    commentSubmitting.value = false
  }
}

function formatDate(s?: string) {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

onMounted(() => {
  loadArticle()
  loadComments()
})
</script>

<template>
  <div class="detail-page">
    <ReadingProgressBar />

    <button class="btn btn-outline btn-sm mb-16" @click="goBack">← 返回列表</button>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="loadArticle">重试</button>
    </div>

    <div v-else-if="loading || !article" class="card">
      <div class="loading">加载中...</div>
    </div>

    <template v-else>
      <div class="article-layout">
        <TocSidebar
          :items="tocItems"
          :active-id="activeId"
          :visible="tocVisible"
          @jump="handleTocJump"
        />

        <div class="article-main">
          <article ref="contentRef" class="card mb-24 article-card">
            <h1 class="title" :id="'article-title'">{{ article.title }}</h1>
            <div class="meta flex gap-16 flex-wrap mt-8">
              <span>📅 {{ formatDate(article.publishTime || article.createTime) }}</span>
              <span>👁️ {{ article.viewCount || 0 }} 阅读</span>
              <span>💬 {{ article.commentCount || 0 }} 评论</span>
              <span v-if="article.isTop" class="tag tag-sm">置顶</span>
            </div>
            <img v-if="article.cover" :src="article.cover" class="cover mt-16" alt="cover" />
            <div class="content markdown-body mt-24" v-html="renderedContent"></div>

            <div class="action-bar mt-24">
              <button
                class="btn"
                :class="liked ? 'btn-primary' : 'btn-outline'"
                :disabled="likeLoading"
                @click="toggleLike"
              >
                {{ liked ? '❤️ 已点赞' : '🤍 点赞' }} ({{ article.likeCount || 0 }})
              </button>
            </div>
          </article>

          <section class="card mb-24">
            <h2 class="section-title">发表评论</h2>
            <div v-if="commentError" class="form-error">{{ commentError }}</div>
            <div class="comment-form">
              <div class="form-row flex gap-12 flex-wrap">
                <div class="form-item flex-1" style="min-width: 150px">
                  <label class="form-label">昵称 *</label>
                  <input v-model="commentForm.nickname" class="form-input" placeholder="请输入昵称" />
                </div>
                <div class="form-item flex-1" style="min-width: 150px">
                  <label class="form-label">邮箱（可选）</label>
                  <input v-model="commentForm.email" class="form-input" placeholder="用于回复通知" />
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">评论内容 *</label>
                <textarea
                  v-model="commentForm.content"
                  class="form-textarea"
                  placeholder="写下你的评论..."
                  rows="4"
                ></textarea>
              </div>
              <div class="flex justify-between">
                <span style="color: var(--text-tertiary); font-size: 12px">评论将公开显示</span>
                <button class="btn btn-primary" :disabled="commentSubmitting" @click="submitComment">
                  {{ commentSubmitting ? '提交中...' : '发表评论' }}
                </button>
              </div>
            </div>
          </section>

          <section class="card">
            <h2 class="section-title">评论列表 ({{ commentTotal }})</h2>
            <div v-if="commentLoading" class="loading">加载评论中...</div>
            <div v-else-if="comments.length === 0" class="empty">暂无评论，来抢沙发吧~</div>
            <ul v-else class="comment-list">
              <li v-for="c in comments" :key="c.id" class="comment-item">
                <div class="comment-head">
                  <img
                    v-if="c.avatar"
                    :src="c.avatar"
                    class="comment-avatar"
                    alt="avatar"
                    onerror="this.style.display = 'none'"
                  />
                  <div v-else class="comment-avatar fallback">
                    {{ (c.nickname || '匿').slice(0, 1) }}
                  </div>
                  <div class="comment-meta">
                    <div class="comment-name">{{ c.nickname || '匿名用户' }}</div>
                    <div class="comment-time">{{ formatDate(c.createTime) }}</div>
                  </div>
                </div>
                <div class="comment-body">{{ c.content }}</div>
              </li>
            </ul>
            <AppPagination
              v-if="commentTotal > commentSize"
              :current="commentPage"
              :page-size="commentSize"
              :total="commentTotal"
              @change="
                (p) => {
                  commentPage = p
                  loadComments()
                }
              "
            />
          </section>
        </div>
        <!-- /article-main -->
      </div>
      <!-- /article-layout -->

      <BackToTop :visible="showBackToTop" @go-top="scrollToTop" />
    </template>
  </div>
</template>

<style scoped>
.title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.35;
}

.meta {
  font-size: 13px;
  color: var(--text-tertiary);
}

.cover {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.content {
  font-size: 15px;
  line-height: 1.85;
  color: var(--text-regular);
  word-break: break-word;
}

/* ========== Markdown 正文样式 ========== */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.35;
  margin-top: 1.6em;
  margin-bottom: 0.6em;
}

.markdown-body :deep(h1) {
  font-size: 1.7em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-light);
}

.markdown-body :deep(h2) {
  font-size: 1.45em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-light);
}

.markdown-body :deep(h3) {
  font-size: 1.25em;
}

.markdown-body :deep(h4) {
  font-size: 1.1em;
}

.markdown-body :deep(h5) {
  font-size: 1em;
}

.markdown-body :deep(h6) {
  font-size: 0.9em;
  color: var(--text-tertiary);
}

.markdown-body :deep(p) {
  margin: 0 0 1em;
}

.markdown-body :deep(strong) {
  font-weight: 700;
  color: var(--text-primary);
}

.markdown-body :deep(em) {
  font-style: italic;
}

.markdown-body :deep(del) {
  color: var(--text-tertiary);
}

.markdown-body :deep(a) {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}

.markdown-body :deep(a:hover) {
  color: var(--accent-hover);
  border-bottom-color: var(--accent-hover);
  text-decoration: none;
}

.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  display: block;
  margin: 1em auto;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 1em;
  padding-left: 1.8em;
}

.markdown-body :deep(li) {
  margin: 0.25em 0;
}

.markdown-body :deep(li > ul),
.markdown-body :deep(li > ol) {
  margin: 0.25em 0;
}

.markdown-body :deep(blockquote) {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 4px solid var(--accent);
  background: var(--bg-subtle);
  color: var(--text-secondary);
  border-radius: 0 4px 4px 0;
}

.markdown-body :deep(blockquote > p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(hr) {
  margin: 1.6em 0;
  border: none;
  border-top: 2px solid var(--border-light);
}

/* 行内代码 */
.markdown-body :deep(code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.88em;
  padding: 0.2em 0.4em;
  background: var(--bg-subtle);
  border-radius: 3px;
  color: var(--danger);
}

/* 代码块 */
.markdown-body :deep(pre) {
  margin: 1em 0;
  padding: 14px 16px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-light);
  border-radius: 6px;
  overflow-x: auto;
  line-height: 1.55;
}

.markdown-body :deep(pre code) {
  font-size: 0.85em;
  padding: 0;
  background: transparent;
  border-radius: 0;
  color: var(--text-regular);
  white-space: pre;
}

/* GFM 表格 */
.markdown-body :deep(table) {
  width: 100%;
  margin: 1em 0;
  border-collapse: collapse;
  overflow-x: auto;
  display: block;
}

.markdown-body :deep(thead) {
  background: var(--bg-subtle);
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 8px 12px;
  border: 1px solid var(--border-base);
  text-align: left;
}

.markdown-body :deep(th) {
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-body :deep(tbody tr:nth-child(2n)) {
  background: var(--bg-subtle);
}

/* 任务列表复选框 */
.markdown-body :deep(input[type='checkbox']) {
  margin-right: 0.4em;
  vertical-align: middle;
}

/* ========== highlight.js 语法高亮配色（随主题切换） ========== */
.markdown-body :deep(.hljs) {
  color: var(--text-regular);
  background: transparent;
}

.markdown-body :deep(.hljs-comment),
.markdown-body :deep(.hljs-quote) {
  color: var(--text-tertiary);
  font-style: italic;
}

.markdown-body :deep(.hljs-keyword),
.markdown-body :deep(.hljs-selector-tag),
.markdown-body :deep(.hljs-built_in),
.markdown-body :deep(.hljs-name),
.markdown-body :deep(.hljs-tag) {
  color: var(--accent);
}

.markdown-body :deep(.hljs-string),
.markdown-body :deep(.hljs-title),
.markdown-body :deep(.hljs-section),
.markdown-body :deep(.hljs-attribute),
.markdown-body :deep(.hljs-literal),
.markdown-body :deep(.hljs-template-tag),
.markdown-body :deep(.hljs-template-variable),
.markdown-body :deep(.hljs-type),
.markdown-body :deep(.hljs-addition) {
  color: var(--success);
}

.markdown-body :deep(.hljs-number),
.markdown-body :deep(.hljs-symbol),
.markdown-body :deep(.hljs-bullet),
.markdown-body :deep(.hljs-link),
.markdown-body :deep(.hljs-meta),
.markdown-body :deep(.hljs-selector-id),
.markdown-body :deep(.hljs-selector-class) {
  color: var(--warning);
}

.markdown-body :deep(.hljs-attr),
.markdown-body :deep(.hljs-variable),
.markdown-body :deep(.hljs-property),
.markdown-body :deep(.hljs-params) {
  color: var(--text-primary);
}

.markdown-body :deep(.hljs-deletion) {
  color: var(--danger);
}

.markdown-body :deep(.hljs-emphasis) {
  font-style: italic;
}

.markdown-body :deep(.hljs-strong) {
  font-weight: 700;
}

.action-bar {
  padding-top: 16px;
  border-top: 1px solid var(--border-lighter);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.comment-list {
  list-style: none;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-lighter);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.comment-avatar.fallback {
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.comment-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.comment-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.comment-body {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
  padding-left: 48px;
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

/* ========== 两栏布局：左侧目录 + 主内容（更大宽度占比） ========== */
.article-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  align-items: start;
  gap: 32px;
  width: 100%;
}

/* 目录所在 grid item 占满整行高度，使内部 sticky 有滚动空间 */
.article-layout > :first-child {
  align-self: stretch;
}

.article-main {
  width: 100%;
  min-width: 0; /* 允许内部 markdown 溢出元素 (表格) 正确显示滚动条 */
}

.article-card {
  /* 预留 padding，使 sticky 目录与 card 上边缘对齐 */
}

/* 桌面端（>= 1280px）：进一步增大目录区域 */
@media (min-width: 1280px) {
  .article-layout {
    grid-template-columns: 300px 1fr;
    gap: 40px;
  }
}

/* 平板端（768px - 1023px）：保持两栏但减小目录宽度 */
@media (min-width: 768px) and (max-width: 1023px) {
  .article-layout {
    grid-template-columns: 240px 1fr;
    gap: 24px;
  }
}

/* 移动端（< 768px）：让侧边栏收起为 FAB + 抽屉（由组件自行处理） */
@media (max-width: 767px) {
  .article-layout {
    display: block;
  }
}

@media (max-width: 640px) {
  .title {
    font-size: 22px;
  }
  .comment-body {
    padding-left: 0;
  }
  .markdown-body {
    font-size: 14px;
  }
  .markdown-body :deep(h1) {
    font-size: 1.5em;
  }
  .markdown-body :deep(h2) {
    font-size: 1.3em;
  }
  .markdown-body :deep(pre) {
    padding: 10px 12px;
    font-size: 12px;
  }
  .markdown-body :deep(ul),
  .markdown-body :deep(ol) {
    padding-left: 1.4em;
  }
  .markdown-body :deep(table) {
    font-size: 13px;
  }
}
</style>
