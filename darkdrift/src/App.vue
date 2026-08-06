<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
import ControlPanel from '@/components/ControlPanel.vue'
import MouseEffects from '@/components/MouseEffects.vue'

useTheme()
</script>

<template>
  <router-view />
  <MouseEffects />
  <ControlPanel />
</template>
