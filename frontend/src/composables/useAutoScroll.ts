import { nextTick, type Ref } from 'vue'

/**
 * 在容器内自动滚动到底部。使用 ref 而不是 selector，避免组件多实例冲突。
 */
export function useAutoScroll(container: Ref<HTMLElement | null>) {
  function scrollToBottom(smooth = true) {
    void nextTick(() => {
      const el = container.value
      if (!el) return
      el.scrollTo({ top: el.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
    })
  }

  return { scrollToBottom }
}
