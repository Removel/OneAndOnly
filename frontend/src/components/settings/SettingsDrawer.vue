<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { NButton, NCollapse, NCollapseItem, NSpin, NSwitch, NTag } from 'naive-ui'
import { useUiStore } from '@/stores/ui'
import { useEmotionStore } from '@/stores/emotion'
import { useLive2DStore } from '@/stores/live2d'
import { useBackgroundStore } from '@/stores/background'

const ui = useUiStore()
const emotion = useEmotionStore()
const live2d = useLive2DStore()
const background = useBackgroundStore()
const { showDebug } = storeToRefs(ui)
const { vac, category } = storeToRefs(emotion)
const { models, currentId, loading, error, lastLoadedAt } = storeToRefs(live2d)
const { allBackgrounds, currentId: currentBgId } = storeToRefs(background)

const bgLoading = ref(false)
const bgError = ref<string | null>(null)

onMounted(async () => {
  void live2d.loadManifest().catch(() => undefined)
  await loadBackgroundManifest().catch(() => undefined)
})

async function loadBackgroundManifest() {
  bgLoading.value = true
  bgError.value = null
  try {
    const res = await fetch('/background/manifest.json', { cache: 'no-cache' })
    if (!res.ok) throw new Error(`背景manifest加载失败：HTTP ${res.status}`)
    const data = await res.json()
    if (data.backgrounds && Array.isArray(data.backgrounds)) {
      data.backgrounds.forEach((bg: any) => {
        background.addCustom({
          id: bg.id,
          name: bg.name,
          path: bg.path,
          thumbnail: bg.thumbnail,
        })
      })
    }
  } catch (e) {
    bgError.value = e instanceof Error ? e.message : String(e)
  } finally {
    bgLoading.value = false
  }
}

function handlePick(id: string) {
  if (id === currentId.value) return
  live2d.setCurrent(id)
}

function handlePickBackground(id: string) {
  if (id === currentBgId.value) return
  background.setCurrent(id)
}

function handleReload() {
  void live2d.loadManifest(true).catch(() => undefined)
}

function handleReloadBackground() {
  void loadBackgroundManifest().catch(() => undefined)
}

function formatLoadedAt(value: number | null) {
  return value == null ? '未读取' : new Date(value).toLocaleTimeString()
}
</script>

<template>
  <div class="settings">
    <NCollapse :default-expanded-names="['l2d', 'debug']" arrow-placement="right">
      <NCollapseItem title="L2D 模型" name="l2d">
        <p class="muted">把模型文件夹放入 public/live2d/models/，再在 manifest.json 追加一项。</p>

        <div class="toolbar">
          <span class="loaded-at">manifest：{{ formatLoadedAt(lastLoadedAt) }}</span>
          <NButton size="small" tertiary :loading="loading" @click="handleReload">
            <template #icon>
              <span class="i-solar-refresh-bold-duotone" />
            </template>
            重新读取 manifest
          </NButton>
        </div>

        <div v-if="loading" class="placeholder">
          <NSpin size="small" />
          <span>正在读取 manifest…</span>
        </div>

        <div v-else-if="error" class="placeholder error">
          <span class="i-solar-cloud-cross-bold-duotone placeholder-icon" />
          <span class="error-text">{{ error }}</span>
        </div>

        <div v-else-if="models.length === 0" class="placeholder">
          <span class="i-solar-folder-open-bold-duotone placeholder-icon" />
          <span>manifest 中没有可用模型</span>
        </div>

        <ul v-else class="model-list">
          <li
            v-for="m in models"
            :key="m.id"
            class="model-item"
            :class="{ active: m.id === currentId }"
            role="button"
            tabindex="0"
            @click="handlePick(m.id)"
            @keydown.enter.prevent="handlePick(m.id)"
          >
            <div class="model-thumb">
              <img v-if="m.avatar" :src="m.avatar" :alt="m.name" />
              <span v-else class="i-solar-magic-stick-3-bold-duotone" />
            </div>
            <div class="model-meta">
              <p class="model-name">{{ m.name }}</p>
              <p class="model-id">{{ m.id }}</p>
            </div>
            <NTag
              v-if="m.id === currentId"
              size="small"
              type="info"
              :bordered="false"
              class="active-tag"
            >
              使用中
            </NTag>
          </li>
        </ul>
      </NCollapseItem>

      <NCollapseItem title="背景设置" name="background">
        <p class="muted">背景图片放在 public/background/ 文件夹下，在 manifest.json 中配置。</p>

        <div class="toolbar">
          <span class="loaded-at">背景数量：{{ allBackgrounds.length }}</span>
          <NButton size="small" tertiary :loading="bgLoading" @click="handleReloadBackground">
            <template #icon>
              <span class="i-solar-refresh-bold-duotone" />
            </template>
            重新读取
          </NButton>
        </div>

        <div v-if="bgLoading" class="placeholder">
          <NSpin size="small" />
          <span>正在读取背景配置…</span>
        </div>

        <div v-else-if="bgError" class="placeholder error">
          <span class="i-solar-cloud-cross-bold-duotone placeholder-icon" />
          <span class="error-text">{{ bgError }}</span>
        </div>

        <ul v-else class="model-list">
          <li
            v-for="bg in allBackgrounds"
            :key="bg.id"
            class="model-item"
            :class="{ active: bg.id === currentBgId }"
            role="button"
            tabindex="0"
            @click="handlePickBackground(bg.id)"
            @keydown.enter.prevent="handlePickBackground(bg.id)"
          >
            <div class="model-thumb">
              <img v-if="bg.thumbnail" :src="bg.thumbnail" :alt="bg.name" />
              <img v-else-if="bg.path" :src="bg.path" :alt="bg.name" />
              <span v-else class="i-solar-image-bold-duotone" />
            </div>
            <div class="model-meta">
              <p class="model-name">{{ bg.name }}</p>
              <p class="model-id">{{ bg.id }}</p>
            </div>
            <NTag
              v-if="bg.id === currentBgId"
              size="small"
              type="success"
              :bordered="false"
              class="active-tag"
            >
              使用中
            </NTag>
          </li>
        </ul>
      </NCollapseItem>

      <NCollapseItem title="风格 / LoRA" name="style">
        <p class="muted">暂未开放，下个版本提供风格化文本与 LoRA 切换入口。</p>
      </NCollapseItem>

      <NCollapseItem title="调试" name="debug">
        <div class="row">
          <span>显示 VAC 调试面板</span>
          <NSwitch v-model:value="showDebug" />
        </div>
        <div v-if="showDebug" class="debug-card">
          <p class="row">
            <span>类别</span>
            <NTag size="small" type="info" :bordered="false">{{ category }}</NTag>
          </p>
          <p class="row">
            <span>Valence</span>
            <span class="num">{{ vac.valence.toFixed(2) }}</span>
          </p>
          <p class="row">
            <span>Arousal</span>
            <span class="num">{{ vac.arousal.toFixed(2) }}</span>
          </p>
          <p class="row">
            <span>Control</span>
            <span class="num">{{ vac.control.toFixed(2) }}</span>
          </p>
        </div>
      </NCollapseItem>
    </NCollapse>
  </div>
</template>

<style scoped>
.settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.muted {
  margin: 0 0 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 4px 0 8px;
}

.loaded-at {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 14px;
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  color: var(--color-text-tertiary);
  font-size: 13px;
  border: 1px dashed var(--color-border-light);
}

.placeholder.error {
  color: var(--color-danger);
  border-color: rgb(224 120 120 / 35%);
  background: rgb(224 120 120 / 8%);
}

.error-text {
  word-break: break-word;
}

.placeholder-icon {
  font-size: 22px;
  color: var(--color-primary);
}

.placeholder.error .placeholder-icon {
  color: var(--color-danger);
}

.model-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    background 0.18s ease,
    border-color 0.18s ease;
}

.model-item:hover {
  background: var(--color-accent-foam);
  border-color: var(--color-border-light);
}

.model-item.active {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}

.model-thumb {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  font-size: 24px;
  overflow: hidden;
  flex-shrink: 0;
}

.model-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.model-meta {
  flex: 1;
  min-width: 0;
}

.model-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-id {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: 'JetBrains Mono', 'Menlo', monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.active-tag {
  flex-shrink: 0;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 6px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.debug-card {
  margin-top: 8px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-soft);
  border: 1px solid var(--color-border-light);
}

.num {
  font-family: 'JetBrains Mono', 'Menlo', monospace;
  color: var(--color-primary-strong);
}
</style>
