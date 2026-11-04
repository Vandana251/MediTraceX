import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Eye, EyeOff, Lock, Mail, Phone } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../services/api'
import { AuthLayout } from '../components/AuthLayout'
import { ErrorBanner } from '../components/ui'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [isForgotMode, setIsForgotMode] = useState(false)
  const [forgotStep, setForgotStep] = useState(1)
  const [forgotIdentifier, setForgotIdentifier] = useState('')
  const [otp, setOtp] = useState('')
  const [demoOtp, setDemoOtp] = useState('')
  const [emailSent, setEmailSent] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showNewPassword, setShowNewPassword] = useState(false)

  useEffect(() => {
    if (isAuthenticated) navigate('/', { replace: true })
  }, [isAuthenticated, navigate])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!identifier || !password) {
      setError('Please provide your email address or phone number, and password.')
      return
    }
    setLoading(true)
    setError(null)
    setSuccessMsg(null)
    try {
      await login({ email: identifier.trim(), identifier: identifier.trim(), password })
      navigate('/')
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.')
    } finally {
      setLoading(false)
    }
  }

  async function handleRequestOtp(e) {
    e.preventDefault()
    if (!forgotIdentifier.trim()) {
      setError('Please provide your registered email address or phone number.')
      return
    }
    setLoading(true)
    setError(null)
    setSuccessMsg(null)
    try {
      const res = await authApi.forgotPassword({ identifier: forgotIdentifier.trim() })
      const wasRealSent = Boolean(res.email_sent)
      setEmailSent(wasRealSent)
      if (wasRealSent) {
        setDemoOtp('')
        setOtp('')
        setSuccessMsg(res.message || `A verification code was sent to ${forgotIdentifier}.`)
      } else {
        setDemoOtp(res.demo_otp || '')
        setOtp(res.demo_otp || '')
        setSuccessMsg(res.message || 'Verification code generated.')
      }
      setForgotStep(2)
    } catch (err) {
      setError(err.message || 'Account not found. Please check email/phone.')
    } finally {
      setLoading(false)
    }
  }

  async function handleResetPassword(e) {
    e.preventDefault()
    if (!otp.trim()) {
      setError('Please enter the 6-digit verification code.')
      return
    }
    if (!newPassword || newPassword.length < 6) {
      setError('New password must be at least 6 characters.')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('New password and confirm password do not match.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await authApi.resetPassword({
        identifier: forgotIdentifier.trim(),
        otp: otp.trim(),
        new_password: newPassword,
      })
      setSuccessMsg('Password updated. You can now sign in.')
      setIdentifier(forgotIdentifier.trim())
      setPassword('')
      setIsForgotMode(false)
      setForgotStep(1)
    } catch (err) {
      setError(err.message || 'Failed to reset password. Please check the code.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title={isForgotMode ? 'Reset password' : 'Sign in'}
      subtitle={
        isForgotMode
          ? 'Verify your registered email or phone to set a new password.'
          : 'Access watchlists, medicine requests, and pharmacy operations.'
      }
    >
      <ErrorBanner error={error} />
      {successMsg ? (
        <div className="alert success" style={{ marginBottom: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
          <CheckCircle2 size={16} /> {successMsg}
        </div>
      ) : null}

      {isForgotMode ? (
        <div className="form-stack">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setIsForgotMode(false)
              setError(null)
              setSuccessMsg(null)
            }}
            style={{ alignSelf: 'flex-start' }}
          >
            <ArrowLeft size={16} /> Back to sign in
          </button>
          {forgotStep === 1 ? (
            <form onSubmit={handleRequestOtp} className="form-stack">
              <div className="field">
                <label className="label">
                  <Mail size={14} /> / <Phone size={14} /> Email or phone
                </label>
                <input
                  className="input"
                  value={forgotIdentifier}
                  onChange={(e) => setForgotIdentifier(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? 'Sending code…' : 'Send verification code'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="form-stack">
              {demoOtp && !emailSent ? (
                <div className="alert info">Verification code: {demoOtp}</div>
              ) : null}
              <div className="field">
                <label className="label">6-digit code</label>
                <input className="input" value={otp} onChange={(e) => setOtp(e.target.value)} required />
              </div>
              <div className="field">
                <label className="label">
                  <Lock size={14} /> New password
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    className="input"
                    type={showNewPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    style={{ paddingRight: 42 }}
                  />
                  <button className="icon-btn" type="button" onClick={() => setShowNewPassword((v) => !v)} style={{ position: 'absolute', right: 4, top: 4, width: 32, height: 32 }}>
                    {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
              <div className="field">
                <label className="label">Confirm password</label>
                <input
                  className="input"
                  type={showNewPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? 'Updating…' : 'Save new password'}
              </button>
            </form>
          )}
        </div>
      ) : (
        <form className="form-stack" onSubmit={handleSubmit}>
          <div className="field">
            <label className="label">Email or phone</label>
            <input
              className="input"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="name@clinic.com or +91…"
              required
              autoFocus
            />
          </div>
          <div className="field">
            <label className="label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                className="input"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ paddingRight: 42 }}
              />
              <button className="icon-btn" type="button" onClick={() => setShowPassword((v) => !v)} style={{ position: 'absolute', right: 4, top: 4, width: 32, height: 32 }}>
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="muted-link"
              onClick={() => {
                setIsForgotMode(true)
                setForgotIdentifier(identifier)
                setForgotStep(1)
                setError(null)
                setSuccessMsg(null)
              }}
              style={{ background: 'none', border: 0 }}
            >
              Forgot password?
            </button>
          </div>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
          <p className="sub" style={{ textAlign: 'center' }}>
            New to MediTraceX? <Link className="muted-link" to="/register">Create an account</Link>
          </p>
        </form>
      )}
    </AuthLayout>
  )
}
