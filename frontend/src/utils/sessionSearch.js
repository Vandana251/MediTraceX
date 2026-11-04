const KEY = 'mtx_session_searches'

export function recordSearch(query) {
  if (!query) return
  try {
    const current = JSON.parse(sessionStorage.getItem(KEY) || '[]')
    current.push({ q: query, at: Date.now() })
    sessionStorage.setItem(KEY, JSON.stringify(current.slice(-40)))
  } catch {
    /* ignore quota */
  }
}

export function getSessionSearches() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY) || '[]')
  } catch {
    return []
  }
}
