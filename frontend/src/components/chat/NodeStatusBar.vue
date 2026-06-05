<script setup lang="ts">
import { useNodeStatus } from '@/composables/useNodeStatus'

const { status, label, active } = useNodeStatus()

function getStatusIcon(): string {
  switch (status.value) {
    case 'recalling':
      return 'i-solar-history-bold-duotone'
    case 'thinking':
      return 'i-solar-cpu-bold-duotone'
    case 'answering':
      return 'i-solar-chat-square-call-bold-duotone'
    case 'tool_calling':
      return 'i-solar-settings-bold-duotone'
    case 'node_processing':
      return 'i-solar-refresh-circle-linear'
    case 'failed':
      return 'i-solar-danger-circle-bold-duotone'
    default:
      return 'i-solar-info-circle-bold-duotone'
  }
}
</script>

<template>
  <div class="status-bar" :class="[`status-${status}`, { active }]">
    <span v-if="active" :class="getStatusIcon()" class="status-icon" />
    <span v-else class="dot" />
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

.status-icon {
  font-size: 14px;
  flex-shrink: 0;
}

/* 活跃状态下图标旋转 */
.status-bar.active .status-icon {
  animation: rotate 2s linear infinite;
}

.status-bar.active .dot {
  animation: pulse 1.4s ease-in-out infinite;
}

/* ---- 各状态颜色 ---- */
.status-recalling { color: var(--color-primary-strong); }
.status-recalling .dot { background: var(--color-primary); }
.status-recalling .status-icon { color: var(--color-primary); }

.status-thinking { color: var(--color-primary-strong); }
.status-thinking .dot { background: var(--color-accent-aqua); }
.status-thinking .status-icon { color: var(--color-accent-aqua); }

.status-answering { color: var(--color-success); }
.status-answering .dot { background: var(--color-success); }
.status-answering .status-icon { color: var(--color-success); }

.status-tool_calling { color: var(--color-warning); }
.status-tool_calling .dot { background: var(--color-warning); }
.status-tool_calling .status-icon { color: var(--color-warning); }

.status-node_processing { color: var(--color-info); }
.status-node_processing .dot { background: var(--color-info); }
.status-node_processing .status-icon { color: var(--color-info); }

.status-failed { color: var(--color-danger); }
.status-failed .dot { background: var(--color-danger); }
.status-failed .status-icon { color: var(--color-danger); }

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

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
