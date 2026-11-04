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

export default function AnalyticsPage() {
  const { medicines, pharmacies, inventory, summary, error, reload } = usePlatformData()

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

  const cityData = useMemo(() => {
    const map = {}
    pharmacies.forEach((p) => {
      map[p.city] = (map[p.city] || 0) + 1
    })
    return Object.entries(map)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
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

  return (
    <div className="page">
      <PageHeader
        eyebrow="Pan-India Analytics"
        title="National Healthcare Network Insights"
        description="Comprehensive geographic distribution, state coverage, therapeutic category metrics, and inventory health across India."
      />
      <ErrorBanner error={error} onRetry={reload} />

      <div className="grid grid-2" style={{ marginBottom: 18 }}>
        {/* State-wise Coverage */}
        <div className="card">
          <h3>State-Wise Pharmacy Distribution</h3>
          <p className="sub">
            Distribution across {stateData.length} Indian states & regions ({pharmacies.length} total branches).
          </p>
          <div style={{ height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={stateData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0f5c5c" radius={[0, 6, 6, 0]} name="Pharmacies" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Cities Coverage */}
        <div className="card">
          <h3>Top 10 Cities by Pharmacy Coverage</h3>
          <p className="sub">
            Metropolitan hubs with highest pharmacy discovery density.
          </p>
          <div style={{ height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={cityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-25} height={60} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1d5f8a" radius={[6, 6, 0, 0]} name="Pharmacies" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        {/* Therapeutic Categories */}
        <div className="card">
          <h3>Therapeutic Categories</h3>
          <p className="sub">
            {medicines.length} indexed medicines categorized by pharmacological classification.
          </p>
          <div style={{ height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={categoryData.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-20} height={65} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#b7791f" radius={[6, 6, 0, 0]} name="Medicines" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Inventory Stock Health */}
        <div className="card">
          <h3>Network Stock Health Ratio</h3>
          <p className="sub">
            Sampled inventory breakdown across available, low, and out of stock SKUs.
          </p>
          <div style={{ height: 240 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={donut} dataKey="value" nameKey="name" innerRadius={60} outerRadius={88} paddingAngle={3}>
                  {donut.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {searches.length > 0 && (
            <div style={{ marginTop: 12, borderTop: '1px solid var(--line)', paddingTop: 10 }}>
              <strong style={{ fontSize: '0.85rem' }}>Popular Searches (Session):</strong>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 6 }}>
                {searches.map((s) => (
                  <span key={s.name} className="status-badge status-neutral" style={{ fontSize: '0.75rem' }}>
                    {s.name} ({s.value})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
