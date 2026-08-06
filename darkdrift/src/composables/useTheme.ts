import { watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore, type ThemeMode } from '@/stores/settings'

type ResolvedTheme = 'light' | 'dark' | 'eye-care'

function resolveTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === 'system') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return mode
}

/** 将主题应用到 <html data-theme="...">，并在系统主题变化时同步刷新 */
export function applyTheme(mode: ThemeMode) {
  document.documentElement.setAttribute('data-theme', resolveTheme(mode))
}

export function useTheme() {
  const store = useSettingsStore()
  const { theme } = storeToRefs(store)

  let mq: MediaQueryList | null = null
  const onMqChange = () => applyTheme(theme.value)

  onMounted(() => {
    applyTheme(theme.value)
    mq = window.matchMedia('(prefers-color-scheme: dark)')
    mq.addEventListener('change', onMqChange)
  })

  onUnmounted(() => {
    mq?.removeEventListener('change', onMqChange)
  })

  watch(theme, (t) => applyTheme(t))
}
