<script setup lang="ts">
import { NConfigProvider, NMessageProvider } from 'naive-ui'
import { themeOverrides } from '@/styles/naive-theme'
</script>

<template>
  <NConfigProvider :theme-overrides="themeOverrides">
    <NMessageProvider>
      <RouterView />
    </NMessageProvider>
  </NConfigProvider>
</template>

<style scoped>
:deep(.n-config-provider) {
  height: 100%;
}
</style>
