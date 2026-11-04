import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { DEFAULT_LOCATION } from '../config'
import { AuthLayout } from '../components/AuthLayout'
import { ErrorBanner } from '../components/ui'

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

  useEffect(() => {
    if (isAuthenticated) navigate('/', { replace: true })
  }, [isAuthenticated, navigate])

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
    <AuthLayout
      title="Create your account"
      subtitle="Join to request medicines, watch restocks, and manage pharmacy inventory."
    >
      <ErrorBanner error={error} />
      <form className="form-stack" onSubmit={handleSubmit}>
        <div className="field">
          <label className="label">Full name</label>
          <input className="input" value={form.name} onChange={(e) => updateField('name', e.target.value)} required autoFocus />
        </div>
        <div className="field">
          <label className="label">Email</label>
          <input className="input" type="email" value={form.email} onChange={(e) => updateField('email', e.target.value)} required />
        </div>
        <div className="field">
          <label className="label">Phone</label>
          <input className="input" type="tel" value={form.phone} onChange={(e) => updateField('phone', e.target.value)} required />
        </div>
        <div className="field">
          <label className="label">Password</label>
          <div style={{ position: 'relative' }}>
            <input
              className="input"
              type={showPassword ? 'text' : 'password'}
              value={form.password}
              onChange={(e) => updateField('password', e.target.value)}
              required
              style={{ paddingRight: 42 }}
            />
            <button className="icon-btn" type="button" onClick={() => setShowPassword((v) => !v)} style={{ position: 'absolute', right: 4, top: 4, width: 32, height: 32 }}>
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        <div className="field">
          <label className="label">Account role</label>
          <select className="select" value={form.role} onChange={(e) => updateField('role', e.target.value)}>
            <option value="customer">Patient / customer</option>
            <option value="pharmacy_admin">Pharmacy staff</option>
          </select>
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Creating account…' : 'Create account'}
        </button>
        <p className="sub" style={{ textAlign: 'center' }}>
          Already registered? <Link className="muted-link" to="/login">Sign in</Link>
        </p>
      </form>
    </AuthLayout>
  )
}
