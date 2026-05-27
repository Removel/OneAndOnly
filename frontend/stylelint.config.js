/** @type {import('stylelint').Config} */
export default {
  extends: ['stylelint-config-standard', 'stylelint-config-recommended-vue'],
  rules: {
    'selector-class-pattern': null,
    'no-descending-specificity': null,
    // 允许 UnoCSS 的 :deep / :global 选择器
    'selector-pseudo-class-no-unknown': [
      true,
      { ignorePseudoClasses: ['deep', 'global'] },
    ],
  },
}
