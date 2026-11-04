import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, Eye, EyeOff, KeyRound, Lock, Mail, Phone, RotateCcw, ShieldCheck, UserCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { authApi } from '../services/api'
import { ErrorBanner, LogoMark, PageHeader } from '../components/ui'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()

  // Login form state
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  // Forgot password mode state
  const [isForgotMode, setIsForgotMode] = useState(false)
  const [forgotStep, setForgotStep] = useState(1) // 1: enter email/phone, 2: enter otp & new password
  const [forgotIdentifier, setForgotIdentifier] = useState('')
  const [otp, setOtp] = useState('')
  const [demoOtp, setDemoOtp] = useState('')
  const [emailSent, setEmailSent] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showNewPassword, setShowNewPassword] = useState(false)

  if (isAuthenticated) {
    navigate('/', { replace: true })
    return null
  }

  // 1. Regular Login submit
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
      await login({ email: identifier.trim(), password })
      navigate('/')
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.')
    } finally {
      setLoading(false)
    }
  }

  // 2. Request Forgot Password OTP
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
        setSuccessMsg(res.message || `Verification code has been sent directly to ${forgotIdentifier}! Please check your email inbox.`)
      } else {
        setDemoOtp(res.demo_otp || '123456')
        setOtp(res.demo_otp || '123456') // Pre-fill for user convenience in local dev
        setSuccessMsg(res.message || 'Verification code generated!')
      }
      setForgotStep(2)
    } catch (err) {
      setError(err.message || 'Account not found. Please check email/phone.')
    } finally {
      setLoading(false)
    }
  }

  // 3. Reset Password with OTP submit
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

      setSuccessMsg('Password updated successfully! You can now log in.')
      setIdentifier(forgotIdentifier.trim())
      setPassword(newPassword)
      setIsForgotMode(false)
      setForgotStep(1)
    } catch (err) {
      setError(err.message || 'Failed to reset password. Please check OTP code.')
    } finally {
      setLoading(false)
    }
  }

  function fillDemo(demoId, demoPw) {
    setIdentifier(demoId)
    setPassword(demoPw)
    setError(null)
    setSuccessMsg(null)
  }

  return (
    <div className="page" style={{ maxWidth: 520, margin: '40px auto' }}>
      <PageHeader
        eyebrow="Access Portal"
        title={isForgotMode ? "Reset Password" : "Sign in to MediTraceX"}
        description={
          isForgotMode
            ? "Verify your registered email or phone number to set a new secure password."
            : "Authenticate with JWT security to access private restock watchlists, track medicine requests, and manage inventory."
        }
      />

      <ErrorBanner error={error} />

      {successMsg && (
        <div
          className="card"
          style={{
            background: 'var(--teal-soft)',
            border: '1px solid var(--teal)',
            color: 'var(--teal-deep)',
            padding: '12px 16px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontSize: '0.9rem',
            borderRadius: 'var(--radius)'
          }}
        >
          <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
          <div>{successMsg}</div>
        </div>
      )}

      {/* =================================================================== */}
      {/* FORGOT PASSWORD WORKFLOW */}
      {/* =================================================================== */}
      {isForgotMode ? (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <button
            type="button"
            onClick={() => {
              setIsForgotMode(false)
              setError(null)
              setSuccessMsg(null)
            }}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--teal)',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: '0.85rem',
              fontWeight: 600,
              padding: 0,
              alignSelf: 'flex-start',
            }}
          >
            <ArrowLeft size={16} /> Back to Sign in
          </button>

          {forgotStep === 1 ? (
            <form onSubmit={handleRequestOtp} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div className="field">
                <label className="label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Mail size={14} /> / <Phone size={14} />
                  Registered Email Address or Phone Number
                </label>
                <input
                  className="input"
                  type="text"
                  placeholder="e.g. rahul.sharma@example.com or 9876543210"
                  value={forgotIdentifier}
                  onChange={(e) => setForgotIdentifier(e.target.value)}
                  required
                  autoFocus
                />
              </div>

              <button
                className="btn btn-primary"
                type="submit"
                disabled={loading}
                style={{ justifyContent: 'center', marginTop: 4 }}
              >
                {loading ? 'Sending Code…' : 'Send Verification Code (OTP)'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div
                style={{
                  background: 'var(--bg-subtle, #f8fafc)',
                  border: '1px dashed var(--line-strong, #cbd5e1)',
                  padding: '10px 14px',
                  borderRadius: 6,
                  fontSize: '0.85rem',
                }}
              >
                Verification code requested for <strong>{forgotIdentifier}</strong>
                {emailSent ? (
                  <div style={{ marginTop: 6, color: 'var(--teal-deep)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span>📩</span> An email with your 6-digit OTP code has been dispatched to your inbox! Please check your Gmail (and Spam folder).
                  </div>
                ) : (
                  demoOtp && (
                    <div style={{ marginTop: 6, color: 'var(--teal-deep)', fontWeight: 600 }}>
                      ⚡ Demo Code (SMTP server pending): <code>{demoOtp}</code> (or default <code>123456</code>)
                    </div>
                  )
                )}
              </div>

              <div className="field">
                <label className="label">6-Digit Verification Code (OTP)</label>
                <input
                  className="input"
                  type="text"
                  placeholder="e.g. 123456"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                  maxLength={10}
                  autoFocus
                />
              </div>

              <div className="field">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <label className="label" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Lock size={14} /> New Password (min. 6 characters)
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--teal)',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4,
                      fontWeight: 600,
                    }}
                  >
                    {showNewPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                    {showNewPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <input
                    className="input"
                    type={showNewPassword ? 'text' : 'password'}
                    placeholder="Enter new secure password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    style={{ paddingRight: 42, width: '100%' }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    style={{
                      position: 'absolute',
                      right: 8,
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      color: 'var(--muted)',
                      padding: 6,
                      display: 'flex',
                    }}
                  >
                    {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="field">
                <label className="label">Confirm New Password</label>
                <input
                  className="input"
                  type={showNewPassword ? 'text' : 'password'}
                  placeholder="Re-enter new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>

              <button
                className="btn btn-primary"
                type="submit"
                disabled={loading}
                style={{ justifyContent: 'center', marginTop: 8 }}
              >
                {loading ? 'Updating Password…' : 'Save New Password & Continue'}
              </button>
            </form>
          )}
        </div>
      ) : (
        /* =================================================================== */
        /* STANDARD SIGN IN WORKFLOW */
        /* =================================================================== */
        <form className="card" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="field">
            <label className="label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Mail size={14} /> / <Phone size={14} />
              </span>
              Email Address or Phone Number
            </label>
            <input
              className="input"
              type="text"
              placeholder="e.g. rahul.sharma@example.com or +91-9876543210"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="field">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <label className="label" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Lock size={14} />
                Password
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
                  fontWeight: 600,
                }}
              >
                {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                {showPassword ? 'Hide password' : 'Show password'}
              </button>
            </div>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <input
                className="input"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ paddingRight: 42, width: '100%' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? 'Hide password' : 'Show password'}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
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
                  borderRadius: 4,
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {/* Forgot Password link */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: -6 }}>
            <button
              type="button"
              onClick={() => {
                setIsForgotMode(true)
                setForgotIdentifier(identifier)
                setForgotStep(1)
                setError(null)
                setSuccessMsg(null)
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--teal)',
                fontSize: '0.85rem',
                cursor: 'pointer',
                padding: '2px 0',
                fontWeight: 600,
                textDecoration: 'underline',
              }}
            >
              Forgot password?
            </button>
          </div>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={loading}
            style={{ justifyContent: 'center', marginTop: 4 }}
          >
            {loading ? 'Authenticating…' : 'Sign in'}
          </button>

          <div style={{ textAlign: 'center', marginTop: 8, fontSize: '0.9rem', color: 'var(--ink-soft)' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--teal)', fontWeight: 600 }}>
              Create one here
            </Link>
          </div>
        </form>
      )}

      {/* Quick Demo Credentials */}
      <div className="card" style={{ marginTop: 20 }}>
        <h4 style={{ margin: '0 0 10px', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: 6 }}>
          <KeyRound size={16} color="var(--teal)" /> Quick Demo Credentials
        </h4>
        <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: 'var(--muted)' }}>
          Select a pre-seeded account profile to populate credentials (supports Email or Phone):
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fillDemo('rahul.sharma@example.com', 'hashed_pw_user_1')}
              style={{ flex: 1, justifyContent: 'space-between', fontSize: '0.85rem', padding: '8px 12px' }}
            >
              <span>👤 <strong>Rahul Sharma</strong> (Email)</span>
              <span style={{ color: 'var(--muted)' }}>Fill</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fillDemo('+91-9876543210', 'hashed_pw_user_1')}
              title="Test Phone Number Login"
              style={{ justifyContent: 'center', fontSize: '0.85rem', padding: '8px 12px', whiteSpace: 'nowrap' }}
            >
              📱 Phone (+91-9876543210)
            </button>
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fillDemo('admin@medicareplus.com', 'hashed_pw_admin_1')}
              style={{ flex: 1, justifyContent: 'space-between', fontSize: '0.85rem', padding: '8px 12px' }}
            >
              <span>🏥 <strong>MediCare Admin</strong> (Email)</span>
              <span style={{ color: 'var(--muted)' }}>Fill</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => fillDemo('+91-9876543214', 'hashed_pw_admin_1')}
              title="Test Phone Number Login"
              style={{ justifyContent: 'center', fontSize: '0.85rem', padding: '8px 12px', whiteSpace: 'nowrap' }}
            >
              📱 Phone (+91-9876543214)
            </button>
          </div>

          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => fillDemo('admin@meditracex.io', 'hashed_pw_sys_1')}
            style={{ justifyContent: 'space-between', fontSize: '0.85rem', padding: '8px 12px' }}
          >
            <span>🛡️ <strong>System Admin</strong> (admin@meditracex.io)</span>
            <span style={{ color: 'var(--muted)' }}>Fill</span>
          </button>
        </div>
      </div>
    </div>
  )
}
