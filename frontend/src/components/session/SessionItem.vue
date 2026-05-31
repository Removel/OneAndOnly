<script setup lang="ts">
import { computed } from 'vue'
import { NIcon, NPopconfirm } from 'naive-ui'
import type { SessionResponseDTO } from '@/types/session'

const props = defineProps<{
  session: SessionResponseDTO
  active: boolean
}>()

const emit = defineEmits<{
  (e: 'select'): void
  (e: 'delete'): void
}>()

const subtitle = computed(() => {
  const ts = props.session.last_activity_at ?? props.session.updated_at ?? props.session.created_at
  if (!ts) return '尚未活动'
  const d = new Date(ts)
  return d.toLocaleString('zh-CN', { hour12: false })
})
</script>

<template>
  <li
    class="item"
    :class="{ active }"
    role="button"
    tabindex="0"
    @click="emit('select')"
    @keydown.enter.prevent="emit('select')"
  >
    <div class="info">
      <p class="title">会话 #{{ session.id }}</p>
      <p class="subtitle">
        <span class="badge" :data-status="session.status">{{ session.status }}</span>
        <span>{{ subtitle }}</span>
      </p>
    </div>
    <NPopconfirm @positive-click="emit('delete')">
      <template #trigger>
        <button class="delete-btn" type="button" @click.stop>
          <span class="i-solar-trash-bin-2-bold-duotone" style="font-size: 16px" />
        </button>
      </template>
      删除该会话？该操作不可撤销。
    </NPopconfirm>
  </li>
</template>

<style scoped>
.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    background 0.2s ease,
    border-color 0.2s ease;
}

.item:hover {
  background: var(--color-accent-foam);
  border-color: var(--color-border-light);
}

.item.active {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}

.info {
  min-width: 0;
}

.title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.subtitle {
  margin: 4px 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.badge {
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  font-size: 11px;
}

.delete-btn {
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.delete-btn:hover {
  background: rgb(224 120 120 / 12%);
  color: var(--color-danger);
}
</style>
