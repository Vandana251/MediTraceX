import { Link } from 'react-router-dom'
import { Activity, MapPin, ShieldCheck, Sparkles } from 'lucide-react'
import { APP_NAME, APP_TAGLINE } from '../config'
import { LogoMark } from './ui'

export function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="auth-screen">
      <section className="auth-panel">
        <Link to="/" className="auth-brand">
          <div className="brand-mark">
            <LogoMark />
          </div>
          <div>
            <strong>{APP_NAME}</strong>
            <span>{APP_TAGLINE}</span>
          </div>
        </Link>
        <div>
          <p className="eyebrow" style={{ color: '#9ad4ce' }}>Healthcare intelligence</p>
          <h1>Find the right medicine. Verify stock. Reach the nearest pharmacy.</h1>
          <p>
            MediTraceX combines prefix search, typo recovery, geospatial ranking, and demand forecasting
            into a single operations console for pharmacy networks.
          </p>
          <ul className="auth-points">
            <li>
              <ShieldCheck size={16} /> Live inventory across verified partner pharmacies
            </li>
            <li>
              <MapPin size={16} /> Distance-ranked discovery with Haversine and min-heap ranking
            </li>
            <li>
              <Sparkles size={16} /> Demand forecasts and stock-out risk from the model API
            </li>
            <li>
              <Activity size={16} /> Secure JWT sessions for requests and restock alerts
            </li>
          </ul>
        </div>
        <p className="auth-foot">Connected to the live MediTraceX FastAPI service.</p>
      </section>
      <section className="auth-form">
        <div className="auth-card">
          <h2>{title}</h2>
          <p className="sub">{subtitle}</p>
          {children}
        </div>
      </section>
    </div>
  )
}
