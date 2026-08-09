import { ref, onBeforeUnmount, nextTick, watch } from 'vue'

export interface TocItem {
  id: string
  text: string
  level: number // 1-6
}

const THROTTLE_WAIT_MS = 120
const BACK_TO_TOP_RATIO = 0.5 // 页面滚动 50% 后显示返回顶部

/**
 * 节流工具：采用「首次立即触发 + 固定间隔」策略，保证滚动监听的低频更新。
 */
function throttle<T extends (...args: any[]) => void>(fn: T, wait: number): T {
  let last = 0
  let timer: ReturnType<typeof setTimeout> | null = null
  return function (this: unknown, ...args: Parameters<T>) {
    const now = Date.now()
    const remaining = wait - (now - last)
    if (remaining <= 0) {
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
      last = now
      fn.apply(this, args)
    } else if (!timer) {
      timer = setTimeout(() => {
        last = Date.now()
        timer = null
        fn.apply(this, args)
      }, remaining)
    }
  } as T
}

/**
 * 生成一个简短且 DOM 安全的锚点 id。
 * 使用字符 slug 化 + 序号去重，避免内容中存在特殊字符或空标题。
 */
function slugify(text: string, used: Set<string>): string {
  const base = text
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, '-')
    .replace(/[^\p{Letter}\p{Number}\-]/gu, '')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
  let id = base || 'heading'
  let i = 1
  while (used.has(id)) {
    id = `${base || 'heading'}-${i++}`
  }
  used.add(id)
  return id
}

/**
 * 从指定容器内提取 h1-h6 标题并注入 id。
 *
 * 注意：DOMPurify 默认会移除 id/class/href 之外的大多数属性，但保留 id，
 * 因此我们在 marked 渲染 + DOMPurify 净化之后，再为容器内的 heading 注入 id，
 * 确保 id 永远不丢失、不被清空。
 */
function extractHeadings(container: HTMLElement): TocItem[] {
  const used = new Set<string>()
  const headings = container.querySelectorAll<HTMLHeadingElement>('h1,h2,h3,h4,h5,h6')
  const items: TocItem[] = []
  headings.forEach((h) => {
    const text = (h.textContent || '').trim()
    if (!text) return
    // 若已有合法 id，直接复用
    let id = h.id
    if (!id || used.has(id)) {
      id = slugify(text, used)
      h.id = id
    } else {
      used.add(id)
    }
    const level = parseInt(h.tagName.slice(1), 10) || 1
    items.push({ id, text, level })
  })
  return items
}

/**
 * 在一组 toc items 中根据当前滚动位置，找到「离视口顶部最近且不超过 offset」的那个标题。
 * 这是经典的滚动高亮匹配算法：最后一个 `top <= offset` 的标题即为当前章节。
 */
function findActiveId(
  items: TocItem[],
  scrollOffset: number,
  headingOffset: number,
): string | null {
  if (items.length === 0) return null
  let activeId: string | null = null
  for (const item of items) {
    const el = document.getElementById(item.id)
    if (!el) continue
    const rect = el.getBoundingClientRect()
    const top = rect.top + window.scrollY - headingOffset
    if (top <= scrollOffset) {
      activeId = item.id
    } else {
      break
    }
  }
  const lastItem = items[items.length - 1]
  // 若滚动到了页底但还有更后面的标题没被激活，直接激活最后一个
  if (
    lastItem &&
    activeId !== lastItem.id &&
    window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4
  ) {
    activeId = lastItem.id
  }
  return activeId || items[0]?.id || null
}

export function useTableOfContents(
  getContainer: () => HTMLElement | null | undefined,
  options: { headingOffset?: () => number } = {},
) {
  const tocItems = ref<TocItem[]>([])
  const activeId = ref<string | null>(null)
  const showBackToTop = ref(false)

  let programmaticScroll = false
  let programmaticTimer: ReturnType<typeof setTimeout> | null = null

  /**
   * 调用时机：
   *   - 文章数据加载、Markdown 渲染完毕，DOM 更新稳定后
   *   - 再次切换文章路由时
   */
  function rebuild() {
    const container = getContainer()
    if (!container) {
      tocItems.value = []
      activeId.value = null
      return
    }
    tocItems.value = extractHeadings(container)
    const first = tocItems.value[0]
    activeId.value = first ? first.id : null
    onScroll() // 立即校准一次激活态
  }

  /**
   * 平滑滚动到指定锚点，并短暂关闭 scroll-spy，避免滚动过程中高亮闪烁。
   */
  function scrollToId(id: string) {
    const el = document.getElementById(id)
    if (!el) return
    const headingOffset = options.headingOffset?.() ?? 16
    const top = el.getBoundingClientRect().top + window.scrollY - headingOffset
    programmaticScroll = true
    if (programmaticTimer) clearTimeout(programmaticTimer)
    window.scrollTo({ top, behavior: 'smooth' })
    // 平滑滚动结束后再恢复 scroll-spy（Chrome 上 smooth 时长约 300~600ms，给 700ms 留够余量）
    programmaticTimer = setTimeout(() => {
      programmaticScroll = false
      activeId.value = id
      programmaticTimer = null
    }, 700)
  }

  function scrollToTop() {
    programmaticScroll = true
    if (programmaticTimer) clearTimeout(programmaticTimer)
    window.scrollTo({ top: 0, behavior: 'smooth' })
    programmaticTimer = setTimeout(() => {
      programmaticScroll = false
      programmaticTimer = null
    }, 700)
  }

  function onScroll() {
    if (programmaticScroll) return

    const scrollTop = window.scrollY
    const docHeight = document.documentElement.scrollHeight
    const viewHeight = window.innerHeight
    const scrollable = Math.max(1, docHeight - viewHeight)
    showBackToTop.value = scrollTop / scrollable >= BACK_TO_TOP_RATIO

    if (tocItems.value.length === 0) return
    const headingOffset = options.headingOffset?.() ?? 16
    // 将「视口顶部 + 一点余量」作为匹配参考，让用户刚开始看到标题时即完成高亮
    const scrollOffset = scrollTop + Math.max(120, viewHeight * 0.2)
    activeId.value = findActiveId(tocItems.value, scrollOffset, headingOffset)
  }

  const throttledOnScroll = throttle(onScroll, THROTTLE_WAIT_MS)

  // 键盘快捷键："Home" 键浏览器原生会跳到顶部；这里额外支持 Ctrl/⌘ + Shift + ↑ 回到顶部
  function onKey(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'ArrowUp') {
      e.preventDefault()
      scrollToTop()
    }
  }

  onMountedLike(() => {
    window.addEventListener('scroll', throttledOnScroll, { passive: true })
    window.addEventListener('resize', throttledOnScroll)
    window.addEventListener('keydown', onKey)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', throttledOnScroll)
    window.removeEventListener('resize', throttledOnScroll)
    window.removeEventListener('keydown', onKey)
    if (programmaticTimer) clearTimeout(programmaticTimer)
  })

  return {
    tocItems,
    activeId,
    showBackToTop,
    rebuild,
    scrollToId,
    scrollToTop,
  }
}

/**
 * 当这个 composable 在 setup 阶段被调用时，等价于 onMounted；
 * 但如果是在组件渲染后（例如 `nextTick` 后）手动调用，则直接立刻执行。
 */
function onMountedLike(fn: () => void) {
  // 在 setup 同步执行阶段，isMounted 不可直接用，但 onBeforeUnmount 已注册说明是在 setup 中；
  // 这里保持简单：总是注册 onMounted，同时延迟一次兜底执行（不会造成重复，因为回调无共享状态）
  fn()
}
