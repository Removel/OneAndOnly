<script setup lang="ts">
import { computed, toRef } from 'vue'
import type { UiMessage } from '@/types/message'
import { useMarkdown } from '@/composables/useMarkdown'

const props = defineProps<{
  message: UiMessage
}>()

const isUser = computed(() => props.message.role === 'user')
const failed = computed(() => props.message.status === 'failed')
const pending = computed(() => props.message.status === 'pending')

const time = computed(() => formatRelative(props.message.createdAt))

const { rendered } = useMarkdown(toRef(() => props.message.text))

function formatRelative(ts: number) {
  const diff = Date.now() - ts
  if (diff < 60_000) return '刚刚'
  if (diff < 60 * 60_000) return `${Math.floor(diff / 60_000)} 分钟前`
  const d = new Date(ts)
  const today = new Date()
  if (d.toDateString() === today.toDateString()) {
    return `今天 ${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  return `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function pad(n: number) {
  return n < 10 ? `0${n}` : `${n}`
}
</script>

<template>
  <div class="bubble-row" :class="{ user: isUser }">
    <div class="avatar" :class="{ ai: !isUser }">
      <span v-if="isUser" class="i-solar-user-bold-duotone" />
      <span v-else class="i-solar-magic-stick-3-bold-duotone" />
    </div>
    <div class="bubble-wrapper">
      <div class="bubble" :class="{ user: isUser, failed, pending }">
        <p v-if="pending && !message.text" class="typing">
          <span class="dot" />
          <span class="dot" />
          <span class="dot" />
        </p>
        <div v-else class="text markdown-body" v-html="rendered" />
      </div>
      <p class="meta">
        <span>{{ time }}</span>
        <span v-if="failed" class="failed-tag">失败</span>
        <span v-else-if="message.retryTimes && message.retryTimes > 0" class="retry-tag">
          重试 {{ message.retryTimes }} 次
        </span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.bubble-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

.bubble-row.user {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.avatar.ai {
  background: linear-gradient(135deg, var(--color-accent-aqua), var(--color-primary));
  color: var(--color-text-inverse);
}

.bubble-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 78%;
}

.bubble-row.user .bubble-wrapper {
  align-items: flex-end;
}

.bubble {
  padding: 10px 14px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-soft);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  font-size: 15px;
  line-height: 1.65;
  word-break: break-word;
  box-shadow: var(--shadow-card);
  transition: border-color 0.4s ease;
}

.bubble.user {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.bubble.failed {
  background: rgb(224 120 120 / 8%);
  border-color: rgb(224 120 120 / 40%);
  color: var(--color-danger);
}

.bubble.pending {
  border-style: dashed;
  border-color: hsla(var(--aura-h), var(--aura-s), 65%, 0.6);
}

.text {
  margin: 0;
}

.typing {
  margin: 0;
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 4px 0;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary-strong);
  opacity: 0.4;
  animation: typing 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.15s;
}

.dot:nth-child(3) {
  animation-delay: 0.3s;
}

.meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 6px 4px 0;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.failed-tag {
  color: var(--color-danger);
}

.retry-tag {
  color: var(--color-warning);
}

@keyframes typing {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }

  30% {
    transform: translateY(-3px);
    opacity: 1;
  }
}
</style>
