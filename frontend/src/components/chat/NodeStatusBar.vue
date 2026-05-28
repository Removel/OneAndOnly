<script setup lang="ts">
import { useNodeStatus } from '@/composables/useNodeStatus'

const { status, label, active } = useNodeStatus()
</script>

<template>
  <div class="status-bar" :class="[`status-${status}`, { active }]">
    <span class="dot" />
    <span class="text">{{ label }}</span>
  </div>
</template>

<style scoped>
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: var(--color-bg-soft);
  border-top: 1px solid var(--color-border-light);
  transition: color 0.3s ease;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--color-text-tertiary);
  transition: background 0.3s ease;
}

.status-bar.active .dot {
  animation: pulse 1.4s ease-in-out infinite;
}

.status-recalling {
  color: var(--color-primary-strong);
}

.status-recalling .dot {
  background: var(--color-primary);
}

.status-thinking {
  color: var(--color-primary-strong);
}

.status-thinking .dot {
  background: var(--color-accent-aqua);
}

.status-answering {
  color: var(--color-success);
}

.status-answering .dot {
  background: var(--color-success);
}

.status-failed {
  color: var(--color-danger);
}

.status-failed .dot {
  background: var(--color-danger);
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.6);
    opacity: 0.5;
  }
}
</style>
