<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useAutoScroll } from '@/composables/useAutoScroll'
import MessageBubble from '@/components/chat/MessageBubble.vue'

const chat = useChatStore()
const { messages } = storeToRefs(chat)

const scroller = ref<HTMLElement | null>(null)
const { scrollToBottom } = useAutoScroll(scroller)

watch(
  () => messages.value.length,
  () => scrollToBottom(true),
)
watch(
  () => messages.value[messages.value.length - 1]?.text,
  () => scrollToBottom(true),
)
</script>

<template>
  <div ref="scroller" class="message-list">
    <div v-if="messages.length === 0" class="empty">
      <span class="i-solar-chat-square-2-bold-duotone empty-icon" />
      <p class="title">还没有对话</p>
      <p class="hint">在下方输入框开始你的第一句话吧</p>
    </div>
    <template v-else>
      <MessageBubble v-for="m in messages" :key="m.localId" :message="m" />
    </template>
  </div>
</template>

<style scoped>
.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 18px 18px 6px;
  scrollbar-gutter: stable;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  touch-action: pan-y;
  scrollbar-width: thin;
  display: flex;
  flex-direction: column;
}

.message-list::-webkit-scrollbar {
  width: 12px;
}

.message-list::-webkit-scrollbar-track {
  background: var(--color-bg-soft);
  border-radius: 6px;
  box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.1);
}

.message-list::-webkit-scrollbar-thumb {
  background: var(--color-primary-soft);
  border-radius: 6px;
  border: 2px solid transparent;
  background-clip: padding-box;
  min-height: 20px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary-strong);
  background-clip: padding-box;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
  color: var(--color-text-tertiary);
  gap: 6px;
}

.empty-icon {
  font-size: 56px;
  color: var(--color-primary-soft);
}

.title {
  margin: 8px 0 0;
  font-size: 15px;
  color: var(--color-text-secondary);
}

.hint {
  margin: 0;
  font-size: 13px;
}
</style>
