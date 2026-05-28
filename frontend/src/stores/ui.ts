import { defineStore } from 'pinia'
import { ref } from 'vue'

export type DrawerKind = 'none' | 'settings' | 'sessions' | 'help'

export const useUiStore = defineStore('ui', () => {
  const drawer = ref<DrawerKind>('none')
  const isMobile = ref(false)
  const isTablet = ref(false)
  const showDebug = ref(false)

  function openDrawer(kind: Exclude<DrawerKind, 'none'>) {
    drawer.value = kind
  }

  function closeDrawer() {
    drawer.value = 'none'
  }

  function setBreakpoint(mobile: boolean, tablet: boolean) {
    isMobile.value = mobile
    isTablet.value = tablet
  }

  function toggleDebug() {
    showDebug.value = !showDebug.value
  }

  return {
    drawer,
    isMobile,
    isTablet,
    showDebug,
    openDrawer,
    closeDrawer,
    setBreakpoint,
    toggleDebug,
  }
})
