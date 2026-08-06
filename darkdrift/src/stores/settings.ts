import { ref } from 'vue'
import { defineStore } from 'pinia'

/** 主题模式：优先级 系统默认 > 白天 > 黑夜 > 护眼 */
export type ThemeMode = 'system' | 'light' | 'dark' | 'eye-care'

/** 鼠标特效：拖尾 / 点击掉落 / 关闭 */
export type MouseEffect = 'trail' | 'click' | 'off'

const THEME_KEY = 'blog_theme'
const EFFECT_KEY = 'blog_mouse_effect'

function loadTheme(): ThemeMode {
  const v = localStorage.getItem(THEME_KEY) as ThemeMode | null
  const allowed: ThemeMode[] = ['system', 'light', 'dark', 'eye-care']
  return v && allowed.includes(v) ? v : 'system'
}

function loadEffect(): MouseEffect {
  const v = localStorage.getItem(EFFECT_KEY) as MouseEffect | null
  const allowed: MouseEffect[] = ['trail', 'click', 'off']
  return v && allowed.includes(v) ? v : 'trail'
}

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref<ThemeMode>(loadTheme())
  const mouseEffect = ref<MouseEffect>(loadEffect())

  function setTheme(t: ThemeMode) {
    theme.value = t
    localStorage.setItem(THEME_KEY, t)
  }

  function setMouseEffect(e: MouseEffect) {
    mouseEffect.value = e
    localStorage.setItem(EFFECT_KEY, e)
  }

  return { theme, mouseEffect, setTheme, setMouseEffect }
})
