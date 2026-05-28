<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { NSpin } from 'naive-ui'
import { useEmotionStore } from '@/stores/emotion'
import { useLive2DStore } from '@/stores/live2d'
import { useLive2D } from '@/composables/useLive2D'

const emotion = useEmotionStore()
const live2d = useLive2DStore()
const { category } = storeToRefs(emotion)
const { current, error, ready, loading } = storeToRefs(live2d)

const { canvasRef, containerRef, bootstrap } = useLive2D()

const auraStyle = computed(() => ({
  background: `radial-gradient(circle at 50% 35%, hsla(var(--aura-h), var(--aura-s), var(--aura-l), var(--aura-a)) 0%, transparent 65%)`,
}))

const labelMap: Record<string, string> = {
  happy: '心情很好',
  calm: '平静',
  sad: '有些低落',
  angry: '有点不快',
  neutral: '中性',
}

onMounted(async () => {
  try {
    await live2d.loadManifest()
  } catch {
    /* store.error 已写入，UI 自行展示 */
    return
  }
  await bootstrap()
})
</script>

<template>
  <section ref="containerRef" class="stage">
    <div class="stage-bg" />
    <div class="stage-aura" :style="auraStyle" />

    <canvas ref="canvasRef" class="stage-canvas" />

    <div v-if="!ready" class="stage-overlay">
      <template v-if="error">
        <div class="overlay-card error">
          <span class="i-solar-cloud-cross-bold-duotone overlay-icon" />
          <p class="overlay-title">Live2D 加载失败</p>
          <p class="overlay-desc">{{ error }}</p>
        </div>
      </template>
      <template v-else-if="loading || !current">
        <div class="overlay-card">
          <NSpin size="medium" />
          <p class="overlay-desc">正在准备 Live2D 舞台…</p>
        </div>
      </template>
      <template v-else>
        <div class="overlay-card">
          <span class="i-solar-magic-stick-3-bold-duotone overlay-icon" />
          <p class="overlay-title">{{ current.name }}</p>
          <p class="overlay-desc">模型加载中</p>
        </div>
      </template>
    </div>

    <div class="stage-meta">
      <span class="emotion-tag">当前情绪：{{ labelMap[category] ?? '中性' }}</span>
      <span v-if="current && ready" class="model-tag">{{ current.name }}</span>
    </div>
  </section>
</template>

<style scoped>
.stage {
  position: relative;
  flex: 1;
  min-height: 280px;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
}

.stage-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 0%, var(--color-accent-foam) 0%, transparent 55%),
    radial-gradient(circle at 80% 100%, var(--color-primary-soft) 0%, transparent 60%),
    var(--color-bg-card);
}

.stage-aura {
  position: absolute;
  inset: -10%;
  filter: blur(20px);
  transition:
    background 0.6s ease,
    opacity 0.6s ease;
  pointer-events: none;
}

.stage-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.stage-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.overlay-card {
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 28px;
  border-radius: var(--radius-lg);
  background: rgb(255 255 255 / 80%);
  border: 1px solid var(--color-border-light);
  backdrop-filter: blur(10px);
  color: var(--color-text-secondary);
  max-width: 360px;
  text-align: center;
}

.overlay-card.error {
  border-color: rgb(224 120 120 / 35%);
  color: var(--color-danger);
}

.overlay-icon {
  font-size: 36px;
  color: var(--color-primary-strong);
}

.overlay-card.error .overlay-icon {
  color: var(--color-danger);
}

.overlay-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.overlay-card.error .overlay-title {
  color: var(--color-danger);
}

.overlay-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-text-tertiary);
  word-break: break-word;
}

.stage-meta {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  pointer-events: none;
}

.emotion-tag,
.model-tag {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  background: rgb(255 255 255 / 80%);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  backdrop-filter: blur(8px);
}

.emotion-tag {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  border-color: rgb(79 184 230 / 25%);
}
</style>
