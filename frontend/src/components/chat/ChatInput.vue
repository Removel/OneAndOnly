<script setup lang="ts">
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { NButton, NTooltip, useMessage } from 'naive-ui'
import { useChatStore } from '@/stores/chat'
import { useSessionStore } from '@/stores/session'
import { useConnectionStore } from '@/stores/connection'
import { chatService } from '@/services/chatService'

const chat = useChatStore()
const session = useSessionStore()
const connection = useConnectionStore()
const { sending } = storeToRefs(chat)
const message = useMessage()

const text = ref('')

const disabled = computed(() => sending.value || !connection.reachable || session.currentId == null)

const placeholder = computed(() => {
  if (!connection.reachable) return '后端未连接，发送已禁用'
  if (session.currentId == null) return '请先选择或新建一个会话'
  return '在这里输入对话…   Enter 发送 / Shift + Enter 换行'
})

async function handleSend() {
  if (disabled.value) return
  const content = text.value.trim()
  if (!content) return
  text.value = ''
  try {
    await chatService.sendMessage(session.currentId!, content)
  } catch (e) {
    message.error(e instanceof Error ? e.message : '发送失败')
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    void handleSend()
  }
}
</script>

<template>
  <div class="chat-input">
    <textarea
      id="chat-input-textarea"
      name="chat-input"
      v-model="text"
      class="textarea"
      rows="3"
      :placeholder="placeholder"
      :disabled="disabled && !sending"
      @keydown="onKeydown"
    />
    <div class="toolbar">
      <div class="left">
        <NTooltip :delay="200">
          <template #trigger>
            <NButton size="small" quaternary disabled>
              <template #icon>
                <span class="i-solar-microphone-3-bold-duotone" />
              </template>
            </NButton>
          </template>
          语音输入即将上线
        </NTooltip>
        <NTooltip :delay="200">
          <template #trigger>
            <NButton size="small" quaternary disabled>
              <template #icon>
                <span class="i-solar-emoji-funny-circle-bold-duotone" />
              </template>
            </NButton>
          </template>
          表情面板（敬请期待）
        </NTooltip>
        <NTooltip :delay="200">
          <template #trigger>
            <NButton size="small" quaternary disabled>
              <template #icon>
                <span class="i-solar-paperclip-bold-duotone" />
              </template>
            </NButton>
          </template>
          附件（敬请期待）
        </NTooltip>
      </div>
      <div class="right">
        <NButton
          type="primary"
          size="small"
          :loading="sending"
          :disabled="disabled"
          @click="handleSend"
        >
          发送
          <template #icon>
            <span class="i-solar-plain-2-bold-duotone" />
          </template>
        </NButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px 14px;
  background: var(--color-bg-card);
}

.textarea {
  width: 100%;
  resize: none;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  font: inherit;
  font-size: 15px;
  line-height: 1.6;
  background: var(--color-bg-soft);
  color: var(--color-text-primary);
  transition:
    border-color 0.2s ease,
    background 0.2s ease;
  outline: none;
  max-height: 180px;
}

.textarea:focus {
  border-color: var(--color-primary);
  background: var(--color-bg-card);
}

.textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.left,
.right {
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
