import { useMemo, useState } from 'react'
import { predictionsApi, mapLimited } from '../services/api'
import { usePlatformData } from '../hooks/usePlatformData'
import { ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { riskTone } from '../utils/format'

export default function RiskPage() {
  const { pharmacies, inventory, loading } = usePlatformData()
  const [pharmacyId, setPharmacyId] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [category, setCategory] = useState('')
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const candidates = useMemo(() => {
    const pool = inventory.filter((item) => {
      const pharmacyOk = !pharmacyId || String(item.pharmacy_id) === String(pharmacyId)
      const categoryOk = !category || String(item.generic_name || item.medicine_name || '').toLowerCase().includes(category.toLowerCase())
      return pharmacyOk && categoryOk
    })
    const priority = [...pool].sort((a, b) => Number(a.stock_quantity) - Number(b.stock_quantity))
    return priority.slice(0, 12)
  }, [inventory, pharmacyId, category])

  async function assess() {
    if (!candidates.length) {
      setError('No inventory rows match the current filters.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const results = await mapLimited(
        candidates,
        async (item) => {
          try {
            const prediction = await predictionsApi.get(item.pharmacy_id, item.medicine_id, 7)
            return { item, prediction, error: null }
          } catch (err) {
            return { item, prediction: null, error: err.message }
          }
        },
        3
      )
      setRows(results)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const visible = rows.filter((row) => {
    if (!riskFilter) return true
    return String(row.prediction?.stock_out_risk || '').toUpperCase() === riskFilter
  })
  const highCount = rows.filter((row) => row.prediction?.stock_out_risk === 'HIGH').length

  return (
    <div className="page">
      <PageHeader
        eyebrow="Risk monitoring"
        title="Stock-out risk board"
        description="Risk levels are requested from the demand prediction API for a bounded set of real pharmacy-medicine pairs (prioritizing low inventory)."
      />
      {highCount > 0 ? (
        <div className="alert danger" style={{ marginBottom: 16 }}>
          {highCount} assessed pairs currently return HIGH stock-out risk.
        </div>
      ) : null}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="filter-bar">
          <div className="field">
            <label className="label">Pharmacy</label>
            <select className="select" value={pharmacyId} onChange={(e) => setPharmacyId(e.target.value)} disabled={loading}>
              <option value="">All pharmacies</option>
              {pharmacies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Medicine / molecule filter</label>
            <input className="input" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Optional name filter" />
          </div>
          <div className="field">
            <label className="label">Risk level</label>
            <select className="select" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
              <option value="">All assessed</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
        </div>
        <button className="btn btn-primary" type="button" onClick={assess} disabled={busy || loading}>
          {busy ? 'Scoring pairs…' : `Assess ${candidates.length} inventory pairs`}
        </button>
      </div>
      <ErrorBanner error={error} />
      <div className="card">
        <div className="table-wrap">
          <table className="data">
            <thead>
              <tr>
                <th>Pharmacy</th>
                <th>Medicine</th>
                <th>Current stock</th>
                <th>Risk</th>
                <th>Next-day demand</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => (
                <tr key={`${row.item.pharmacy_id}-${row.item.medicine_id}`}>
                  <td>{row.item.pharmacy_name}</td>
                  <td>{row.item.medicine_name}</td>
                  <td>{row.prediction?.current_stock ?? row.item.stock_quantity}</td>
                  <td>
                    {row.prediction ? (
                      <StatusBadge tone={riskTone(row.prediction.stock_out_risk)}>
                        {row.prediction.stock_out_risk}
                      </StatusBadge>
                    ) : (
                      <span className="sub">{row.error || 'Unavailable'}</span>
                    )}
                  </td>
                  <td>{row.prediction?.predicted_next_day_demand ?? '—'}</td>
                  <td>{row.prediction?.risk_reason ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 ? <p className="sub">Run an assessment to load live risk labels.</p> : null}
      </div>
    </div>
  )
}
