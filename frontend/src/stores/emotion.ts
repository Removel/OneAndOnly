import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { EmotionCategory, EmotionVAC } from '@/types/message'

const NEUTRAL: EmotionVAC = { valence: 0, arousal: 0, control: 0 }

function categorize(vac: EmotionVAC): EmotionCategory {
  const { valence, arousal } = vac
  if (valence > 0.3 && arousal > 0.3) return 'happy'
  if (valence > 0.3) return 'calm'
  if (valence < -0.3 && arousal > 0.3) return 'angry'
  if (valence < -0.3) return 'sad'
  return 'neutral'
}

export const useEmotionStore = defineStore('emotion', () => {
  const vac = ref<EmotionVAC>({ ...NEUTRAL })
  const category = ref<EmotionCategory>('neutral')
  const history = ref<{ vac: EmotionVAC; at: number }[]>([])

  function setVac(next: EmotionVAC) {
    vac.value = next
    category.value = categorize(next)
    history.value.push({ vac: next, at: Date.now() })
    if (history.value.length > 50) history.value.shift()
  }

  function reset() {
    vac.value = { ...NEUTRAL }
    category.value = 'neutral'
    history.value = []
  }

  return { vac, category, history, setVac, reset }
})
