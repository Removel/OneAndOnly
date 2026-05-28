import * as sessionApi from '@/api/session'
import { useSessionStore } from '@/stores/session'

export const sessionService = {
  async refresh() {
    const store = useSessionStore()
    store.loading = true
    try {
      const list = await sessionApi.listActiveSessions()
      const sorted = [...list].sort((a, b) => sortKey(b) - sortKey(a))
      store.setList(sorted)
      return sorted
    } finally {
      store.loading = false
    }
  },

  async create() {
    const session = await sessionApi.createSession()
    const store = useSessionStore()
    store.upsert(session)
    store.setCurrent(session.id)
    return session
  },

  async select(id: string) {
    const store = useSessionStore()
    store.setCurrent(id)
  },

  async remove(id: string) {
    await sessionApi.deleteSession(id)
    const store = useSessionStore()
    store.remove(id)
  },
}

function sortKey(s: { last_activity_at: string | null; updated_at: string | null }): number {
  const ts = s.last_activity_at ?? s.updated_at
  return ts ? new Date(ts).getTime() : 0
}
