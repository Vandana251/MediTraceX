import { Link } from 'react-router-dom'
import { AlertCircle, Home } from 'lucide-react'
import { PageHeader } from '../components/ui'

export default function NotFoundPage() {
  return (
    <div className="page" style={{ maxWidth: 580, margin: '60px auto', textAlign: 'center' }}>
      <div
        style={{
          width: 64,
          height: 64,
          borderRadius: 16,
          background: 'var(--danger-soft)',
          color: 'var(--danger)',
          display: 'grid',
          placeItems: 'center',
          margin: '0 auto 20px',
        }}
      >
        <AlertCircle size={32} />
      </div>

      <PageHeader
        eyebrow="404 Error"
        title="Page Not Found"
        description="The URL or resource you requested does not exist or has been moved."
      />

      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 24 }}>
        <Link to="/" className="btn btn-primary">
          <Home size={16} /> Return to Dashboard
        </Link>
        <Link to="/medicines" className="btn btn-secondary">
          Browse Medicines
        </Link>
      </div>
    </div>
  )
}
