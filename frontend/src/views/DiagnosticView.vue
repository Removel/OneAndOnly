<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'

const chat = useChatStore()
const diagnostics = ref<any>({})

function runDiagnostics() {
  const elements = {
    appShell: document.querySelector('.app-shell'),
    main: document.querySelector('.main'),
    chatArea: document.querySelector('.chat-area'),
    chatPanel: document.querySelector('.chat-panel'),
    messageArea: document.querySelector('.message-area'),
    messageList: document.querySelector('.message-list'),
  }

  const result: any = {}

  Object.entries(elements).forEach(([name, el]) => {
    if (el) {
      const computed = window.getComputedStyle(el)
      result[name] = {
        height: computed.height,
        minHeight: computed.minHeight,
        maxHeight: computed.maxHeight,
        overflow: computed.overflow,
        overflowY: computed.overflowY,
        display: computed.display,
        flex: computed.flex,
        flexGrow: computed.flexGrow,
        flexShrink: computed.flexShrink,
        offsetHeight: (el as HTMLElement).offsetHeight,
        scrollHeight: (el as HTMLElement).scrollHeight,
        canScroll: (el as HTMLElement).scrollHeight > (el as HTMLElement).offsetHeight,
      }
    }
  })

  diagnostics.value = result
}

function addTestMessages() {
  for (let i = 1; i <= 20; i++) {
    chat.append({
      localId: 'test-' + i,
      role: i % 2 === 0 ? 'user' : 'assistant',
      text: `测试消息 ${i}：这是一条用来测试滚动条的长消息。`.repeat(3),
      status: 'sent',
      createdAt: Date.now() - i * 60000,
    })
  }
  setTimeout(runDiagnostics, 100)
}

function clearMessages() {
  chat.reset()
  setTimeout(runDiagnostics, 100)
}

onMounted(() => {
  runDiagnostics()
})
</script>

<template>
  <div class="diagnostic-page">
    <h1>MessageList 滚动条诊断</h1>

    <div class="actions">
      <button @click="addTestMessages">添加20条测试消息</button>
      <button @click="clearMessages">清空消息</button>
      <button @click="runDiagnostics">刷新诊断</button>
    </div>

    <div class="diagnostics">
      <h2>布局层级诊断</h2>
      <div v-for="(data, name) in diagnostics" :key="name" class="diagnostic-item">
        <h3>{{ name }}</h3>
        <table>
          <tbody>
            <tr>
              <td>height</td>
              <td :class="{ warning: data.height === 'auto' }">{{ data.height }}</td>
            </tr>
            <tr>
              <td>minHeight</td>
              <td :class="{ success: data.minHeight === '0px' }">{{ data.minHeight }}</td>
            </tr>
            <tr>
              <td>maxHeight</td>
              <td :class="{ warning: data.maxHeight !== 'none' }">{{ data.maxHeight }}</td>
            </tr>
            <tr>
              <td>overflow-y</td>
              <td :class="{ success: data.overflowY === 'auto' || data.overflowY === 'scroll' }">
                {{ data.overflowY }}
              </td>
            </tr>
            <tr>
              <td>display</td>
              <td>{{ data.display }}</td>
            </tr>
            <tr>
              <td>flex</td>
              <td :class="{ success: data.flex !== '0 1 auto' }">{{ data.flex }}</td>
            </tr>
            <tr>
              <td>offsetHeight</td>
              <td>{{ data.offsetHeight }}px</td>
            </tr>
            <tr>
              <td>scrollHeight</td>
              <td>{{ data.scrollHeight }}px</td>
            </tr>
            <tr>
              <td>可滚动</td>
              <td :class="{ success: data.canScroll, error: !data.canScroll }">
                {{ data.canScroll ? '✓ 是' : '✗ 否' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="tips">
      <h3>关键检查点</h3>
      <ul>
        <li><strong>messageList</strong> 必须有 <code>overflow-y: auto</code></li>
        <li><strong>messageList</strong> 必须有 <code>min-height: 0</code></li>
        <li><strong>messageList</strong> 必须有 <code>flex: 1 1 0%</code> 或类似</li>
        <li><strong>messageList</strong> 的 <code>offsetHeight</code> 必须小于 <code>scrollHeight</code></li>
        <li>所有父容器必须有明确的高度约束</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.diagnostic-page {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--color-bg-base);
  min-height: 100vh;
}

h1 {
  color: var(--color-primary);
  margin-bottom: 30px;
}

h2 {
  color: var(--color-text-primary);
  margin: 30px 0 20px;
}

h3 {
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  font-size: 16px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

button {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background: var(--color-primary-strong);
}

.diagnostics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.diagnostic-item {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: 16px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

tr {
  border-bottom: 1px solid var(--color-border-light);
}

tr:last-child {
  border-bottom: none;
}

td {
  padding: 8px 4px;
  color: var(--color-text-secondary);
}

td:first-child {
  font-weight: 600;
  color: var(--color-text-primary);
  width: 40%;
}

td:last-child {
  font-family: monospace;
  font-size: 12px;
}

.success {
  color: var(--color-success) !important;
  font-weight: 600;
}

.warning {
  color: var(--color-warning) !important;
  font-weight: 600;
}

.error {
  color: var(--color-danger) !important;
  font-weight: 600;
}

.tips {
  margin-top: 40px;
  padding: 20px;
  background: var(--color-bg-card);
  border: 2px solid var(--color-primary-soft);
  border-radius: var(--radius-md);
}

.tips ul {
  margin: 0;
  padding-left: 24px;
}

.tips li {
  margin-bottom: 8px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.tips code {
  background: var(--color-bg-soft);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--color-primary-strong);
}
</style>
