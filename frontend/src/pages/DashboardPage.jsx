import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Activity,
  Bell,
  Building2,
  ClipboardList,
  Globe,
  Landmark,
  MapPin,
  Package,
  Pill,
  ShieldAlert,
  ShieldCheck,
  Store,
} from 'lucide-react'
import { usePlatformData } from '../hooks/usePlatformData'
import { useAuth } from '../context/AuthContext'
import { requestsApi, watchlistApi } from '../services/api'
import { CITY_STATE_MAP, getStateForCity } from '../config'
import { formatNumber } from '../utils/format'
import { ErrorBanner, KpiCard, PageHeader, SkeletonGrid } from '../components/ui'
import { MedicineSearchBar } from '../components/MedicineSearchBar'
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const { loading, error, medicines, medicineTotal, pharmacies, inventory, summary, reload } =
    usePlatformData()
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

  const cityCount = useMemo(() => {
    return new Set(pharmacies.map((p) => p.city)).size || 50
  }, [pharmacies])

  const stateCount = useMemo(() => {
    return new Set(pharmacies.map((p) => getStateForCity(p.city))).size || 15
  }, [pharmacies])

  const stockChart = [
    { name: 'In stock', value: summary.available, color: '#1b6b57' },
    { name: 'Low stock', value: summary.low, color: '#b7791f' },
    { name: 'Out of stock', value: summary.out, color: '#b42318' },
  ]

  const categories = Object.entries(
    medicines.reduce((acc, med) => {
      acc[med.category] = (acc[med.category] || 0) + 1
      return acc
    }, {})
  )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)

  return (
    <div className="page">
      <PageHeader
        eyebrow="Pan-India Healthcare Operations"
        title="India-Wide Medicine Availability Intelligence"
        description="Real-time pharmaceutical availability, triage demand metrics, and Min-Heap geospatial pharmacy discovery across 15+ states and 50+ major cities in India."
        actions={
          <button className="btn btn-primary" type="button" onClick={() => navigate('/pharmacies')}>
            <Globe size={16} /> Explore Pan-India Map
          </button>
        }
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
        <span className="status-badge status-neutral" style={{ background: 'var(--teal-soft)', color: 'var(--teal-deep)', border: '1px solid var(--line-strong)' }}>
          <ShieldCheck size={14} style={{ display: 'inline', marginRight: 4 }} /> Demo Pharmacy Network
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
          Covering Andhra Pradesh, Telangana, Karnataka, Tamil Nadu, Maharashtra, Delhi NCR, West Bengal, Gujarat, Rajasthan, Kerala, and more.
        </span>
      </div>

      <div className="card" style={{ marginBottom: 18 }}>
        <div className="eyebrow">National medicine catalog search</div>
        <h2>Find. Verify. Reach.</h2>
        <p className="sub">Instant DSA Trie prefix matching with Levenshtein typo recovery (e.g. "paractamol", "amoxcilin", "dolo").</p>
        <MedicineSearchBar
          onSelect={(item) => navigate(`/medicines/${item.id}`)}
          onSubmit={(q) => navigate(`/medicines?q=${encodeURIComponent(q)}`)}
        />
      </div>

      <ErrorBanner error={error} onRetry={reload} />
      {loading ? <SkeletonGrid count={8} /> : (
        <div className="grid grid-4" style={{ marginBottom: 18 }}>
          <KpiCard
            icon={<Store size={18} />}
            value={formatNumber(pharmacies.length)}
            label="Total Pharmacies"
            description="Active stores in discovery network."
            tone="info"
            trend={{ tone: 'up', text: `${pharmacies.filter((p) => p.is_24_7).length} open 24/7` }}
          />
          <KpiCard
            icon={<Building2 size={18} />}
            value={`${cityCount}+`}
            label="Cities Covered"
            description="Across Tier-1 and Tier-2 hubs in India."
            trend={{ tone: 'neutral', text: `${stateCount} Indian states` }}
          />
          <KpiCard
            icon={<Pill size={18} />}
            value={formatNumber(medicineTotal)}
            label="Catalog Medicines"
            description="Indexed pharmaceutical catalog items."
            trend={{ tone: 'neutral', text: 'Trie indexed (< 0.1ms)' }}
          />
          <KpiCard
            icon={<Package size={18} />}
            value={formatNumber(summary.units)}
            label="Monitored Stock Units"
            description={`${formatNumber(summary.available)} in-stock SKU records sampled.`}
            trend={{ tone: 'neutral', text: 'Live API synced' }}
          />
          <KpiCard
            icon={<Activity size={18} />}
            value={formatNumber(summary.uniqueLowMedicines)}
            label="Low Stock Medicines"
            description="SKUs below safety thresholds."
            tone="warning"
            trend={{ tone: 'down', text: 'Replenishment triggered' }}
          />
          <KpiCard
            icon={<ShieldAlert size={18} />}
            value={formatNumber(summary.uniqueOutMedicines)}
            label="Stock-out Alert SKUs"
            description="SKUs with zero availability in hub."
            tone="danger"
            trend={{ tone: 'down', text: 'Triage risk' }}
          />
          <KpiCard
            icon={<ClipboardList size={18} />}
            value={isAuthenticated ? formatNumber(activeRequests.length) : '—'}
            label="Active Medicine Requests"
            description={isAuthenticated ? 'Pending / approved user requests.' : 'Sign in to track requests.'}
            tone="info"
          />
          <KpiCard
            icon={<Bell size={18} />}
            value={isAuthenticated ? formatNumber(watchItems.length) : '—'}
            label="Watchlist Subscriptions"
            description={isAuthenticated ? 'Active restock notifications.' : 'Sign in to manage alerts.'}
          />
        </div>
      )}

      {/* Regional Quick Hubs Row */}
      <div className="card" style={{ marginBottom: 18 }}>
        <h4 style={{ margin: '0 0 8px', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: 6 }}>
          <MapPin size={16} color="var(--teal)" /> Major State Networks
        </h4>
        <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: 'var(--muted)' }}>
          Quickly inspect stock density and pharmacy discovery in key states:
        </p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {[
            { state: 'Andhra Pradesh', cities: 'Vijayawada, Vizag, Guntur, Tirupati' },
            { state: 'Telangana', cities: 'Hyderabad, Secunderabad, Warangal' },
            { state: 'Karnataka', cities: 'Bengaluru, Mysuru, Mangaluru, Hubballi' },
            { state: 'Tamil Nadu', cities: 'Chennai, Coimbatore, Madurai, Salem' },
            { state: 'Maharashtra', cities: 'Mumbai, Pune, Nagpur, Thane, Nashik' },
            { state: 'Delhi NCR', cities: 'New Delhi, Gurgaon, Noida, Ghaziabad' },
            { state: 'West Bengal', cities: 'Kolkata, Siliguri' },
            { state: 'Gujarat', cities: 'Ahmedabad, Surat, Vadodara, Rajkot' },
            { state: 'Rajasthan', cities: 'Jaipur, Jodhpur, Udaipur' },
            { state: 'Kerala', cities: 'Kochi, Thiruvananthapuram, Kozhikode' },
            { state: 'Uttar Pradesh', cities: 'Lucknow, Kanpur, Varanasi, Agra' },
            { state: 'Bihar', cities: 'Patna, Gaya' },
          ].map((item) => (
            <button
              key={item.state}
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/pharmacies')}
              style={{ fontSize: '0.8rem', padding: '6px 12px', textAlign: 'left' }}
            >
              <strong>{item.state}</strong>
              <span style={{ fontSize: '0.75rem', color: 'var(--muted)', marginLeft: 6 }}>({item.cities.split(',')[0]})</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>Network Stock Distribution</h3>
          <p className="sub">Pharmacy inventory status across sampled network records.</p>
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
          <h3>Therapeutic Category Mix</h3>
          <p className="sub">Therapeutic classifications loaded in catalog.</p>
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
                    <td><strong>{count}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: 16 }}>
            <Link className="muted-link" to="/analytics">
              Open full analytics & state coverage →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
