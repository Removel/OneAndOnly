import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface BackgroundOption {
  id: string
  name: string
  path: string
  thumbnail?: string
}

export const useBackgroundStore = defineStore('background', () => {
  const currentId = ref<string>('default')
  const customBackgrounds = ref<BackgroundOption[]>([])

  const defaultBackgrounds: BackgroundOption[] = [
    {
      id: 'default',
      name: '默认渐变',
      path: '',
    },
  ]

  const allBackgrounds = computed(() => [...defaultBackgrounds, ...customBackgrounds.value])

  const currentBackground = computed(() =>
    allBackgrounds.value.find(bg => bg.id === currentId.value) || defaultBackgrounds[0]
  )

  function setCurrent(id: string) {
    currentId.value = id
  }

  function addCustom(background: BackgroundOption) {
    if (!customBackgrounds.value.find(bg => bg.id === background.id)) {
      customBackgrounds.value.push(background)
    }
  }

  function removeCustom(id: string) {
    customBackgrounds.value = customBackgrounds.value.filter(bg => bg.id !== id)
    if (currentId.value === id) {
      currentId.value = 'default'
    }
  }

  return {
    currentId,
    customBackgrounds,
    allBackgrounds,
    currentBackground,
    setCurrent,
    addCustom,
    removeCustom,
  }
})
