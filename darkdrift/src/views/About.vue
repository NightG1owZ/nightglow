<script setup lang="ts">
</script>

<template>
  <div class="page">
    <div class="card">
      <h1 class="page-title">关于本站</h1>
      <div class="divider"></div>

      <div class="about-section contact">
        <p class="about-content">
          Github: https://github.com/NightG1owZ
        </p>
        <p class="about-content">
          Gitee: https://gitee.com/infnoon
        </p>
        <p class="about-content">
          微信公众号：无限长的下午
        </p>
        <p class="about-content">
          QQ: 3112428897
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
</style>
