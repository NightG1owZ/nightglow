<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getConfigByKey } from '@/api/config'

const siteDesc = ref('')
const siteKeywords = ref('')
const loading = ref(false)

async function loadConfigs() {
  loading.value = true
  try {
    const [desc, kw] = await Promise.allSettled([
      getConfigByKey('site_description'),
      getConfigByKey('site_keywords'),
    ])
    if (desc.status === 'fulfilled') siteDesc.value = desc.value?.configValue || ''
    if (kw.status === 'fulfilled') siteKeywords.value = kw.value?.configValue || ''
  } finally {
    loading.value = false
  }
}

onMounted(loadConfigs)
</script>

<template>
  <div class="page">
    <div class="card">
      <h1 class="page-title">ℹ️ 关于本站</h1>
      <div class="divider"></div>

      <div v-if="siteDesc" class="about-section">
        <h2 class="section-title">站点介绍</h2>
        <p class="about-content">{{ siteDesc }}</p>
      </div>

      <div class="about-section">
        <h2 class="section-title">技术栈</h2>
        <div class="tech-grid">
          <div class="tech-item">
            <div class="tech-icon">⚡</div>
            <div class="tech-name">Vue 3</div>
            <div class="tech-desc">前端框架</div>
          </div>
          <div class="tech-item">
            <div class="tech-icon">📘</div>
            <div class="tech-name">TypeScript</div>
            <div class="tech-desc">类型系统</div>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🚀</div>
            <div class="tech-name">Vite</div>
            <div class="tech-desc">构建工具</div>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🐍</div>
            <div class="tech-name">FastAPI</div>
            <div class="tech-desc">后端服务</div>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🗄️</div>
            <div class="tech-name">MySQL</div>
            <div class="tech-desc">数据存储</div>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🍍</div>
            <div class="tech-name">Pinia</div>
            <div class="tech-desc">状态管理</div>
          </div>
        </div>
      </div>

      <div v-if="siteKeywords" class="about-section">
        <h2 class="section-title">关键词</h2>
        <div class="keywords-wrap">
          <span v-for="(kw, i) in siteKeywords.split(/[,，\s]+/)" :key="i" class="tag">
            #{{ kw }}
          </span>
        </div>
      </div>

      <div class="about-section">
        <h2 class="section-title">功能特性</h2>
        <ul class="feature-list">
          <li>✅ 文章发布、分类、标签管理</li>
          <li>✅ 文章浏览量统计（IP去重）</li>
          <li>✅ 文章点赞/取消点赞（IP去重）</li>
          <li>✅ 多级评论与回复</li>
          <li>✅ 用户注册 / 登录 / 权限控制</li>
          <li>✅ 响应式布局，适配移动端</li>
        </ul>
      </div>

      <div class="about-section contact">
        <h2 class="section-title">联系我们</h2>
        <p class="about-content">
          如有任何问题或建议，欢迎通过评论或邮件与我们联系。
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0;
}

.divider {
  height: 1px;
  background: var(--border-lighter);
  margin: 16px 0 24px;
}

.about-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.about-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.85;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.tech-item {
  background: var(--bg-subtle);
  border-radius: 8px;
  padding: 20px 16px;
  text-align: center;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.3s ease;
}

.tech-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.tech-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.tech-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.tech-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

.keywords-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 8px 20px;
}

.feature-list li {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 2;
}
</style>
