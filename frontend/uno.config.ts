import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetUno,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
      collections: {
        solar: () => import('@iconify-json/solar/icons.json').then(i => i.default),
        mingcute: () => import('@iconify-json/mingcute/icons.json').then(i => i.default),
      },
    }),
  ],
  safelist: [
    // AppTopBanner.vue 中的图标
    'i-solar-chat-line-bold-duotone',
    'i-solar-settings-bold-duotone',
    'i-solar-question-circle-bold-duotone',
    'i-solar-info-circle-bold-duotone',
    // MessageList.vue 中的图标
    'i-solar-chat-square-2-bold-duotone',
    // MessageBubble.vue 中的图标
    'i-solar-user-bold-duotone',
    'i-solar-magic-stick-3-bold-duotone',
    // SessionSwitcher.vue 中的图标
    'i-solar-chat-square-like-bold-duotone',
    'i-solar-alt-arrow-down-bold-duotone',
    // SessionListPanel.vue 中的图标
    'i-solar-add-square-bold-duotone',
    // SessionItem.vue 中的图标
    'i-solar-trash-bin-2-bold-duotone',
    // HelpView.vue 中的图标
    'i-solar-arrow-left-bold-duotone',
  ],
  transformers: [transformerDirectives(), transformerVariantGroup()],
  theme: {
    colors: {
      // 主色：天空青
      primary: {
        DEFAULT: '#4FB8E6',
        soft: '#DBEFF8',
        strong: '#2A93C7',
      },
      // 辅助色：冷色域点缀 + 少量暖粉
      accent: {
        aqua: '#7DD3D8',
        sky: '#A8D8F0',
        foam: '#E6F4F8',
        violet: '#B8C8F0',
        pink: '#FF8AB8',
      },
      // 文本：B 站式深灰
      text: {
        primary: '#18191C',
        secondary: '#61666D',
        tertiary: '#9499A0',
        inverse: '#FFFFFF',
        link: '#2A93C7',
      },
      // 背景层（冷白基底）
      bg: {
        base: '#F6F9FB',
        soft: '#EDF3F7',
        card: '#FFFFFF',
        elevated: '#FFFFFF',
      },
      // 边框
      border: {
        light: '#E3E8EC',
        hover: '#C9D6DD',
      },
      // 状态
      status: {
        success: '#5FBFA8',
        warning: '#F0B860',
        danger: '#E07878',
      },
    },
    borderRadius: {
      sm: '6px',
      md: '10px',
      lg: '16px',
      pill: '9999px',
    },
    breakpoints: {
      sm: '360px',
      md: '768px',
      lg: '1280px',
      xl: '1536px',
    },
  },
})
