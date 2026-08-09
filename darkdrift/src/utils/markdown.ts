import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
import DOMPurify from 'dompurify'

/**
 * 配置带语法高亮的 marked 实例。
 * - 启用 GFM（表格、删除线、任务列表等）
 * - 对代码块使用 highlight.js 进行高亮，未识别语言回退到 plaintext
 */
const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
      try {
        return hljs.highlight(code, { language }).value
      } catch {
        return code
      }
    },
  }),
)

marked.setOptions({
  gfm: true,
  breaks: false,
})

/**
 * 为外部链接添加 target="_blank" 和 rel="noopener noreferrer"，
 * 防止 referrer 泄漏与 tabnabbing 攻击。
 */
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A' && node.getAttribute('href')) {
    const href = node.getAttribute('href') || ''
    if (/^https?:\/\//i.test(href)) {
      node.setAttribute('target', '_blank')
      node.setAttribute('rel', 'noopener noreferrer')
    }
  }
})

/**
 * 将 Markdown 文本渲染为经过净化的安全 HTML。
 *
 * 净化策略：
 * - 移除 <script>、<iframe>、on* 事件属性等危险内容
 * - 允许 markdown 常见标签及代码高亮所需的 class 属性
 * - 外部链接自动添加安全 rel 属性
 *
 * @param content 原始 Markdown 字符串
 * @returns 可安全插入 DOM 的 HTML 字符串
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''
  const rawHtml = marked.parse(content, { async: false }) as string
  return DOMPurify.sanitize(rawHtml, {
    ADD_ATTR: ['target', 'rel'],
  })
}
