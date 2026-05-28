import type { GlobalThemeOverrides } from 'naive-ui'

/**
 * Naive UI 主题覆盖：将组件库默认色拉向"亮白底 + 青色 accent"。
 * 仅设置最常用 token，更细粒度的覆写在具体组件 :theme-overrides 中按需补充。
 */
export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#4FB8E6',
    primaryColorHover: '#2A93C7',
    primaryColorPressed: '#1F7CA8',
    primaryColorSuppl: '#DBEFF8',
    infoColor: '#4FB8E6',
    successColor: '#5FBFA8',
    warningColor: '#F0B860',
    errorColor: '#E07878',
    bodyColor: '#F6F9FB',
    cardColor: '#FFFFFF',
    modalColor: '#FFFFFF',
    popoverColor: '#FFFFFF',
    dividerColor: '#E3E8EC',
    borderColor: '#E3E8EC',
    textColorBase: '#18191C',
    textColor1: '#18191C',
    textColor2: '#2C3036',
    textColor3: '#61666D',
    textColorDisabled: '#9499A0',
    placeholderColor: '#9499A0',
    borderRadius: '10px',
    borderRadiusSmall: '6px',
    fontFamily: '"HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif',
  },
  Button: {
    borderRadiusMedium: '10px',
    fontWeight: '500',
  },
  Card: {
    borderRadius: '16px',
    borderColor: '#E3E8EC',
  },
  Input: {
    borderRadius: '10px',
  },
  Tag: {
    borderRadius: '6px',
  },
  Drawer: {
    color: '#FFFFFF',
  },
}
