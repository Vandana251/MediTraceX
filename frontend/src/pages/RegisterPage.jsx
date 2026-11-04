import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Lock, Mail, Phone, Shield, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { DEFAULT_LOCATION } from '../config'
import { ErrorBanner, PageHeader } from '../components/ui'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, isAuthenticated } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'customer',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (isAuthenticated) {
    navigate('/', { replace: true })
    return null
  }

  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name || !form.email || !form.phone || !form.password) {
      setError('Please fill in all required fields.')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }

    setLoading(true)
    setError(null)
    try {
      await register({
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        phone: form.phone.trim(),
        password: form.password,
        role: form.role,
        latitude: DEFAULT_LOCATION.latitude,
        longitude: DEFAULT_LOCATION.longitude,
      })
      navigate('/')
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page" style={{ maxWidth: 540, margin: '40px auto' }}>
      <PageHeader
        eyebrow="Account Registration"
        title="Create your account"
        description="Join the MediTraceX network to track emergency stock availability, receive restock triggers, and manage pharmacy allocations."
      />

      <ErrorBanner error={error} />

      <form className="card" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="field">
          <label className="label">
            <User size={14} style={{ display: 'inline', marginRight: 6 }} />
            Full Name
          </label>
          <input
            className="input"
            type="text"
            placeholder="e.g. Dr. Rajesh Kumar"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
            required
            autoFocus
          />
        </div>

        <div className="grid grid-2" style={{ gap: 12 }}>
          <div className="field">
            <label className="label">
              <Mail size={14} style={{ display: 'inline', marginRight: 6 }} />
              Email Address
            </label>
            <input
              className="input"
              type="email"
              placeholder="rajesh@example.com"
              value={form.email}
              onChange={(e) => updateField('email', e.target.value)}
              required
            />
          </div>

          <div className="field">
            <label className="label">
              <Phone size={14} style={{ display: 'inline', marginRight: 6 }} />
              Phone Number
            </label>
            <input
              className="input"
              type="tel"
              placeholder="+91-9876543210"
              value={form.phone}
              onChange={(e) => updateField('phone', e.target.value)}
              required
            />
          </div>
        </div>

        <div className="grid grid-2" style={{ gap: 12 }}>
          <div className="field">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <label className="label" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Lock size={14} />
                Password (min. 6 chars)
              </label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--teal)',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                  padding: '2px 4px',
                  fontWeight: 600
                }}
              >
                {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <input
                className="input"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => updateField('password', e.target.value)}
                required
                style={{ paddingRight: 42, width: '100%' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? "Hide password" : "Show password"}
                aria-label={showPassword ? "Hide password" : "Show password"}
                style={{
                  position: 'absolute',
                  right: 8,
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--muted)',
                  padding: 6,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 4
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="field">
            <label className="label">
              <Shield size={14} style={{ display: 'inline', marginRight: 6 }} />
              Account Role
            </label>
            <select
              className="select"
              value={form.role}
              onChange={(e) => updateField('role', e.target.value)}
            >
              <option value="customer">Patient / Customer</option>
              <option value="pharmacy_admin">Pharmacy Staff / Manager</option>
            </select>
          </div>
        </div>

        <button className="btn btn-primary" type="submit" disabled={loading} style={{ justifyContent: 'center', marginTop: 8 }}>
          {loading ? 'Creating Account…' : 'Register Account'}
        </button>

        <div style={{ textAlign: 'center', marginTop: 8, fontSize: '0.9rem', color: 'var(--ink-soft)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--teal)', fontWeight: 600 }}>
            Sign in here
          </Link>
        </div>
      </form>
    </div>
  )
}
