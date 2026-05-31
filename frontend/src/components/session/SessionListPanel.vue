<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { NButton, NEmpty, NIcon, NSpin, useMessage } from 'naive-ui'
import { useSessionStore } from '@/stores/session'
import { useUiStore } from '@/stores/ui'
import { sessionService } from '@/services/sessionService'
import { chatService } from '@/services/chatService'
import SessionItem from '@/components/session/SessionItem.vue'

const session = useSessionStore()
const ui = useUiStore()
const message = useMessage()
const { list, loading, currentId } = storeToRefs(session)

const emit = defineEmits<{
  (e: 'finished'): void
}>()

onMounted(() => {
  void refresh()
})

async function refresh() {
  try {
    await sessionService.refresh()
  } catch (e) {
    message.error(e instanceof Error ? e.message : '加载会话失败')
  }
}

async function handleSelect(id: string) {
  if (id === currentId.value) {
    ui.closeDrawer()
    emit('finished')
    return
  }
  await sessionService.select(id)
  try {
    await chatService.loadHistory(id)
  } catch (e) {
    message.error(e instanceof Error ? e.message : '加载历史失败')
  }
  ui.closeDrawer()
  emit('finished')
}

async function handleDelete(id: string) {
  try {
    await sessionService.remove(id)
    message.success('已删除')
  } catch (e) {
    message.error(e instanceof Error ? e.message : '删除失败')
  }
}

async function handleNew() {
  try {
    const created = await sessionService.create()
    await chatService.loadHistory(created.id)
    ui.closeDrawer()
    emit('finished')
  } catch (e) {
    message.error(e instanceof Error ? e.message : '创建失败')
  }
}
</script>

<template>
  <div class="session-list">
    <div class="header">
      <NButton type="primary" block @click="handleNew">
        <template #icon>
          <span class="i-solar-add-square-bold-duotone" style="font-size: 18px" />
        </template>
        新建对话
      </NButton>
    </div>
    <NSpin v-if="loading" class="loading" />
    <div v-else-if="list.length === 0" class="empty">
      <NEmpty description="暂无会话" />
    </div>
    <ul v-else class="list">
      <SessionItem
        v-for="item in list"
        :key="item.id"
        :session="item"
        :active="item.id === currentId"
        @select="handleSelect(item.id)"
        @delete="handleDelete(item.id)"
      />
    </ul>
  </div>
</template>

<style scoped>
.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.header {
  padding: 4px 4px 0;
}

.list {
  flex: 1;
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.loading,
.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}
</style>
