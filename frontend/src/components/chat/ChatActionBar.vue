<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { NButton, NPopconfirm, NTooltip, useMessage } from 'naive-ui'
import { useSessionStore } from '@/stores/session'
import { useChatStore } from '@/stores/chat'
import { sessionService } from '@/services/sessionService'
import { chatService } from '@/services/chatService'

const session = useSessionStore()
const chat = useChatStore()
const { current } = storeToRefs(session)
const message = useMessage()

const hasSession = computed(() => current.value !== null)

async function handleNew() {
  try {
    const created = await sessionService.create()
    chat.reset()
    message.success(`已创建新对话 #${created.id}`)
  } catch (e) {
    message.error(extract(e, '创建会话失败'))
  }
}

async function handleClear() {
  if (!current.value) return
  try {
    await chatService.clearHistory(current.value.id)
    message.success('已清空当前对话记录')
  } catch (e) {
    message.error(extract(e, '清空失败'))
  }
}

function handleExport() {
  if (!current.value) return
  const items = chat.messages.map((m) => ({
    role: m.role,
    text: m.text,
    status: m.status,
    createdAt: new Date(m.createdAt).toISOString(),
  }))
  const md = items
    .map((m) => `**${m.role === 'user' ? '我' : 'AI'}** · ${m.createdAt}\n\n${m.text}`)
    .join('\n\n---\n\n')
  download(`session_${current.value.id}.md`, md, 'text/markdown')
  message.success('已导出 Markdown')
}

function download(name: string, content: string, mime: string) {
  const blob = new Blob([content], { type: `${mime};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}

function extract(err: unknown, fallback: string) {
  return err instanceof Error ? err.message : fallback
}
</script>

<template>
  <div class="action-bar">
    <div class="top-row">
      <span class="label">{{ current ? `会话 #${current.id}` : '尚未选择会话' }}</span>
      <span v-if="current" class="status-pill">{{ current.status }}</span>
    </div>
    <div class="button-row">
      <NTooltip :delay="200">
        <template #trigger>
          <NButton size="small" tertiary class="action-btn" @click="handleNew">
            <template #icon>
              <span class="i-solar-add-square-bold-duotone" />
            </template>
            新建对话
          </NButton>
        </template>
        创建并切换到一个全新的会话
      </NTooltip>

      <NPopconfirm :positive-text="'清空'" :negative-text="'取消'" @positive-click="handleClear">
        <template #trigger>
          <NButton size="small" tertiary class="action-btn" :disabled="!hasSession">
            <template #icon>
              <span class="i-solar-trash-bin-2-bold-duotone" />
            </template>
            清空记录
          </NButton>
        </template>
        清空当前会话的全部消息？该操作不可撤销。
      </NPopconfirm>

      <NButton size="small" tertiary class="action-btn" :disabled="!hasSession" @click="handleExport">
        <template #icon>
          <span class="i-solar-download-bold-duotone" />
        </template>
        导出
      </NButton>
    </div>
  </div>
</template>

<style scoped>
.action-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 16px;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
}

.top-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-text-primary);
  font-weight: 500;
  min-width: 0;
}

.label {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-pill {
  font-size: 11px;
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  padding: 2px 8px;
  border-radius: var(--radius-pill);
}

.button-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.action-btn {
  width: 100%;
  text-align: center;
}

.action-btn :deep(.n-button__content) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  line-height: 1;
}

.action-btn :deep(.n-button__icon) {
  margin: 0 !important;
  display: flex;
  align-items: center;
}
</style>
