<script setup lang="ts">
import ChatActionBar from '@/components/chat/ChatActionBar.vue'
import MessageList from '@/components/chat/MessageList.vue'
import NodeStatusBar from '@/components/chat/NodeStatusBar.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
</script>

<template>
  <section class="chat-panel">
    <ChatActionBar class="block" />
    <MessageList class="message-area" />
    <NodeStatusBar class="block" />
    <ChatInput class="block input-area" />
  </section>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.block {
  flex-shrink: 0;
}

.message-area {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.input-area {
  border-top: 1px solid var(--color-border-light);
}
</style>
