import { onBeforeUnmount, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'

const QUERY_MOBILE = '(max-width: 767.98px)'
const QUERY_TABLET = '(min-width: 768px) and (max-width: 1279.98px)'

/**
 * 监听断点并写回 ui store。组件层不要再各自监听 window.matchMedia。
 */
export function useResponsive() {
  const ui = useUiStore()
  const mqMobile = window.matchMedia(QUERY_MOBILE)
  const mqTablet = window.matchMedia(QUERY_TABLET)

  function sync() {
    ui.setBreakpoint(mqMobile.matches, mqTablet.matches)
  }

  onMounted(() => {
    sync()
    mqMobile.addEventListener('change', sync)
    mqTablet.addEventListener('change', sync)
  })
  onBeforeUnmount(() => {
    mqMobile.removeEventListener('change', sync)
    mqTablet.removeEventListener('change', sync)
  })
}
