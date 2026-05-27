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
    }),
  ],
  transformers: [transformerDirectives(), transformerVariantGroup()],
  theme: {
    colors: {
      // 主色：樱粉
      primary: {
        DEFAULT: '#FF8FA3',
        soft: '#FFC2CE',
        strong: '#F46A86',
      },
      // 辅助色：暖色调点缀
      accent: {
        peach: '#FFB089',
        cream: '#FFD9A8',
        mint: '#B8E0C2',
        lilac: '#E5C8F0',
      },
      // 文本：暖棕替代冷黑
      text: {
        primary: '#5A3E36',
        secondary: '#8A6A5E',
        inverse: '#FFFFFF',
      },
      // 背景层
      bg: {
        base: '#FFF8F1',
        soft: '#FFEFE2',
        card: '#FFFFFFEE',
        elevated: '#FFE4D6',
      },
    },
    borderRadius: {
      sm: '8px',
      md: '14px',
      lg: '22px',
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
