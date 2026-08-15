<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { getArticle } from '@/api/article'
import { addComment, listComment } from '@/api/comment'
import type { ArticleVO, CommentVO } from '@/types'
import AppPagination from '@/components/AppPagination.vue'
import TocSidebar from '@/components/TocSidebar.vue'
import BackToTop from '@/components/BackToTop.vue'
import ReadingProgressBar from '@/components/ReadingProgressBar.vue'
import { renderMarkdown } from '@/utils/markdown'
import { useTableOfContents } from '@/composables/useTableOfContents'
import { useUserStore } from '@/stores/user'
import { startWechatLogin } from '@/utils/wechat'

const route = useRoute()
const router = useRouter()

const userStore = useUserStore()
const { isLoggedIn, nickname } = storeToRefs(userStore)

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

const comments = ref<CommentVO[]>([])
const commentPage = ref(1)
const commentSize = ref(10)
const commentTotal = ref(0)
const commentLoading = ref(false)

const commentForm = reactive({
  content: '',
})
const commentSubmitting = ref(false)
const commentError = ref('')
const commentTextareaRef = ref<HTMLTextAreaElement | null>(null)
const wechatLoading = ref(false)
const wechatError = ref('')

// 评论编辑器标签页：write = 编辑，preview = 预览
const commentTab = ref<'write' | 'preview'>('write')
// 实时渲染评论输入框中的 Markdown 内容
const commentPreview = computed(() => renderMarkdown(commentForm.content))

// ========== 文章互动 Emoji（精简为 8 个） ==========
interface ReactionEmoji {
  char: string
  name: string
}

const reactionEmojis: ReactionEmoji[] = [
  { char: '👍', name: '点赞' },
  { char: '👎', name: '点踩' },
  { char: '😂', name: '大笑' },
  { char: '🎉', name: '庆祝' },
  { char: '🤔', name: '疑惑' },
  { char: '❤️', name: '爱心' },
  { char: '🚀', name: '火箭' },
  { char: '👀', name: '眼睛' },
]

interface ReactionState {
  count: number
  active: boolean
}

// 前端本地维护的反应状态，不请求后端
const reactions = reactive<Record<string, ReactionState>>({})
reactionEmojis.forEach((e) => {
  reactions[e.char] = { count: 0, active: false }
})

// 点击 emoji：切换选中态并更新计数（仅前端视觉反馈）
function toggleReaction(char: string) {
  const state = reactions[char]
  if (!state) return
  if (state.active) {
    state.active = false
    state.count = Math.max(0, state.count - 1)
  } else {
    state.active = true
    state.count += 1
  }
}

// 向评论输入框插入 emoji
function insertEmoji(char: string) {
  const textarea = commentTextareaRef.value
  if (!textarea) {
    commentForm.content += char
    return
  }
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const before = commentForm.content.slice(0, start)
  const after = commentForm.content.slice(end)
  commentForm.content = before + char + after
  // 恢复光标位置到插入字符之后
  nextTick(() => {
    textarea.focus()
    const newPos = start + char.length
    textarea.setSelectionRange(newPos, newPos)
  })
}

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

async function submitComment() {
  if (!commentForm.content.trim()) {
    commentError.value = '请输入评论内容'
    return
  }
  commentError.value = ''
  commentSubmitting.value = true
  try {
    await addComment({
      articleId: articleId.value,
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

function formatDateOnly(s?: string) {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function goLogin() {
  router.push({ path: '/login', query: { redirect: route.fullPath } })
}

function goRegister() {
  router.push({ path: '/register', query: { redirect: route.fullPath } })
}

async function handleWechatLogin() {
  wechatError.value = ''
  wechatLoading.value = true
  try {
    await startWechatLogin(route.fullPath)
  } catch (e: any) {
    wechatError.value = e?.message || '微信登录失败'
  } finally {
    wechatLoading.value = false
  }
}

async function handleLogout() {
  await userStore.logout()
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
            <div class="meta mt-8">
              <span class="publish-time">{{ formatDateOnly(article.publishTime || article.createTime) }}</span>
              <span v-if="article.isTop" class="tag tag-sm">置顶</span>
            </div>
            <img v-if="article.cover" :src="article.cover" class="cover mt-16" alt="cover" />
            <div class="content markdown-body mt-24" v-html="renderedContent"></div>

            <div class="action-bar mt-24" role="group" aria-label="文章互动">
              <button
                v-for="e in reactionEmojis"
                :key="e.char"
                type="button"
                class="reaction-btn"
                :class="{ active: reactions[e.char]?.active ?? false }"
                :aria-pressed="reactions[e.char]?.active ?? false"
                :aria-label="e.name"
                :title="e.name"
                @click="toggleReaction(e.char)"
              >
                <span class="reaction-emoji">{{ e.char }}</span>
                <span v-if="(reactions[e.char]?.count ?? 0) > 0" class="reaction-count">
                  {{ reactions[e.char]?.count ?? 0 }}
                </span>
              </button>
            </div>
          </article>

          <section class="mb-24">
            <div class="composer">
              <!-- 未登录：注册 / 登录 / 微信登录入口 -->
              <div v-if="!isLoggedIn" class="composer-login">
                <p class="login-title">登录后参与评论</p>
                <p class="login-hint">支持账号密码或微信扫码一键登录</p>
                <div class="login-actions">
                  <button type="button" class="btn btn-outline btn-sm" @click="goLogin">账号登录</button>
                  <button type="button" class="btn btn-outline btn-sm" @click="goRegister">注册账号</button>
                  <button
                    type="button"
                    class="btn btn-primary btn-sm"
                    :disabled="wechatLoading"
                    @click="handleWechatLogin"
                  >
                    {{ wechatLoading ? '跳转中...' : '微信登录' }}
                  </button>
                </div>
                <div v-if="wechatError" class="composer-error">{{ wechatError }}</div>
              </div>

              <!-- 已登录：评论编辑器 -->
              <template v-else>
                <div class="composer-tabs" role="tablist" aria-label="评论编辑模式">
                  <button
                    type="button"
                    role="tab"
                    class="composer-tab"
                    :class="{ active: commentTab === 'write' }"
                    :aria-selected="commentTab === 'write'"
                    @click="commentTab = 'write'"
                  >
                    Write
                  </button>
                  <button
                    type="button"
                    role="tab"
                    class="composer-tab"
                    :class="{ active: commentTab === 'preview' }"
                    :aria-selected="commentTab === 'preview'"
                    @click="commentTab = 'preview'"
                  >
                    Preview
                  </button>
                </div>

                <div v-if="commentError" class="composer-error">{{ commentError }}</div>

                <div v-if="commentTab === 'write'" class="composer-body">
                  <div class="emoji-toolbar" role="toolbar" aria-label="插入表情">
                    <button
                      v-for="e in reactionEmojis"
                      :key="e.char"
                      type="button"
                      class="emoji-quick-btn"
                      :title="e.name"
                      :aria-label="'插入 ' + e.name"
                      @click="insertEmoji(e.char)"
                    >
                      {{ e.char }}
                    </button>
                  </div>
                  <textarea
                    ref="commentTextareaRef"
                    v-model="commentForm.content"
                    class="composer-textarea"
                    placeholder="写下你的评论...（支持 Markdown）"
                  ></textarea>
                </div>

                <div v-else class="composer-body composer-preview">
                  <div v-if="commentForm.content.trim()" class="markdown-body" v-html="commentPreview"></div>
                  <div v-else class="preview-empty">Nothing to preview</div>
                </div>

                <div class="composer-footer">
                  <span class="composer-hint">以 {{ nickname }} 身份评论 · Styling with Markdown is supported</span>
                  <div class="composer-actions">
                    <button type="button" class="btn btn-outline btn-sm" @click="handleLogout">退出登录</button>
                    <button class="btn btn-primary btn-sm" :disabled="commentSubmitting" @click="submitComment">
                      {{ commentSubmitting ? '提交中...' : '发表评论' }}
                    </button>
                  </div>
                </div>
              </template>
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
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--text-tertiary);
}

.publish-time {
  letter-spacing: 0.02em;
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
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.reaction-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid var(--border-base);
  border-radius: 20px;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.reaction-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-bg);
}

.reaction-btn.active {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-bg);
}

.reaction-emoji {
  display: inline-block;
  font-size: 18px;
  line-height: 1;
}

.reaction-btn.active .reaction-emoji {
  animation: reaction-pop 0.3s ease;
}

.reaction-btn:active .reaction-emoji {
  transform: scale(1.3);
}

.reaction-count {
  font-size: 13px;
  font-weight: 600;
}

@keyframes reaction-pop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.4);
  }
  100% {
    transform: scale(1);
  }
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

/* ========== 评论输入框 Emoji 快捷插入样式 ========== */
.emoji-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.emoji-quick-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
  transition:
    background-color 0.15s ease,
    transform 0.15s ease;
}

.emoji-quick-btn:hover {
  background: var(--bg-subtle);
  transform: scale(1.15);
}

.emoji-quick-btn:active {
  transform: scale(0.9);
}

/* ========== 评论编辑器（Write / Preview） ========== */
.composer {
  border: 1px solid var(--border-base);
  border-radius: 8px;
  background: var(--bg-card);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.composer-login {
  padding: 24px 16px;
  text-align: center;
}

.login-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.login-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.login-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.composer-tabs {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 12px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-subtle);
}

.composer-tab {
  position: relative;
  padding: 10px 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.composer-tab:hover {
  color: var(--text-primary);
}

.composer-tab.active {
  color: var(--text-primary);
}

.composer-tab.active::after {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: -1px;
  height: 2px;
  border-radius: 2px 2px 0 0;
  background: var(--accent);
}

.composer-error {
  margin: 8px 12px 0;
}

.composer-body {
  padding: 12px;
}

.composer-textarea {
  width: 100%;
  min-height: 120px;
  padding: 0;
  border: none;
  outline: none;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background: transparent;
}

.composer-textarea::placeholder {
  color: var(--text-tertiary);
}

.composer-preview {
  min-height: 140px;
}

.preview-empty {
  color: var(--text-tertiary);
  padding: 16px 0;
  text-align: center;
}

.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 8px 12px;
  border-top: 1px solid var(--border-light);
  background: var(--bg-subtle);
}

.composer-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
