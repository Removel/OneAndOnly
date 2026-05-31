<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { NButton, NTooltip, NTag } from 'naive-ui'
import { useUiStore } from '@/stores/ui'
import { useConnectionStore } from '@/stores/connection'
import SessionSwitcher from '@/components/session/SessionSwitcher.vue'

const router = useRouter()
const route = useRoute()
const ui = useUiStore()
const connection = useConnectionStore()
const { isMobile } = storeToRefs(ui)

type Action = {
  key: 'settings' | 'sessions' | 'help' | 'about'
  label: string
  icon: string
  mobileOnly?: boolean
}

const actions: Action[] = [
  { key: 'sessions', label: '对话列表', icon: 'i-solar-chat-line-bold-duotone', mobileOnly: true },
  { key: 'settings', label: '设置', icon: 'i-solar-settings-bold-duotone' },
  { key: 'help', label: '帮助', icon: 'i-solar-question-circle-bold-duotone' },
  { key: 'about', label: '介绍', icon: 'i-solar-info-circle-bold-duotone' },
]

const visibleActions = computed(() => actions.filter((a) => !a.mobileOnly || isMobile.value))

const currentHelpTab = computed(() => route.query.tab)

function isActionActive(action: Action) {
  if (action.key === 'help' || action.key === 'about') {
    // 对于帮助和关于按钮，检查当前活动的标签页
    return currentHelpTab.value === action.key
  }
  // 对于其他按钮，简单检查当前路由是否是help页面
  return false
}

function handle(action: Action) {
  switch (action.key) {
    case 'settings':
      ui.openDrawer('settings')
      break
    case 'sessions':
      ui.openDrawer('sessions')
      break
    case 'help':
      router.push({ name: 'help', query: { tab: 'help' } })
      break
    case 'about':
      router.push({ name: 'help', query: { tab: 'about' } })
      break
  }
}
</script>

<template>
  <header class="banner">
    <div class="banner-left">
      <RouterLink to="/" class="brand">
        <span class="logo" />
        <span class="title">One and Only</span>
        <span class="subtitle">陪伴在你身边</span>
      </RouterLink>
    </div>
    <div class="banner-right">
      <NTag
        :type="connection.reachable ? 'success' : 'warning'"
        :bordered="false"
        size="small"
        round
        class="status-tag"
      >
        <template #icon>
          <span class="status-dot" :class="{ on: connection.reachable }" />
        </template>
        {{ connection.reachable ? '已连接' : '离线' }}
      </NTag>
      <SessionSwitcher v-if="!isMobile" class="session-switcher" />
      <NTooltip
        v-for="action in visibleActions"
        :key="action.key"
        trigger="hover"
        placement="bottom"
        :delay="200"
      >
        <template #trigger>
          <NButton
            quaternary
            circle
            class="banner-btn"
            :class="{ active: isActionActive(action) }"
            @click="handle(action)"
          >
            <template #icon>
              <span :class="action.icon" style="font-size: 20px" />
            </template>
          </NButton>
        </template>
        {{ action.label }}
      </NTooltip>
    </div>
  </header>
</template>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 24px;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-light);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 30;
}

.banner-left .brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--color-text-primary);
}

.logo {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-accent-aqua), var(--color-primary));
  box-shadow: var(--shadow-card);
}

.title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-left: 4px;
}

.banner-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.session-switcher {
  margin-left: 4px;
  margin-right: 6px;
}

.status-tag {
  margin-right: 4px;
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--color-text-tertiary);
}

.status-dot.on {
  background: var(--color-success);
  box-shadow: 0 0 0 3px rgb(95 191 168 / 25%);
}

.banner-btn {
  color: var(--color-text-secondary) !important;
  background: var(--color-bg-soft) !important;
}

.banner-btn:hover {
  color: var(--color-primary-strong) !important;
  background: var(--color-bg-hover) !important;
}

.banner-btn.active {
  color: var(--color-primary-strong) !important;
  background: var(--color-primary-soft) !important;
}

@media (max-width: 767.98px) {
  .banner {
    padding: 0 14px;
  }

  .subtitle {
    display: none;
  }
}
</style>
