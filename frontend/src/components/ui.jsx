export function LogoMark({ size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="26" height="26" rx="8" fill="currentColor" opacity="0.12" />
      <path d="M16 8v16M8 16h16" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

export function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <div className="page-header">
      <div>
        {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {actions}
    </div>
  )
}

export function KpiCard({ icon, value, label, description, tone = 'teal', trend }) {
  return (
    <div className="card kpi">
      {icon ? <div className={`kpi-icon ${tone}`}>{icon}</div> : null}
      <div>
        <strong>{value}</strong>
        <span>{label}</span>
        {description ? <p>{description}</p> : null}
        {trend ? <div className={`trend ${trend.tone}`}>{trend.text}</div> : null}
      </div>
    </div>
  )
}

export function StatusBadge({ tone = 'neutral', children }) {
  return <span className={`badge ${tone}`}>{children}</span>
}

export function Skeleton({ height = 16, width = '100%', radius = 10 }) {
  return <div className="skeleton" style={{ height, width, borderRadius: radius }} />
}

export function SkeletonGrid({ count = 4 }) {
  return (
    <div className="grid grid-4">
      {Array.from({ length: count }).map((_, i) => (
        <div className="card" key={i}>
          <Skeleton height={42} width={42} />
          <div style={{ height: 10 }} />
          <Skeleton height={22} width="50%" />
          <div style={{ height: 8 }} />
          <Skeleton height={12} width="80%" />
        </div>
      ))}
    </div>
  )
}

export function EmptyState({ title, description, action }) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}

export function ErrorBanner({ error, onRetry }) {
  if (!error) return null
  return (
    <div className="alert danger" role="alert">
      {error}
      {onRetry ? (
        <>
          {' '}
          <button className="btn btn-ghost" type="button" onClick={onRetry} style={{ marginLeft: 8 }}>
            Retry
          </button>
        </>
      ) : null}
    </div>
  )
}

export function Spinner({ label = 'Loading' }) {
  return (
    <div className="empty">
      <Skeleton height={18} width={180} />
      <p>{label}</p>
    </div>
  )
}
