import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import {
  Activity,
  Bell,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  MapPin,
  Menu,
  Package,
  Pill,
  Sparkles,
  UserRound,
  ClipboardList,
  Bookmark,
  BarChart3,
  ShieldAlert,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { watchlistApi } from '../services/api'
import { initials } from '../utils/format'
import { LogoMark } from './ui'
import { MedicineSearchBar } from './MedicineSearchBar'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/medicines', label: 'Medicines', icon: Pill },
  { to: '/pharmacies', label: 'Pharmacies', icon: MapPin },
  { to: '/inventory', label: 'Inventory', icon: Package },
  { to: '/intelligence', label: 'AI / ML Intelligence', icon: Sparkles },
  { to: '/risk', label: 'Stock-out Risk', icon: ShieldAlert },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/requests', label: 'Requests', icon: ClipboardList },
  { to: '/watchlist', label: 'Watchlist', icon: Bookmark },
  { to: '/profile', label: 'Profile', icon: UserRound },
]

export function AppShell() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [notesOpen, setNotesOpen] = useState(false)
  const [watchCount, setWatchCount] = useState(0)

  useEffect(() => {
    let cancelled = false
    async function load() {
      if (!isAuthenticated) {
        setWatchCount(0)
        return
      }
      try {
        const items = await watchlistApi.list()
        if (!cancelled) setWatchCount(Array.isArray(items) ? items.length : 0)
      } catch {
        if (!cancelled) setWatchCount(0)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  return (
    <div className={`app-shell ${collapsed ? 'collapsed' : ''}`}>
      <div
        className={`sidebar-overlay ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
      />
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <LogoMark />
          </div>
          <div className="brand-copy">
            <strong>MediTraceX</strong>
            <span>Find. Verify. Reach.</span>
          </div>
        </div>
        <nav className="nav-group">
          {NAV.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setMobileOpen(false)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
        <div className="sidebar-foot">
          {isAuthenticated ? (
            <button
              className="nav-item"
              type="button"
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          ) : (
            <NavLink className="nav-item" to="/login">
              <LogOut size={18} />
              <span>Sign in</span>
            </NavLink>
          )}
          <button className="collapse-btn" type="button" onClick={() => setCollapsed((v) => !v)}>
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            <span>{collapsed ? 'Expand' : 'Collapse'}</span>
          </button>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <button className="icon-btn mobile-toggle" type="button" onClick={() => setMobileOpen((v) => !v)}>
            <Menu size={18} />
          </button>
          <div className="topbar-search">
            <MedicineSearchBar
              compact
              onSelect={(item) => navigate(`/medicines/${item.id}`)}
              onSubmit={(q) => navigate(`/medicines?q=${encodeURIComponent(q)}`)}
            />
          </div>
          <div style={{ position: 'relative' }}>
            <button className="icon-btn" type="button" onClick={() => setNotesOpen((v) => !v)} aria-label="Notifications">
              <Bell size={18} />
              {watchCount > 0 ? <span className="dot" /> : null}
            </button>
            {notesOpen ? (
              <div className="dropdown">
                <div className="dropdown-item">
                  <strong>Restock alerts</strong>
                  <p style={{ margin: '6px 0 0', color: 'var(--muted)' }}>
                    {isAuthenticated
                      ? `${watchCount} active watchlist ${watchCount === 1 ? 'item' : 'items'} are monitoring restock events.`
                      : 'Sign in to receive restock notifications from your watchlist.'}
                  </p>
                </div>
              </div>
            ) : null}
          </div>
          <button className="user-chip" type="button" onClick={() => navigate(isAuthenticated ? '/profile' : '/login')}>
            <span className="avatar">{initials(user?.name || 'Guest')}</span>
            <span>
              {user?.name || 'Guest'}
              <small>{user?.role?.replace('_', ' ') || 'Public access'}</small>
            </span>
          </button>
        </header>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function RequireAuth({ children }) {
  const { isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    if (!loading && !isAuthenticated) navigate('/login')
  }, [isAuthenticated, loading, navigate])
  if (loading) {
    return (
      <div className="page">
        <div className="card">
          <Activity size={18} /> Checking session…
        </div>
      </div>
    )
  }
  if (!isAuthenticated) return null
  return children
}
