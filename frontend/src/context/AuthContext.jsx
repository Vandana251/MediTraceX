import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authApi } from '../services/api'
import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '../config'

const AuthContext = createContext(null)

function readStoredUser() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY))
  const [user, setUser] = useState(readStoredUser)
  const [loading, setLoading] = useState(Boolean(token))

  const persist = useCallback((nextToken, nextUser) => {
    setToken(nextToken)
    setUser(nextUser)
    if (nextToken) localStorage.setItem(TOKEN_STORAGE_KEY, nextToken)
    else localStorage.removeItem(TOKEN_STORAGE_KEY)
    if (nextUser) localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(nextUser))
    else localStorage.removeItem(USER_STORAGE_KEY)
  }, [])

  const logout = useCallback(() => persist(null, null), [persist])

  const applyAuthPayload = useCallback(
    (payload) => {
      persist(payload.access_token, {
        id: payload.user_id,
        name: payload.name,
        email: payload.email,
        role: payload.role,
      })
    },
    [persist]
  )

  const login = useCallback(
    async (credentials) => {
      const payload = await authApi.login(credentials)
      applyAuthPayload(payload)
      const profile = await authApi.me()
      persist(payload.access_token, profile)
      return profile
    },
    [applyAuthPayload, persist]
  )

  const register = useCallback(
    async (payload) => {
      const response = await authApi.register(payload)
      applyAuthPayload(response)
      const profile = await authApi.me()
      persist(response.access_token, profile)
      return profile
    },
    [applyAuthPayload, persist]
  )

  const refreshMe = useCallback(async () => {
    if (!token) return null
    const profile = await authApi.me()
    persist(token, profile)
    return profile
  }, [persist, token])

  useEffect(() => {
    const onUnauthorized = () => logout()
    window.addEventListener('mtx:unauthorized', onUnauthorized)
    return () => window.removeEventListener('mtx:unauthorized', onUnauthorized)
  }, [logout])

  useEffect(() => {
    let cancelled = false
    async function hydrate() {
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const profile = await authApi.me()
        if (!cancelled) persist(token, profile)
      } catch {
        if (!cancelled) logout()
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    hydrate()
    return () => {
      cancelled = true
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token && user),
      isPharmacyStaff: ['pharmacy_admin', 'pharmacy', 'system_admin'].includes(user?.role),
      login,
      register,
      logout,
      refreshMe,
    }),
    [token, user, loading, login, register, logout, refreshMe]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
