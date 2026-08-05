<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle, likeArticle, cancelLikeArticle } from '@/api/article'
import { addComment, listComment } from '@/api/comment'
import type { ArticleVO, CommentVO } from '@/types'
import AppPagination from '@/components/AppPagination.vue'

const route = useRoute()
const router = useRouter()

const articleId = computed(() => parseInt(String(route.params.id), 10) || 0)

const article = ref<ArticleVO | null>(null)
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
    <button class="btn btn-outline btn-sm mb-16" @click="goBack">← 返回列表</button>

    <div v-if="error" class="card mb-24 error-box">
      <p>⚠️ {{ error }}</p>
      <button class="btn btn-outline btn-sm mt-16" @click="loadArticle">重试</button>
    </div>

    <div v-else-if="loading || !article" class="card">
      <div class="loading">加载中...</div>
    </div>

    <template v-else>
      <article class="card mb-24">
        <h1 class="title">{{ article.title }}</h1>
        <div class="meta flex gap-16 flex-wrap mt-8">
          <span>📅 {{ formatDate(article.publishTime || article.createTime) }}</span>
          <span>👁️ {{ article.viewCount || 0 }} 阅读</span>
          <span>💬 {{ article.commentCount || 0 }} 评论</span>
          <span v-if="article.isTop" class="tag tag-sm">置顶</span>
        </div>
        <img v-if="article.cover" :src="article.cover" class="cover mt-16" alt="cover" />
        <div class="content mt-24">
          <p v-for="(line, i) in article.content.split('\n')" :key="i" class="content-line">
            {{ line }}
          </p>
        </div>

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
            <span style="color: #909399; font-size: 12px">评论将公开显示</span>
            <button
              class="btn btn-primary"
              :disabled="commentSubmitting"
              @click="submitComment"
            >
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
                onerror="this.style.display='none'"
              />
              <div v-else class="comment-avatar fallback">{{ (c.nickname || '匿').slice(0, 1) }}</div>
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
          @change="(p) => { commentPage = p; loadComments() }"
        />
      </section>
    </template>
  </div>
</template>

<style scoped>
.title {
  font-size: 26px;
  font-weight: 700;
  color: #1f2d3d;
  line-height: 1.35;
}

.meta {
  font-size: 13px;
  color: #909399;
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
  color: #2c3e50;
}

.content-line {
  margin-bottom: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.action-bar {
  padding-top: 16px;
  border-top: 1px solid #f2f6fc;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2d3d;
  margin-bottom: 16px;
}

.comment-list {
  list-style: none;
}

.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #f2f6fc;
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
  background: linear-gradient(135deg, #4a90d9, #67a7e0);
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
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-body {
  font-size: 14px;
  color: #303133;
  line-height: 1.7;
  padding-left: 48px;
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

@media (max-width: 640px) {
  .title {
    font-size: 22px;
  }
  .comment-body {
    padding-left: 0;
  }
}
</style>
