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
  content: '',
})
const commentSubmitting = ref(false)
const commentError = ref('')
const commentTextareaRef = ref<HTMLTextAreaElement | null>(null)

// ========== Emoji 表情选择器 ==========
const emojiPickerOpen = ref(false)
const emojiSearch = ref('')
const activeCategory = ref('smileys')

interface EmojiItem {
  char: string
  name: string
}

const emojiCategories = [
  { key: 'smileys', label: '😊 表情' },
  { key: 'gestures', label: '👋 手势' },
  { key: 'animals', label: '🐾 动物' },
  { key: 'food', label: '🍔 食物' },
  { key: 'travel', label: '🚗 旅行' },
  { key: 'activities', label: '⚽ 活动' },
  { key: 'objects', label: '💡 物品' },
  { key: 'symbols', label: '❤️ 符号' },
]

const emojiMap: Record<string, EmojiItem[]> = {
  smileys: [
    { char: '😀', name: '笑脸' }, { char: '😃', name: '大笑' }, { char: '😄', name: '开心' },
    { char: '😁', name: '露齿笑' }, { char: '😆', name: '满足' }, { char: '😅', name: '冷汗' },
    { char: '🤣', name: '笑翻' }, { char: '😂', name: '笑哭' }, { char: '🙂', name: '微笑' },
    { char: '😉', name: '眨眼' }, { char: '😊', name: '害羞' }, { char: '😇', name: '天使' },
    { char: '🥰', name: '爱心' }, { char: '😍', name: '花痴' }, { char: '🤩', name: '星星眼' },
    { char: '😘', name: '飞吻' }, { char: '😗', name: '亲吻' }, { char: '😚', name: '闭眼吻' },
    { char: '😋', name: '馋嘴' }, { char: '😛', name: '鬼脸' }, { char: '😜', name: '调皮' },
    { char: '🤪', name: '疯癫' }, { char: '😝', name: '眯眼笑' }, { char: '🤑', name: '发财' },
    { char: '🤗', name: '拥抱' }, { char: '🤭', name: '捂嘴笑' }, { char: '🤫', name: '嘘' },
    { char: '🤔', name: '思考' }, { char: '🤐', name: '闭嘴' }, { char: '🤨', name: '挑眉' },
    { char: '😐', name: '面无表情' }, { char: '😑', name: '无语' }, { char: '😶', name: '沉默' },
    { char: '😏', name: '得意' }, { char: '😒', name: '不爽' }, { char: '🙄', name: '翻白眼' },
    { char: '😬', name: '尴尬' }, { char: '😮', name: '惊讶' }, { char: '😯', name: '沉默惊讶' },
    { char: '😲', name: '震惊' }, { char: '😳', name: '脸红' }, { char: '🥺', name: '委屈' },
    { char: '😢', name: '哭泣' }, { char: '😭', name: '大哭' }, { char: '😤', name: '生气' },
    { char: '😠', name: '愤怒' }, { char: '😡', name: '暴怒' }, { char: '🤬', name: '骂人' },
    { char: '😈', name: '恶魔' }, { char: '👿', name: '魔鬼' }, { char: '💀', name: '骷髅' },
    { char: '☠️', name: '毒药' }, { char: '💩', name: '心碎' }, { char: '💔', name: '破碎的心' },
  ],
  gestures: [
    { char: '👋', name: '挥手' }, { char: '🤚', name: '手背' }, { char: '🖐️', name: '手掌' },
    { char: '✋', name: '举手' }, { char: '🖖', name: '瓦肯礼' }, { char: '👌', name: 'OK' },
    { char: '🤏', name: '捏' }, { char: '✌️', name: 'V字' }, { char: '🤞', name: '交叉手指' },
    { char: '🤟', name: '摇滚' }, { char: '🤘', name: '金属礼' }, { char: '🤙', name: '打电话' },
    { char: '👈', name: '左指' }, { char: '👉', name: '右指' }, { char: '👆', name: '上指' },
    { char: '🖕', name: '中指' }, { char: '👇', name: '下指' }, { char: '👍', name: '点赞' },
    { char: '👎', name: '踩' }, { char: '✊', name: '拳头' }, { char: '👊', name: '出拳' },
    { char: '🤛', name: '左拳' }, { char: '🤜', name: '右拳' }, { char: '👏', name: '鼓掌' },
    { char: '🙌', name: '举手庆祝' }, { char: '👐', name: '张开手' }, { char: '🤲', name: '捧手' },
    { char: '🙏', name: '合十' }, { char: '🤝', name: '握手' }, { char: '💪', name: '肌肉' },
  ],
  animals: [
    { char: '🐶', name: '狗' }, { char: '🐱', name: '猫' }, { char: '🐭', name: '老鼠' },
    { char: '🐹', name: '仓鼠' }, { char: '🐰', name: '兔子' }, { char: '🦊', name: '狐狸' },
    { char: '🐻', name: '熊' }, { char: '🐼', name: '熊猫' }, { char: '🐨', name: '考拉' },
    { char: '🐯', name: '老虎' }, { char: '🦁', name: '狮子' }, { char: '🐮', name: '牛' },
    { char: '🐷', name: '猪' }, { char: '🐸', name: '青蛙' }, { char: '🐵', name: '猴子' },
    { char: '🐔', name: '鸡' }, { char: '🐧', name: '企鹅' }, { char: '🐦', name: '鸟' },
    { char: '🐤', name: '小鸡' }, { char: '🦆', name: '鸭子' }, { char: '🦅', name: '鹰' },
    { char: '🦉', name: '猫头鹰' }, { char: '🦇', name: '蝙蝠' }, { char: '🐺', name: '狼' },
    { char: '🐴', name: '马' }, { char: '🦄', name: '独角兽' }, { char: '🐝', name: '蜜蜂' },
    { char: '🐛', name: '毛毛虫' }, { char: '🦋', name: '蝴蝶' }, { char: '🐌', name: '蜗牛' },
    { char: '🐞', name: '瓢虫' }, { char: '🐜', name: '蚂蚁' }, { char: '🦗', name: '蟋蟀' },
    { char: '🐢', name: '乌龟' }, { char: '🐍', name: '蛇' }, { char: '🦎', name: '蜥蜴' },
    { char: '🐙', name: '章鱼' }, { char: '🐠', name: '热带鱼' }, { char: '🐟', name: '鱼' },
    { char: '🐬', name: '海豚' }, { char: '🐳', name: '鲸鱼' }, { char: '🦈', name: '鲨鱼' },
  ],
  food: [
    { char: '🍎', name: '苹果' }, { char: '🍐', name: '梨' }, { char: '🍊', name: '橘子' },
    { char: '🍋', name: '柠檬' }, { char: '🍌', name: '香蕉' }, { char: '🍉', name: '西瓜' },
    { char: '🍇', name: '葡萄' }, { char: '🍓', name: '草莓' }, { char: '🍈', name: '甜瓜' },
    { char: '🍒', name: '樱桃' }, { char: '🍑', name: '桃子' }, { char: '🥭', name: '芒果' },
    { char: '🍍', name: '菠萝' }, { char: '🥥', name: '椰子' }, { char: '🥝', name: '猕猴桃' },
    { char: '🍅', name: '番茄' }, { char: '🥑', name: '牛油果' }, { char: '🥦', name: '西兰花' },
    { char: '🥬', name: '生菜' }, { char: '🥒', name: '黄瓜' }, { char: '🌶️', name: '辣椒' },
    { char: '🌽', name: '玉米' }, { char: '🥕', name: '胡萝卜' }, { char: '🧄', name: '大蒜' },
    { char: '🧅', name: '洋葱' }, { char: '🍄', name: '蘑菇' }, { char: '🥜', name: '花生' },
    { char: '🍞', name: '面包' }, { char: '🥐', name: '牛角包' }, { char: '🥖', name: '法棍' },
    { char: '🧀', name: '奶酪' }, { char: '🥚', name: '鸡蛋' }, { char: '🍳', name: '煎蛋' },
    { char: '🥓', name: '培根' }, { char: '🥩', name: '牛排' }, { char: '🍗', name: '鸡腿' },
    { char: '🍖', name: '烤肉' }, { char: '🍔', name: '汉堡' }, { char: '🍟', name: '薯条' },
    { char: '🍕', name: '披萨' }, { char: '🌭', name: '热狗' }, { char: '🥪', name: '三明治' },
    { char: '🍿', name: '爆米花' }, { char: '🧈', name: '黄油' }, { char: '🍣', name: '寿司' },
    { char: '🍜', name: '拉面' }, { char: '🍝', name: '意面' }, { char: '🍲', name: '火锅' },
    { char: '🍛', name: '咖喱饭' }, { char: '🍙', name: '饭团' }, { char: '🍚', name: '米饭' },
    { char: '🍰', name: '蛋糕' }, { char: '🧁', name: '杯子蛋糕' }, { char: '🍩', name: '甜甜圈' },
    { char: '🍪', name: '饼干' }, { char: '🍫', name: '巧克力' }, { char: '🍬', name: '糖果' },
    { char: '🍭', name: '棒棒糖' }, { char: '🍮', name: '布丁' }, { char: '☕', name: '咖啡' },
    { char: '🍵', name: '茶' }, { char: '🍶', name: '清酒' }, { char: '🍾', name: '香槟' },
    { char: '🍷', name: '红酒' }, { char: '🍸', name: '鸡尾酒' }, { char: '🍹', name: '果汁' },
    { char: '🍺', name: '啤酒' }, { char: '🥂', name: '干杯' }, { char: '🥃', name: '威士忌' },
  ],
  travel: [
    { char: '🚗', name: '汽车' }, { char: '🚕', name: '出租车' }, { char: '🚙', name: 'SUV' },
    { char: '🚌', name: '巴士' }, { char: '🚎', name: '电车' }, { char: '🏎️', name: '赛车' },
    { char: '🚓', name: '警车' }, { char: '🚑', name: '救护车' }, { char: '🚒', name: '消防车' },
    { char: '🚐', name: '面包车' }, { char: '🚚', name: '货车' }, { char: '🚛', name: '卡车' },
    { char: '🚜', name: '拖拉机' }, { char: '🛴', name: '滑板车' }, { char: '🚲', name: '自行车' },
    { char: '🛵', name: '摩托车' }, { char: '🏍️', name: '摩托赛车' }, { char: '✈️', name: '飞机' },
    { char: '🚀', name: '火箭' }, { char: '🚁', name: '直升机' }, { char: '🛳️', name: '邮轮' },
    { char: '⛵', name: '帆船' }, { char: '🚤', name: '快艇' }, { char: '🚢', name: '轮船' },
    { char: '🏖️', name: '沙滩' }, { char: '🏝️', name: '海岛' }, { char: '🏔️', name: '雪山' },
    { char: '⛰️', name: '山' }, { char: '🌋', name: '火山' }, { char: '🏕️', name: '露营' },
    { char: '🏠', name: '房子' }, { char: '🏡', name: '别墅' }, { char: '🏢', name: '办公楼' },
    { char: '🏗️', name: '施工中' }, { char: '🏰', name: '城堡' }, { char: '🗼', name: '东京塔' },
    { char: '🗽', name: '自由女神' }, { char: '🌍', name: '地球' }, { char: '🗺️', name: '地图' },
  ],
  activities: [
    { char: '⚽', name: '足球' }, { char: '🏀', name: '篮球' }, { char: '🏈', name: '橄榄球' },
    { char: '⚾', name: '棒球' }, { char: '🎾', name: '网球' }, { char: '🏐', name: '排球' },
    { char: '🏓', name: '乒乓球' }, { char: '🏸', name: '羽毛球' }, { char: '🥅', name: '球门' },
    { char: '🏒', name: '冰球' }, { char: '🏹', name: '射箭' }, { char: '⛳', name: '高尔夫' },
    { char: '🎣', name: '钓鱼' }, { char: '🤿', name: '潜水' }, { char: '🏊', name: '游泳' },
    { char: '🚴', name: '骑行' }, { char: '🧗', name: '攀岩' }, { char: '🎮', name: '游戏' },
    { char: '🎰', name: '老虎机' }, { char: '🎲', name: '骰子' }, { char: '♟️', name: '国际象棋' },
    { char: '🎯', name: '飞镖' }, { char: '🎳', name: '保龄球' }, { char: '🎸', name: '吉他' },
    { char: '🎹', name: '钢琴' }, { char: '🎺', name: '小号' }, { char: '🎻', name: '小提琴' },
    { char: '🥁', name: '鼓' }, { char: '🎤', name: '麦克风' }, { char: '🎧', name: '耳机' },
    { char: '🎬', name: '拍电影' }, { char: '🎨', name: '画画' }, { char: '🎭', name: '表演' },
  ],
  objects: [
    { char: '💡', name: '灯泡' }, { char: '🔦', name: '手电筒' }, { char: '🕯️', name: '蜡烛' },
    { char: '💻', name: '电脑' }, { char: '🖥️', name: '台式机' }, { char: '⌨️', name: '键盘' },
    { char: '🖱️', name: '鼠标' }, { char: '📱', name: '手机' }, { char: '📷', name: '相机' },
    { char: '📹', name: '摄像机' }, { char: '🎥', name: '录像机' }, { char: '📺', name: '电视' },
    { char: '⏰', name: '闹钟' }, { char: '⌚', name: '手表' }, { char: '📖', name: '书' },
    { char: '📚', name: '书籍' }, { char: '📓', name: '笔记本' }, { char: '📝', name: '备忘录' },
    { char: '✏️', name: '铅笔' }, { char: '🖊️', name: '钢笔' }, { char: '✂️', name: '剪刀' },
    { char: '📎', name: '回形针' }, { char: '📌', name: '图钉' }, { char: '🗑️', name: '垃圾桶' },
    { char: '🔒', name: '锁' }, { char: '🔑', name: '钥匙' }, { char: '🔨', name: '锤子' },
    { char: '🛠️', name: '工具' }, { char: '⚙️', name: '齿轮' }, { char: '🧲', name: '磁铁' },
    { char: '💊', name: '药丸' }, { char: '🩹', name: '创可贴' }, { char: '🧪', name: '试管' },
    { char: '🎁', name: '礼物' }, { char: '🎈', name: '气球' }, { char: '🎀', name: '蝴蝶结' },
  ],
  symbols: [
    { char: '❤️', name: '红心' }, { char: '🧡', name: '橙心' }, { char: '💛', name: '黄心' },
    { char: '💚', name: '绿心' }, { char: '💙', name: '蓝心' }, { char: '💜', name: '紫心' },
    { char: '🖤', name: '黑心' }, { char: '🤍', name: '白心' }, { char: '🤎', name: '棕心' },
    { char: '💯', name: '满分' }, { char: '💢', name: '怒气' }, { char: '💥', name: '爆炸' },
    { char: '💫', name: '眩晕' }, { char: '💦', name: '汗水' }, { char: '💨', name: '风' },
    { char: '💤', name: '困' }, { char: '⭐', name: '星星' }, { char: '🌟', name: '星光' },
    { char: '✨', name: '闪烁' }, { char: '🔥', name: '火焰' }, { char: '💧', name: '水滴' },
    { char: '🌈', name: '彩虹' }, { char: '☀️', name: '太阳' }, { char: '🌙', name: '月亮' },
    { char: '⚡', name: '闪电' }, { char: '❄️', name: '雪花' }, { char: '☁️', name: '云' },
    { char: '⭕', name: '圆圈' }, { char: '✅', name: '对勾' }, { char: '❌', name: '叉号' },
    { char: '⚠️', name: '警告' }, { char: '🚫', name: '禁止' }, { char: '♻️', name: '回收' },
    { char: '🔰', name: '新手' }, { char: '🈯', name: '指' }, { char: '🈲', name: '禁' },
    { char: '㊙️', name: '秘' }, { char: '🉐', name: '得' }, { char: '©️', name: '版权' },
    { char: '®️', name: '注册商标' }, { char: '™️', name: '商标' },
  ],
}

const filteredEmojis = computed(() => {
  const list = emojiMap[activeCategory.value] || []
  if (!emojiSearch.value.trim()) return list
  const keyword = emojiSearch.value.trim().toLowerCase()
  return list.filter(
    (e) => e.name.includes(keyword) || e.char.includes(keyword),
  )
})

function toggleEmojiPicker() {
  emojiPickerOpen.value = !emojiPickerOpen.value
}

function filterEmojis() {
  // 搜索由 computed filteredEmojis 自动处理，无需额外逻辑
  // 保留此函数供模板 @input 绑定使用
}

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
  if (!commentForm.content.trim()) {
    commentError.value = '请输入评论内容'
    return
  }
  commentError.value = ''
  commentSubmitting.value = true
  try {
    await addComment({
      articleId: articleId.value,
      nickname: '匿名用户',
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
              <div class="form-item">
                <div class="emoji-toolbar">
                  <button
                    class="emoji-toggle-btn"
                    :class="{ active: emojiPickerOpen }"
                    @click.stop="toggleEmojiPicker"
                    title="插入表情"
                  >
                    😊
                  </button>
                  <div v-if="emojiPickerOpen" class="emoji-picker-wrapper" @click.stop>
                    <div class="emoji-picker-header">
                      <input
                        v-model="emojiSearch"
                        class="emoji-search-input"
                        placeholder="搜索表情..."
                        @input="filterEmojis"
                      />
                    </div>
                    <div class="emoji-categories">
                      <button
                        v-for="cat in emojiCategories"
                        :key="cat.key"
                        class="emoji-cat-btn"
                        :class="{ active: activeCategory === cat.key }"
                        @click="activeCategory = cat.key"
                      >
                        {{ cat.label }}
                      </button>
                    </div>
                    <div class="emoji-grid">
                      <button
                        v-for="e in filteredEmojis"
                        :key="e.char"
                        class="emoji-item"
                        @click="insertEmoji(e.char)"
                        :title="e.name"
                      >
                        {{ e.char }}
                      </button>
                    </div>
                  </div>
                </div>
                <textarea
                  ref="commentTextareaRef"
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

/* ========== Emoji 表情选择器样式 ========== */
.emoji-toolbar {
  position: relative;
  margin-bottom: 8px;
}

.emoji-toggle-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 6px;
  background: var(--bg-card, #fff);
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  &:hover {
    background: var(--bg-hover, #f3f4f6);
    border-color: var(--primary-color, #3b82f6);
  }
  &.active {
    background: var(--primary-color, #3b82f6);
    border-color: var(--primary-color, #3b82f6);
    color: #fff;
  }
}

.emoji-picker-wrapper {
  position: absolute;
  top: 40px;
  left: 0;
  z-index: 100;
  width: 320px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 10px;
  max-height: 360px;
  display: flex;
  flex-direction: column;
}

.emoji-picker-header {
  margin-bottom: 8px;
}

.emoji-search-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  background: var(--bg-input, #f9fafb);
  &:focus {
    border-color: var(--primary-color, #3b82f6);
  }
}

.emoji-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.emoji-cat-btn {
  padding: 3px 8px;
  border: none;
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary, #6b7280);
  transition: all 0.15s;
  &:hover {
    background: var(--bg-hover, #f3f4f6);
  }
  &.active {
    background: var(--primary-color, #3b82f6);
    color: #fff;
  }
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  padding-right: 2px;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--border-color, #e5e7eb);
    border-radius: 2px;
  }
}

.emoji-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.15s;
  &:hover {
    background: var(--bg-hover, #f3f4f6);
    transform: scale(1.15);
  }
}
</style>
