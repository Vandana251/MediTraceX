import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Bookmark,
  Calendar,
  CheckCircle2,
  ClipboardList,
  LogOut,
  Mail,
  MapPin,
  Phone,
  Shield,
  User,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { requestsApi, watchlistApi } from '../services/api'
import { RequireAuth } from '../components/AppShell'
import { ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { formatDate, initials } from '../utils/format'

function ProfileInner() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [requestsCount, setRequestsCount] = useState(0)
  const [watchlistCount, setWatchlistCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function loadStats() {
      try {
        const [reqs, watch] = await Promise.all([
          requestsApi.my().catch(() => []),
          watchlistApi.list().catch(() => []),
        ])
        if (!cancelled) {
          setRequestsCount(Array.isArray(reqs) ? reqs.length : 0)
          setWatchlistCount(Array.isArray(watch) ? watch.length : 0)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadStats()
    return () => {
      cancelled = true
    }
  }, [])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const roleLabel = (user?.role || 'customer').replace('_', ' ').toUpperCase()
  const roleTone =
    user?.role === 'system_admin'
      ? 'danger'
      : user?.role === 'pharmacy_admin' || user?.role === 'pharmacy'
      ? 'gold'
      : 'teal'

  return (
    <div className="page" style={{ maxWidth: 840 }}>
      <PageHeader
        eyebrow="Account Overview"
        title="User Profile & Security"
        description="View your authenticated credentials, registered system role, and access rights across the platform."
      />

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div
              style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                background: 'var(--teal)',
                color: '#fff',
                display: 'grid',
                placeItems: 'center',
                fontSize: '1.4rem',
                fontWeight: 700,
              }}
            >
              {initials(user?.name || 'User')}
            </div>
            <div>
              <h2 style={{ margin: '0 0 4px', fontSize: '1.4rem' }}>{user?.name || 'User'}</h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <StatusBadge tone={roleTone}>{roleLabel}</StatusBadge>
                <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
                  User ID #{user?.id || '—'}
                </span>
              </div>
            </div>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleLogout}
            style={{ color: 'var(--danger)', borderColor: 'var(--danger-soft)' }}
          >
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </div>

      <div className="grid grid-3" style={{ marginBottom: 20 }}>
        <div className="card">
          <h4 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <ClipboardList size={16} color="var(--teal)" /> Medicine Requests
          </h4>
          <h2 style={{ margin: '0 0 4px', fontSize: '1.8rem' }}>{requestsCount}</h2>
          <Link to="/requests" style={{ fontSize: '0.85rem', color: 'var(--teal)', fontWeight: 600 }}>
            View requests →
          </Link>
        </div>

        <div className="card">
          <h4 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Bookmark size={16} color="var(--gold)" /> Restock Watchlist
          </h4>
          <h2 style={{ margin: '0 0 4px', fontSize: '1.8rem' }}>{watchlistCount}</h2>
          <Link to="/watchlist" style={{ fontSize: '0.85rem', color: 'var(--teal)', fontWeight: 600 }}>
            Manage watchlist →
          </Link>
        </div>

        <div className="card">
          <h4 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Shield size={16} color="var(--success)" /> Access Level
          </h4>
          <h2 style={{ margin: '0 0 4px', fontSize: '1.4rem' }}>{roleLabel}</h2>
          <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>JWT Authenticated</span>
        </div>
      </div>

      <div className="card">
        <h3 style={{ margin: '0 0 16px', fontSize: '1.1rem' }}>Account Details</h3>
        <div className="grid grid-2" style={{ gap: 16 }}>
          <div className="field">
            <label className="label"><Mail size={14} style={{ display: 'inline', marginRight: 6 }} /> Email Address</label>
            <input className="input" value={user?.email || '—'} readOnly />
          </div>

          <div className="field">
            <label className="label"><Phone size={14} style={{ display: 'inline', marginRight: 6 }} /> Phone Number</label>
            <input className="input" value={user?.phone || '—'} readOnly />
          </div>

          <div className="field">
            <label className="label"><MapPin size={14} style={{ display: 'inline', marginRight: 6 }} /> GPS Coordinates</label>
            <input
              className="input"
              value={user?.latitude && user?.longitude ? `${user.latitude.toFixed(4)}° N, ${user.longitude.toFixed(4)}° E` : 'Hyderabad (17.4435° N, 78.3780° E)'}
              readOnly
            />
          </div>

          <div className="field">
            <label className="label"><Calendar size={14} style={{ display: 'inline', marginRight: 6 }} /> Account Status</label>
            <input
              className="input"
              value={user?.created_at ? `Active since ${formatDate(user.created_at)}` : 'Active & Verified'}
              readOnly
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ProfilePage() {
  return (
    <RequireAuth>
      <ProfileInner />
    </RequireAuth>
  )
}
