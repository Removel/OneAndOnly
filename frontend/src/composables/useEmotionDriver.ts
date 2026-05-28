import { watchEffect } from 'vue'
import { storeToRefs } from 'pinia'
import { useEmotionStore } from '@/stores/emotion'

/**
 * 把 VAC 写到根 CSS 变量上，让 EmotionAura / 气泡描边自动跟随。
 * 设计书 §8.3：valence → 色相在 [350°, 40°] 偏移；
 * 这里改为在 [180°, 220°] 之间的冷青区间偏移，配合新主色。
 */
export function useEmotionDriver() {
  const { vac } = storeToRefs(useEmotionStore())

  watchEffect(() => {
    const { valence, arousal, control } = vac.value
    const root = document.documentElement
    // valence ∈ [-1, 1] → hue 200 ± 20
    const hue = 200 + clamp(valence, -1, 1) * 20
    // arousal ∈ [-1, 1] → saturation 25%~90%
    const saturation = 25 + ((clamp(arousal, -1, 1) + 1) / 2) * 65
    // control ∈ [-1, 1] → alpha 0.15 ~ 0.55
    const alpha = 0.15 + ((clamp(control, -1, 1) + 1) / 2) * 0.4
    root.style.setProperty('--aura-h', String(hue.toFixed(1)))
    root.style.setProperty('--aura-s', `${saturation.toFixed(1)}%`)
    root.style.setProperty('--aura-l', '75%')
    root.style.setProperty('--aura-a', alpha.toFixed(3))
  })
}

function clamp(v: number, lo: number, hi: number) {
  return Math.min(hi, Math.max(lo, v))
}
