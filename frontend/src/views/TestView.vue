<script setup lang="ts">
import { ref } from 'vue'

const messages = ref(Array.from({ length: 20 }, (_, i) => `测试消息 ${i + 1}`))
</script>

<template>
  <div class="test-page">
    <h1>图标和滚动条测试页面</h1>

    <section class="icon-test">
      <h2>图标测试</h2>
      <div class="icon-grid">
        <div class="icon-item">
          <span class="i-solar-chat-line-bold-duotone" />
          <p>chat-line</p>
        </div>
        <div class="icon-item">
          <span class="i-solar-user-bold-duotone" />
          <p>user</p>
        </div>
        <div class="icon-item">
          <span class="i-solar-magic-stick-3-bold-duotone" />
          <p>magic-stick</p>
        </div>
        <div class="icon-item">
          <span class="i-solar-settings-bold-duotone" />
          <p>settings</p>
        </div>
      </div>
    </section>

    <section class="scroll-test">
      <h2>滚动条测试</h2>
      <div class="scroll-container">
        <div v-for="msg in messages" :key="msg" class="message-item">
          {{ msg }}
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.test-page {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: var(--color-primary);
  margin-bottom: 40px;
}

h2 {
  color: var(--color-text-primary);
  margin-bottom: 20px;
}

.icon-test {
  margin-bottom: 60px;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 20px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
}

.icon-item span {
  font-size: 48px;
  color: var(--color-primary);
}

.icon-item p {
  margin: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.scroll-test {
  margin-bottom: 40px;
}

.scroll-container {
  height: 300px;
  overflow-y: auto;
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-md);
  padding: 16px;
  background: var(--color-bg-card);
  scrollbar-width: thin;
}

.scroll-container::-webkit-scrollbar {
  width: 12px;
}

.scroll-container::-webkit-scrollbar-track {
  background: var(--color-bg-soft);
  border-radius: 6px;
}

.scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-primary);
  border-radius: 6px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

.scroll-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary-strong);
  background-clip: padding-box;
}

.message-item {
  padding: 12px;
  margin-bottom: 8px;
  background: var(--color-bg-soft);
  border-radius: var(--radius-sm);
  color: var(--color-text-primary);
}
</style>
