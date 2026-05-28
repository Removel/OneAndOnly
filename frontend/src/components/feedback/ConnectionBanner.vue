<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { NButton, NIcon } from 'naive-ui'
import { useConnectionStore } from '@/stores/connection'

const connection = useConnectionStore()
const { reachable, checking } = storeToRefs(connection)
</script>

<template>
  <transition name="slide-down">
    <div v-if="!reachable" class="banner">
      <span class="i-solar-cloud-cross-bold-duotone icon" />
      <p class="text">后端未连接，发送已禁用。请确认 backend 服务在 8000 端口运行。</p>
      <NButton size="tiny" tertiary :loading="checking" @click="connection.check()">
        <template #icon>
          <NIcon><span class="i-solar-refresh-bold-duotone" /></NIcon>
        </template>
        重试
      </NButton>
    </div>
  </transition>
</template>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgb(240 184 96 / 18%);
  border-bottom: 1px solid rgb(240 184 96 / 35%);
  color: var(--color-text-primary);
  font-size: 13px;
}

.icon {
  color: var(--color-warning);
  font-size: 18px;
}

.text {
  margin: 0;
  flex: 1;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
