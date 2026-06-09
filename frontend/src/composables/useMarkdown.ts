import { computed, type MaybeRef, toRef } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true,
  typographer: true,
})

export function useMarkdown(source: MaybeRef<string>) {
  const sourceRef = toRef(source)

  const rendered = computed(() => {
    const raw = sourceRef.value
    if (!raw) return ''
    return md.render(raw)
  })

  return { rendered }
}
