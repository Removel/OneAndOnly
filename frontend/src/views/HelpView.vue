<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { NCard, NTabs, NTabPane } from 'naive-ui'

const route = useRoute()
const tab = computed(() => (route.query.tab === 'about' ? 'about' : 'help'))
</script>

<template>
  <main class="help-shell">
    <header class="header">
      <RouterLink class="back" to="/">
        <span class="i-solar-arrow-left-bold-duotone" />
        返回主页
      </RouterLink>
      <h1 class="title">帮助 / 介绍</h1>
    </header>
    <NCard class="card" :bordered="false">
      <NTabs :value="tab" type="line" animated>
        <NTabPane name="help" tab="使用帮助">
          <h3>基础使用</h3>
          <ul>
            <li>在右下输入框直接发送消息，按 Enter 发送、Shift + Enter 换行。</li>
            <li>顶栏「对话列表」管理会话，「设置」打开模型与调试面板。</li>
            <li>对话状态条会显示「回忆中 / 思考中 / 回答中」三个阶段。</li>
          </ul>
          <h3>调试与情绪</h3>
          <ul>
            <li>在设置 → 调试中开启 VAC 面板，可实时查看情绪向量。</li>
            <li>舞台中央的色彩光晕会随情绪变化，valence 偏冷青、负向降饱和。</li>
          </ul>
        </NTabPane>
        <NTabPane name="about" tab="关于本项目">
          <p>One and Only 是一个 AI 陪伴项目，由四个独立模块组成：</p>
          <ul>
            <li><strong>agent/</strong>：基于 LangGraph 的认知层。</li>
            <li><strong>backend/</strong>：FastAPI 服务层，负责持久化与协议封装。</li>
            <li><strong>custom_model/</strong>：本地 PyTorch 风格化与 VAC 模型。</li>
            <li><strong>unity/</strong> 与 <strong>frontend/</strong>：两条并行的客户端。</li>
          </ul>
          <p class="muted">前端版本：v0.3 · 主题：亮白 + 青色 accent。</p>
        </NTabPane>
      </NTabs>
    </NCard>
  </main>
</template>

<style scoped>
.help-shell {
  min-height: 100dvh;
  padding: 24px;
  background: var(--color-bg-base);
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-primary-strong);
  text-decoration: none;
  font-weight: 500;
}

.back:hover {
  text-decoration: underline;
}

.title {
  margin: 0;
  font-size: 20px;
  color: var(--color-text-primary);
}

.card {
  max-width: 880px;
  margin: 0 auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-card);
  background: var(--color-bg-card);
}

h3 {
  margin: 16px 0 8px;
  font-size: 15px;
  color: var(--color-primary-strong);
}

ul {
  padding-left: 20px;
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.muted {
  color: var(--color-text-tertiary);
  font-size: 13px;
}
</style>
