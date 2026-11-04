import { useMemo } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { usePlatformData } from '../hooks/usePlatformData'
import { getStateForCity } from '../config'
import { ErrorBanner, PageHeader } from '../components/ui'
import { getSessionSearches } from '../utils/sessionSearch'
import { formatNumber } from '../utils/format'

export default function AnalyticsPage() {
  const { medicines, pharmacies, summary, error, reload } = usePlatformData()

  const stateData = useMemo(() => {
    const map = {}
    pharmacies.forEach((p) => {
      const state = getStateForCity(p.city)
      map[state] = (map[state] || 0) + 1
    })
    return Object.entries(map)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
  }, [pharmacies])

  const categoryData = useMemo(() => {
    const map = {}
    medicines.forEach((m) => {
      map[m.category] = (map[m.category] || 0) + 1
    })
    return Object.entries(map)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
  }, [medicines])

  const searches = useMemo(() => {
    const counts = {}
    getSessionSearches().forEach((item) => {
      counts[item.q] = (counts[item.q] || 0) + 1
    })
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8)
  }, [])

  const donut = [
    { name: 'In stock', value: summary.available, color: '#1b6b57' },
    { name: 'Low stock', value: summary.low, color: '#b7791f' },
    { name: 'Out of stock', value: summary.out, color: '#b42318' },
  ]

  const alwaysOpen = pharmacies.filter((p) => p.is_24_7).length
  const availableShare = summary.total ? Math.round((summary.available / summary.total) * 100) : 0

  return (
    <div className="page">
      <PageHeader
        eyebrow="Analytics"
        title="Network insights"
        description="Metrics are derived from live catalog, pharmacy, inventory, and this session’s search activity. ML scores appear on the Intelligence and Risk pages."
      />
      <ErrorBanner error={error} onRetry={reload} />

      <div className="grid grid-4" style={{ marginBottom: 16 }}>
        <div className="card"><h3>{formatNumber(medicines.length)}</h3><p className="sub">Catalog medicines loaded</p></div>
        <div className="card"><h3>{availableShare}%</h3><p className="sub">Inventory rows in stock</p></div>
        <div className="card"><h3>{formatNumber(alwaysOpen)}</h3><p className="sub">24/7 pharmacies</p></div>
        <div className="card"><h3>{formatNumber(summary.uniqueAtRiskMedicines)}</h3><p className="sub">SKUs at or below safety</p></div>
      </div>

      <div className="grid grid-2" style={{ marginBottom: 18 }}>
        <div className="card">
          <h3>Medicine analytics</h3>
          <p className="sub">Category mix and session search volume.</p>
          <div style={{ height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={categoryData.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-20} height={65} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#0f5c5c" radius={[6, 6, 0, 0]} name="Medicines" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {searches.length > 0 ? (
            <div className="chips" style={{ marginTop: 12 }}>
              {searches.map((s) => (
                <span key={s.name} className="status-badge">
                  {s.name} ({s.value})
                </span>
              ))}
            </div>
          ) : (
            <p className="sub">Most-searched terms appear here after you run catalog searches in this session.</p>
          )}
        </div>
        <div className="card">
          <h3>Pharmacy analytics</h3>
          <p className="sub">Coverage by state from the pharmacy directory.</p>
          <div style={{ height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={stateData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1d5f8a" radius={[0, 6, 6, 0]} name="Pharmacies" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>Inventory analytics</h3>
          <p className="sub">Stock distribution across sampled inventory rows.</p>
          <div style={{ height: 240 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={donut} dataKey="value" nameKey="name" innerRadius={60} outerRadius={88} paddingAngle={3}>
                  {donut.map((d) => (
                    <Cell key={d.name} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h3>ML analytics</h3>
          <p className="sub">
            Demand and stock-out scores are pair-specific. This page does not invent network-wide model averages.
          </p>
          <p>
            Use <strong>AI / ML Intelligence</strong> to forecast a pharmacy-medicine pair, and <strong>Stock-out Risk</strong> to score the lowest-stock inventory rows.
          </p>
        </div>
      </div>
    </div>
  )
}
