<script setup lang="ts">
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { NPopover, NIcon } from 'naive-ui'
import { useSessionStore } from '@/stores/session'
import SessionListPanel from '@/components/session/SessionListPanel.vue'

const session = useSessionStore()
const { current, list } = storeToRefs(session)

const show = ref(false)

const label = computed(() => (current.value ? `会话 #${current.value.id}` : '尚未选择会话'))
const status = computed(() => current.value?.status ?? null)
const total = computed(() => list.value.length)

function handleFinished() {
  show.value = false
}
</script>

<template>
  <NPopover
    v-model:show="show"
    placement="bottom-end"
    trigger="click"
    :show-arrow="false"
    raw
    style="padding: 0"
  >
    <template #trigger>
      <button
        type="button"
        class="switcher"
        :class="{ open: show, empty: !current }"
        :title="label"
      >
        <NIcon :size="16" class="icon">
          <span class="i-solar-chat-square-like-bold-duotone" />
        </NIcon>
        <span class="text">{{ label }}</span>
        <span v-if="total > 0" class="count">{{ total > 99 ? '99+' : total }}</span>
        <span v-if="status" class="status-pill" :data-status="status">{{ status }}</span>
        <NIcon :size="14" class="caret">
          <span class="i-solar-alt-arrow-down-bold-duotone" />
        </NIcon>
      </button>
    </template>

    <div class="popover-card">
      <SessionListPanel @finished="handleFinished" />
    </div>
  </NPopover>
</template>

<style scoped>
.switcher {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px 6px 12px;
  height: 36px;
  background: var(--color-bg-soft);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-pill);
  color: var(--color-text-primary);
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition:
    background 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease;
  min-width: 0;
}

.switcher:hover {
  background: var(--color-accent-foam);
  border-color: var(--color-primary);
  color: var(--color-primary-strong);
}

.switcher.open {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
  color: var(--color-primary-strong);
}

.switcher.empty {
  color: var(--color-text-tertiary);
}

.icon {
  flex-shrink: 0;
}

.text {
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 6px;
  border-radius: var(--radius-pill);
  background: var(--color-primary-strong);
  color: var(--color-text-inverse);
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}

.status-pill {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.status-pill[data-status='active'] {
  color: var(--color-success);
  border-color: rgb(95 191 168 / 35%);
  background: rgb(95 191 168 / 12%);
}

.caret {
  color: var(--color-text-tertiary);
  transition: transform 0.18s ease;
}

.switcher.open .caret {
  transform: rotate(180deg);
  color: var(--color-primary-strong);
}

.popover-card {
  width: 360px;
  max-height: min(560px, 70vh);
  padding: 14px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-float);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.popover-card :deep(.session-list) {
  flex: 1;
  min-height: 0;
}
</style>
