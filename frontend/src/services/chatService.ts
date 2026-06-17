import * as chatApi from '@/api/chat'
import { useChatStore } from '@/stores/chat'
import type { UiMessage, MessageItem } from '@/types/message'
import type { MessageResponseDTO } from '@/types/message'

function localId(): string {
  return `m_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`
}

/**
 * 移除文本中的 [EMOTION]...[/EMOTION] 区块。
 * LLM 在流式输出时会吐出原始格式的 emotion 标签，前端需要过滤掉。
 */
function stripEmotion(raw: string): string {
  const start = raw.indexOf('[EMOTION]')
  if (start === -1) return raw
  const end = raw.indexOf('[/EMOTION]', start)
  if (end === -1) {
    // 只出现了开始标签，截断到标签之前
    return raw.substring(0, start).trimEnd()
  }
  // 移除整个 Emotion 区块
  const before = raw.substring(0, start)
  const after = raw.substring(end + '[/EMOTION]'.length)
  return (before + after).trim()
}

function pickRenderableHistory(messages: MessageResponseDTO[]): UiMessage[] {
  return messages
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .map((m, idx) => {
      // 历史消息使用实际时间戳或合理回退值（每条间隔1分钟）
      const timestamp = m.response_metadata?.timestamp as number | undefined
      const createdAt = timestamp ?? Date.now() - (messages.length - idx) * 60_000
      return {
        localId: `h_${idx}_${m.message_id ?? Math.random().toString(36).slice(2, 8)}`,
        role: m.role as 'user' | 'assistant',
        text: m.content,
        status: 'sent' as const,
        createdAt,
      }
    })
}

function mapNodeNameToStatus(nodeName: string): 'recalling' | 'thinking' | 'answering' | 'tool_calling' | 'node_processing' {
  const lowerName = nodeName.toLowerCase()
  if (lowerName.includes('recall') || lowerName.includes('memory')) {
    return 'recalling'
  }
  if (lowerName.includes('think') || lowerName.includes('plan')) {
    return 'thinking'
  }
  if (lowerName.includes('answer') || lowerName.includes('response') || lowerName.includes('styled') || lowerName.includes('output')) {
    return 'answering'
  }
  if (lowerName.includes('tool') || lowerName.includes('execute')) {
    return 'tool_calling'
  }
  return 'node_processing'
}

/**
 * 只有 styled_output 是用户可见输出源。
 * plan_execute 属于内部推理/工具执行阶段，不能直接流式展示，否则会和最终风格化回复重复。
 */
function isTokenSourceNode(nodeName: string): boolean {
  const lowerName = nodeName.toLowerCase()
  return lowerName.includes('styled') || lowerName.includes('output')
}

/**
 * 流式 token 清洗：检测 JSON 结构体起始并截断。
 * LLM 输出通常是 "自然语言...\n\n{...JSON...}" —— 我们只保留自然语言部分。
 */
function cleanStreamContent(buffer: string): { display: string; inJson: boolean; jsonStarted: boolean } {
  // 如果已经在 JSON 区域内，丢弃新内容
  const jsonStart = buffer.lastIndexOf('\n\n{')
  if (jsonStart >= 0) {
    // JSON 已经开始，只取 JSON 之前的部分
    const beforeJson = buffer.substring(0, jsonStart)
    return { display: beforeJson, inJson: true, jsonStarted: true }
  }
  // 检查是否仅以 { 开头（纯 JSON，无自然语言前缀）
  if (buffer.trimStart().startsWith('{')) {
    return { display: '', inJson: true, jsonStarted: true }
  }
  // 正常文本
  return { display: buffer, inJson: false, jsonStarted: false }
}

/**
 * 判断是否是图节点（而不是内部 RunnableSequence 等链）。
 * LangGraph astream_events 会同时发出图节点事件和内部 chain 事件，
 * 只有图节点才应该改变 shouldCollectTokens 和状态栏。
 */
const GRAPH_NODES = new Set([
  'memory_retrieve',
  'plan_execute',
  'evaluate',
  'styled_output',
])

function isGraphNode(name: string): boolean {
  return GRAPH_NODES.has(name)
}

export const chatService = {
  async loadHistory(sessionId: string) {
    const chat = useChatStore()
    const history = await chatApi.getHistory(sessionId)
    chat.reset()
    chat.messages.splice(0, chat.messages.length, ...pickRenderableHistory(history.messages))
  },

  async clearHistory(sessionId: string) {
    await chatApi.clearHistory(sessionId)
    const chat = useChatStore()
    chat.reset()
  },

  async sendMessage(sessionId: string, text: string) {
    const trimmed = text.trim()
    if (!trimmed) return
    const chat = useChatStore()

    const now = Date.now()
    const userMsg: UiMessage = {
      localId: localId(),
      role: 'user',
      text: trimmed,
      status: 'sent',
      createdAt: now,
    }
    const assistantMsg: UiMessage = {
      localId: localId(),
      role: 'assistant',
      text: '',
      status: 'pending',
      createdAt: now,
      items: [],
    }
    chat.append(userMsg)
    chat.append(assistantMsg)
    chat.setSending(true)
    chat.setStatus('thinking')

    let currentNode = ''
    let shouldCollectTokens = false
    /** 用于流式 token 清洗的原始文本缓冲（检测 JSON 起始） */
    let rawBuffer = ''
    /** 跨 token 持久化 JSON 抑制状态（cleanStreamContent 无状态，需外部跟踪） */
    let inJsonBlock = false

    try {
      const stream = chatApi.sendChatStream({ human_input: trimmed, session_id: sessionId })

      for await (const event of stream) {
        switch (event.type) {
          case 'node_start': {
            const rawName = (event.data.node as string) || ''
            if (rawName && isGraphNode(rawName)) {
              currentNode = rawName
              const nodeStatus = mapNodeNameToStatus(currentNode)
              chat.setStatus(nodeStatus)

              // plan_execute 和 styled_output 产生的 token 需要展示给用户
              shouldCollectTokens = isTokenSourceNode(currentNode)
              // 重置缓冲和 JSON 抑制状态，准备接收新节点的流式输出
              rawBuffer = ''
              inJsonBlock = false
            }
            break
          }

          case 'node_end': {
            const rawName = (event.data.node as string) || ''
            if (rawName && isGraphNode(rawName)) {
              shouldCollectTokens = false
              chat.setStatus('thinking')
            }
            break
          }

          case 'token': {
            const content = event.data.content as string | undefined
            if (content && shouldCollectTokens) {
              // 如果已进入 JSON 块，持续抑制直到节点结束
              if (inJsonBlock) {
                break
              }

              // 流式清洗：先合并当前 token，再检测 JSON 起始，避免跨 token 漏掉 "{"
              rawBuffer += content
              const cleaned = cleanStreamContent(rawBuffer)

              if (cleaned.jsonStarted) {
                // 检测到 JSON 起始，进入抑制模式，不再展示后续 token
                inJsonBlock = true
                break
              }

              // 累积文本并移除 emotion 标签
              const displayText = stripEmotion(cleaned.display)
              if (!displayText) break

              assistantMsg.text = displayText

              // 获取当前 items 列表
              const items = assistantMsg.items ?? []
              // 全量刷新模式：每次用最新完整文本替换最后一个 text item
              const last = items[items.length - 1]
              let newItems: MessageItem[]
              if (last && last.type === 'text') {
                newItems = [...items.slice(0, -1), { ...last, content: displayText, timestamp: Date.now() }]
              } else {
                newItems = [...items, { type: 'text', content: displayText, timestamp: Date.now() }]
              }

              chat.update(assistantMsg.localId, {
                items: newItems,
                text: displayText,
                status: 'pending',
              })
              assistantMsg.items = newItems
              chat.setStatus('answering')
            }
            break
          }

          case 'tool_start': {
            const toolName = (event.data.tool as string) || 'unknown'
            const toolItem: MessageItem = {
              type: 'tool_call',
              content: `调用工具: ${toolName}`,
              toolName,
              timestamp: Date.now(),
            }
            const items = [...(assistantMsg.items ?? []), toolItem]
            chat.update(assistantMsg.localId, { items })
            assistantMsg.items = items
            chat.setStatus('tool_calling')
            break
          }

          case 'tool_end': {
            const items = assistantMsg.items ?? []
            if (items.length > 0) {
              const lastIdx = items.length - 1
              const lastItem = items[lastIdx]
              if (lastItem.type === 'tool_call') {
                const updated = [...items]
                updated[lastIdx] = { ...lastItem, content: `调用工具: ${lastItem.toolName ?? 'unknown'} ✓` }
                chat.update(assistantMsg.localId, { items: updated })
                assistantMsg.items = updated
              }
            }
            break
          }

          case 'done': {
            // 使用服务端返回的权威干净 response_text，同时保留工具调用记录
            const finalText = (event.data.response_text as string) || assistantMsg.text
            // 保留所有 tool_call item，只替换/追加 text item
            const toolItems = (assistantMsg.items ?? []).filter(i => i.type === 'tool_call')
            const finalItems: MessageItem[] = finalText
              ? [...toolItems, { type: 'text' as const, content: finalText, timestamp: Date.now() }]
              : [...toolItems, ...(assistantMsg.items ?? []).filter(i => i.type === 'text')]

            chat.update(assistantMsg.localId, {
              status: 'sent',
              text: finalText,
              items: finalItems,
              retryTimes: event.data.retry_times as number | undefined,
            })
            assistantMsg.text = finalText
            assistantMsg.items = finalItems
            chat.setStatus('idle')
            break
          }

          case 'error': {
            chat.update(assistantMsg.localId, {
              status: 'failed',
              text: (event.data.message as string) || '回复失败，请重试',
              errorMessage: event.data.message as string,
            })
            chat.setStatus('failed')
            window.setTimeout(() => chat.setStatus('idle'), 1500)
            break
          }
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '请求失败'
      chat.update(assistantMsg.localId, {
        status: 'failed',
        text: message,
        errorMessage: message,
      })
      chat.setStatus('failed')
      window.setTimeout(() => chat.setStatus('idle'), 1500)
    } finally {
      chat.setSending(false)
    }
  },
}
