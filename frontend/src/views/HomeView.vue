<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMessage } from 'naive-ui'
import AppTopBanner from '@/components/layout/AppTopBanner.vue'
import StagePanel from '@/components/layout/StagePanel.vue'
import ChatPanel from '@/components/layout/ChatPanel.vue'
import MobileDrawer from '@/components/layout/MobileDrawer.vue'
import ConnectionBanner from '@/components/feedback/ConnectionBanner.vue'
import { useConnectionStore } from '@/stores/connection'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'
import { useChatStore } from '@/stores/chat'
import { sessionService } from '@/services/sessionService'
import { chatService } from '@/services/chatService'
import { useResponsive } from '@/composables/useResponsive'
import { useEmotionDriver } from '@/composables/useEmotionDriver'

const connection = useConnectionStore()
const session = useSessionStore()
const ui = useUiStore()
const chat = useChatStore()
const message = useMessage()
const { isMobile, isTablet } = storeToRefs(ui)

useResponsive()
useEmotionDriver()

let healthTimer: number | null = null

onMounted(async () => {
  await connection.check()
  scheduleHealth()
  if (!connection.reachable) return
  try {
    const list = await sessionService.refresh()
    let target = list.find((s) => s.status === 'active') ?? list[0]
    if (!target) target = await sessionService.create()
    session.setCurrent(target.id)
    await chatService.loadHistory(target.id)
  } catch (e) {
    message.error(e instanceof Error ? e.message : '初始化失败')
  }
})

function scheduleHealth() {
  if (healthTimer != null) return
  healthTimer = window.setInterval(() => {
    void connection.check()
  }, 5000)
}

// 测试函数
function addTestMessages() {
  for (let i = 1; i <= 20; i++) {
    chat.append({
      localId: 'test-' + i,
      role: i % 2 === 0 ? 'user' : 'assistant',
      text: `测试消息 ${i}：这是一条用来测试滚动条的长消息。`.repeat(5),
      status: 'sent',
      createdAt: Date.now() - i * 60000,
    })
  }

  setTimeout(() => {
    const messageList = document.querySelector('.message-list')
    if (messageList) {
      const element = messageList as HTMLElement
      console.log('=== MessageList 诊断 ===')
      console.log('offsetHeight:', element.offsetHeight)
      console.log('scrollHeight:', element.scrollHeight)
      console.log('可滚动:', element.scrollHeight > element.offsetHeight)
    }
  }, 500)
}

function clearTestMessages() {
  chat.reset()
  console.log('消息已清空，请查看空状态是否占满整个对话区域')
}

// 暴露到window供调试使用
if (import.meta.env.DEV) {
  ;(window as any).addTestMessages = addTestMessages
  ;(window as any).clearTestMessages = clearTestMessages
}

</script>

<template>
  <div class="app-shell" :class="{ mobile: isMobile, tablet: isTablet }">
    <AppTopBanner />
    <ConnectionBanner />
    <main class="main">
      <div class="stage-area">
        <StagePanel />
      </div>
      <div class="chat-area">
        <ChatPanel />
      </div>
    </main>
    <MobileDrawer />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  background: var(--color-bg-base);
}

.main {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 460px;
  gap: 16px;
  padding: 16px 20px 20px;
  min-height: 0;
  overflow: hidden;
}

.stage-area,
.chat-area {
  min-height: 0;
  display: flex;
  overflow: hidden;
}

.chat-area {
  align-items: stretch;
}

.stage-area {
  min-height: 60vh;
}

.app-shell.tablet .main {
  grid-template-columns: 1fr;
  grid-template-rows: 40vh minmax(0, 1fr);
}

.app-shell.mobile .main {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
  gap: 0;
  padding: 0;
  position: relative;
}

.app-shell.mobile .stage-area {
  position: absolute;
  inset: 0;
  z-index: 0;
  opacity: 0.45;
  pointer-events: none;
}

.app-shell.mobile .chat-area {
  position: relative;
  z-index: 1;
  height: calc(100dvh - 60px);
}
</style>
