<script setup lang="ts">
import { computed } from 'vue'
import { NDrawer, NDrawerContent } from 'naive-ui'
import { useUiStore } from '@/stores/ui'
import SessionListPanel from '@/components/session/SessionListPanel.vue'
import SettingsDrawer from '@/components/settings/SettingsDrawer.vue'

const ui = useUiStore()

const placement = computed(() => (ui.isMobile ? 'bottom' : 'right'))
const widthOrHeight = computed(() => (ui.isMobile ? '78%' : 360))

const titleMap: Record<'sessions' | 'settings', string> = {
  sessions: '对话列表',
  settings: '设置',
}
</script>

<template>
  <NDrawer
    :show="ui.drawer === 'sessions'"
    :placement="placement"
    :width="widthOrHeight"
    :height="widthOrHeight"
    :auto-focus="false"
    @update:show="(v: boolean) => !v && ui.closeDrawer()"
  >
    <NDrawerContent :title="titleMap.sessions" closable :native-scrollbar="false">
      <SessionListPanel />
    </NDrawerContent>
  </NDrawer>

  <NDrawer
    :show="ui.drawer === 'settings'"
    :placement="placement"
    :width="widthOrHeight"
    :height="widthOrHeight"
    :auto-focus="false"
    @update:show="(v: boolean) => !v && ui.closeDrawer()"
  >
    <NDrawerContent :title="titleMap.settings" closable :native-scrollbar="false">
      <SettingsDrawer />
    </NDrawerContent>
  </NDrawer>
</template>
