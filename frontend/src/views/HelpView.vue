<script setup lang="ts">
import { NCard } from 'naive-ui'
</script>

<template>
  <main class="help flex items-center justify-center min-h-100dvh p-6">
    <NCard class="card" content-style="padding: 32px;">
      <h1 class="m-0 mb-2 text-text-primary">帮助 / 介绍</h1>
      <p class="text-text-secondary mt-0">占位页，后续补充说明。</p>
    </NCard>
  </main>
</template>

<style scoped>
.help {
  background: var(--color-bg-base);
}

.card {
  max-width: 520px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
</style>
