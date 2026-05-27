<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { NCard, NTag, NButton, NSpace } from 'naive-ui'
import { useConnectionStore } from '@/stores/connection'

const connection = useConnectionStore()
const { reachable, lastCheckAt, checking } = storeToRefs(connection)

onMounted(() => {
  void connection.check()
})

function formatTime(ts: number | null) {
  if (!ts) return '—'
  return new Date(ts).toLocaleTimeString()
}
</script>

<template>
  <main class="home flex items-center justify-center min-h-100dvh p-6">
    <NCard class="welcome" content-style="padding: 32px;">
      <h1 class="m-0 mb-2 text-text-primary">One and Only</h1>
      <p class="text-text-secondary mt-0">前端骨架已就绪，等待主页面接入。</p>

      <NSpace align="center" class="mt-6">
        <NTag :type="reachable ? 'success' : 'error'" round>
          后端 {{ reachable ? '已连接' : '未连接' }}
        </NTag>
        <span class="text-text-secondary text-sm">最近检查：{{ formatTime(lastCheckAt) }}</span>
        <NButton size="small" :loading="checking" @click="connection.check()">
          重新检查
        </NButton>
      </NSpace>
    </NCard>
  </main>
</template>

<style scoped>
.home {
  background: linear-gradient(135deg, var(--color-bg-base), var(--color-bg-soft));
}

.welcome {
  max-width: 520px;
  width: 100%;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
</style>
