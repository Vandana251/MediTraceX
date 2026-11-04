import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Activity,
  Bell,
  ClipboardList,
  Package,
  Pill,
  ShieldAlert,
  Store,
} from 'lucide-react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { usePlatformData } from '../hooks/usePlatformData'
import { useAuth } from '../context/AuthContext'
import { requestsApi, watchlistApi } from '../services/api'
import { formatNumber } from '../utils/format'
import { ErrorBanner, KpiCard, PageHeader, SkeletonGrid } from '../components/ui'
import { MedicineSearchBar } from '../components/MedicineSearchBar'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const { loading, error, medicines, medicineTotal, pharmacies, summary, reload } = usePlatformData()
  const [myRequests, setMyRequests] = useState([])
  const [watchItems, setWatchItems] = useState([])

  useEffect(() => {
    let cancelled = false
    async function loadPrivate() {
      if (!isAuthenticated) {
        setMyRequests([])
        setWatchItems([])
        return
      }
      try {
        const [reqs, watch] = await Promise.all([requestsApi.my(), watchlistApi.list()])
        if (!cancelled) {
          setMyRequests(Array.isArray(reqs) ? reqs : [])
          setWatchItems(Array.isArray(watch) ? watch : [])
        }
      } catch {
        if (!cancelled) {
          setMyRequests([])
          setWatchItems([])
        }
      }
    }
    loadPrivate()
    return () => {
      cancelled = true
    }
  }, [isAuthenticated])

  const activeRequests = myRequests.filter((item) =>
    ['PENDING', 'ACCEPTED'].includes(String(item.status).toUpperCase())
  )

  const stockChart = [
    { name: 'In stock', value: summary.available, color: '#1b6b57' },
    { name: 'Low stock', value: summary.low, color: '#b7791f' },
    { name: 'Out of stock', value: summary.out, color: '#b42318' },
  ]

  const categories = useMemo(
    () =>
      Object.entries(
        medicines.reduce((acc, med) => {
          acc[med.category] = (acc[med.category] || 0) + 1
          return acc
        }, {})
      )
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6),
    [medicines]
  )

  return (
    <div className="page">
      <PageHeader
        eyebrow="Operations overview"
        title="Medicine availability intelligence"
        description="Live catalog, inventory, and pharmacy network metrics from the MediTraceX API — Find. Verify. Reach."
        actions={
          <button className="btn btn-primary" type="button" onClick={() => navigate('/pharmacies')}>
            Open pharmacy discovery
          </button>
        }
      />

      <div className="capability-row">
        <span className="capability">Prefix Trie search</span>
        <span className="capability">Levenshtein typo recovery</span>
        <span className="capability">Haversine distance</span>
        <span className="capability">Min-heap pharmacy ranking</span>
        <span className="capability">Demand forecast</span>
        <span className="capability">Stock-out risk</span>
      </div>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="eyebrow">Global medicine search</div>
        <h2>Find. Verify. Reach.</h2>
        <p className="sub">
          Search by brand, generic name, or prefix. Misspellings such as “paracetaamol” are recovered by the
          backend fuzzy matcher.
        </p>
        <MedicineSearchBar
          onSelect={(item) => navigate(`/medicines/${item.id}`)}
          onSubmit={(q) => navigate(`/medicines?q=${encodeURIComponent(q)}`)}
        />
      </div>

      <ErrorBanner error={error} onRetry={reload} />
      {loading ? (
        <SkeletonGrid count={8} />
      ) : (
        <div className="grid grid-4" style={{ marginBottom: 18 }}>
          <KpiCard
            icon={<Pill size={18} />}
            value={formatNumber(medicineTotal)}
            label="Total medicines"
            description="Indexed catalog records."
            trend={{ tone: 'neutral', text: 'Trie-indexed catalog' }}
          />
          <KpiCard
            icon={<Store size={18} />}
            value={formatNumber(pharmacies.length)}
            label="Total pharmacies"
            description="Verified partner locations."
            tone="info"
            trend={{ tone: 'up', text: `${pharmacies.filter((p) => p.is_24_7).length} open 24/7` }}
          />
          <KpiCard
            icon={<Package size={18} />}
            value={formatNumber(summary.available)}
            label="Available inventory"
            description={`${formatNumber(summary.units)} units on hand in sampled stock.`}
            trend={{ tone: 'neutral', text: `${formatNumber(summary.total)} inventory rows` }}
          />
          <KpiCard
            icon={<Activity size={18} />}
            value={formatNumber(summary.uniqueLowMedicines)}
            label="Low stock medicines"
            description="Distinct SKUs below safety stock."
            tone="warning"
            trend={{ tone: 'down', text: `${formatNumber(summary.low)} low-stock rows` }}
          />
          <KpiCard
            icon={<ShieldAlert size={18} />}
            value={formatNumber(summary.uniqueOutMedicines)}
            label="Out-of-stock medicines"
            description="Distinct SKUs with zero availability."
            tone="danger"
            trend={{ tone: 'down', text: `${formatNumber(summary.out)} out-of-stock rows` }}
          />
          <KpiCard
            icon={<ClipboardList size={18} />}
            value={isAuthenticated ? formatNumber(activeRequests.length) : '—'}
            label="Active medicine requests"
            description={isAuthenticated ? 'Pending or approved requests.' : 'Sign in to track requests.'}
            tone="info"
          />
          <KpiCard
            icon={<Bell size={18} />}
            value={isAuthenticated ? formatNumber(watchItems.length) : '—'}
            label="Watchlist items"
            description={isAuthenticated ? 'Active restock subscriptions.' : 'Sign in to manage alerts.'}
          />
          <KpiCard
            icon={<ShieldAlert size={18} />}
            value={formatNumber(summary.uniqueAtRiskMedicines)}
            label="High stock-out risk medicines"
            description="Distinct SKUs at or below the safety threshold in live inventory."
            tone="danger"
            trend={{ tone: 'neutral', text: 'From inventory, not estimated' }}
          />
        </div>
      )}

      <div className="grid grid-2">
        <div className="card">
          <h3>Network stock distribution</h3>
          <p className="sub">Sampled pharmacy inventory status from live APIs.</p>
          {loading ? (
            <div style={{ height: 240 }} />
          ) : summary.total === 0 ? (
            <p className="sub">No inventory records returned.</p>
          ) : (
            <div style={{ height: 260 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={stockChart} dataKey="value" nameKey="name" innerRadius={64} outerRadius={92} paddingAngle={3}>
                    {stockChart.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="card">
          <h3>Therapeutic category mix</h3>
          <p className="sub">Classifications currently loaded from the catalog.</p>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Medicines</th>
                </tr>
              </thead>
              <tbody>
                {categories.map(([name, count]) => (
                  <tr key={name}>
                    <td>{name}</td>
                    <td>
                      <strong>{count}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: 16 }}>
            <Link className="muted-link" to="/analytics">
              Open analytics →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
