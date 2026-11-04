import { useEffect, useMemo, useState } from 'react'
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
import { ErrorBanner, PageHeader, SkeletonGrid, StatusBadge } from '../components/ui'
import { formatDate, formatNumber, stockTone } from '../utils/format'

export default function InventoryPage() {
  const { loading, error, pharmacies, inventory, summary, reload } = usePlatformData()
  const [pharmacyId, setPharmacyId] = useState('')
  const [medicineQuery, setMedicineQuery] = useState('')

  useEffect(() => {
    if (!pharmacyId && pharmacies[0]) setPharmacyId(String(pharmacies[0].id))
  }, [pharmacies, pharmacyId])

  const filtered = useMemo(() => {
    return inventory.filter((item) => {
      const pharmacyOk = !pharmacyId || String(item.pharmacy_id) === String(pharmacyId)
      const query = medicineQuery.trim().toLowerCase()
      const medicineOk =
        !query ||
        String(item.medicine_name || '').toLowerCase().includes(query) ||
        String(item.generic_name || '').toLowerCase().includes(query)
      return pharmacyOk && medicineOk
    })
  }, [inventory, pharmacyId, medicineQuery])

  const pharmacyBars = useMemo(() => {
    const map = new Map()
    inventory.forEach((item) => {
      const key = item.pharmacy_name || `Pharmacy ${item.pharmacy_id}`
      const current = map.get(key) || { name: key, units: 0, low: 0, out: 0 }
      current.units += Number(item.stock_quantity || 0)
      if (/low/i.test(item.stock_status)) current.low += 1
      if (/out/i.test(item.stock_status)) current.out += 1
      map.set(key, current)
    })
    return [...map.values()].sort((a, b) => b.units - a.units).slice(0, 8)
  }, [inventory])

  const donut = [
    { name: 'In stock', value: summary.available, color: '#1b6b57' },
    { name: 'Low stock', value: summary.low, color: '#b7791f' },
    { name: 'Out of stock', value: summary.out, color: '#b42318' },
  ]

  return (
    <div className="page">
      <PageHeader
        eyebrow="Inventory intelligence"
        title="Stock across the pharmacy network"
        description="Every chart and table on this page is aggregated from live pharmacy inventory APIs."
      />
      <ErrorBanner error={error} onRetry={reload} />
      {loading ? <SkeletonGrid count={4} /> : (
        <div className="grid grid-4" style={{ marginBottom: 16 }}>
          <div className="card"><h3>{formatNumber(summary.total)}</h3><p className="sub">Inventory records</p></div>
          <div className="card"><h3>{formatNumber(summary.units)}</h3><p className="sub">Units on hand</p></div>
          <div className="card"><h3>{formatNumber(summary.low)}</h3><p className="sub">Low stock rows</p></div>
          <div className="card"><h3>{formatNumber(summary.out)}</h3><p className="sub">Out of stock rows</p></div>
        </div>
      )}

      <div className="grid grid-2" style={{ marginBottom: 16 }}>
        <div className="card">
          <h3>Stock-level distribution</h3>
          <div style={{ height: 260 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={donut} dataKey="value" nameKey="name" innerRadius={62} outerRadius={90}>
                  {donut.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h3>Pharmacy comparison</h3>
          <p className="sub">Units on hand for the highest-volume pharmacies.</p>
          <div style={{ height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={pharmacyBars} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="units" fill="#0f5c5c" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="filter-bar">
          <div className="field">
            <label className="label">Pharmacy</label>
            <select className="select" value={pharmacyId} onChange={(e) => setPharmacyId(e.target.value)}>
              <option value="">All pharmacies</option>
              {pharmacies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Medicine</label>
            <input className="input" value={medicineQuery} onChange={(e) => setMedicineQuery(e.target.value)} placeholder="Filter by medicine name" />
          </div>
        </div>
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Pharmacy</th>
                <th>Medicine</th>
                <th>Qty</th>
                <th>Safety</th>
                <th>Status</th>
                <th>Batch</th>
                <th>Expiry</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 80).map((item) => (
                <tr key={item.id}>
                  <td>{item.pharmacy_name}</td>
                  <td>
                    <strong>{item.medicine_name}</strong>
                    <div className="sub" style={{ margin: 0 }}>{item.generic_name}</div>
                  </td>
                  <td>{item.stock_quantity}</td>
                  <td>{item.safety_stock_threshold}</td>
                  <td><StatusBadge tone={stockTone(item.stock_status)}>{item.stock_status}</StatusBadge></td>
                  <td>{item.batch_number}</td>
                  <td>{formatDate(item.expiry_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
