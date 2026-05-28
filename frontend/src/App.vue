<script setup lang="ts">
import { NConfigProvider, NLoadingBarProvider, NMessageProvider } from 'naive-ui'
import { themeOverrides } from '@/styles/naive-theme'
</script>
<template>
  <NConfigProvider :theme-overrides="themeOverrides">
    <NLoadingBarProvider>
      <NMessageProvider>
        <RouterView />
      </NMessageProvider>
    </NLoadingBarProvider>
  </NConfigProvider>
</template>

<style scoped>
:deep(.n-config-provider) {
  height: 100%;
}
</style>
