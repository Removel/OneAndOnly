import type { GlobalThemeOverrides } from 'naive-ui'

/**
 * Naive UI 主题覆盖：将组件库默认色拉向暖色二次元基调。
 * 仅设置最常用 token，更细粒度的覆写在具体组件 :theme-overrides 中按需补充。
 */
export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#FF8FA3',
    primaryColorHover: '#F46A86',
    primaryColorPressed: '#E15775',
    primaryColorSuppl: '#FFC2CE',
    bodyColor: '#FFF8F1',
    cardColor: '#FFFFFF',
    textColorBase: '#5A3E36',
    textColor1: '#5A3E36',
    textColor2: '#6B4A3F',
    textColor3: '#8A6A5E',
    borderRadius: '14px',
    borderRadiusSmall: '8px',
    fontFamily:
      '"HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif',
  },
  Button: {
    borderRadiusMedium: '14px',
    fontWeight: '500',
  },
  Card: {
    borderRadius: '22px',
  },
}
