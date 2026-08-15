<script setup lang="ts">
import { onMounted } from 'vue'
import { useTheme } from '@/composables/useTheme'
import { useUserStore } from '@/stores/user'
import ControlPanel from '@/components/ControlPanel.vue'
import MouseEffects from '@/components/MouseEffects.vue'

useTheme()

const userStore = useUserStore()
// 应用启动时根据会话 Cookie 恢复登录状态
onMounted(() => {
  userStore.fetchCurrentUser()
})
</script>

<template>
  <router-view />
  <MouseEffects />
  <ControlPanel />
</template>
