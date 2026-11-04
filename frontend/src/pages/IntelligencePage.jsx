import { useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { predictionsApi } from '../services/api'
import { usePlatformData } from '../hooks/usePlatformData'
import { ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { riskTone } from '../utils/format'

export default function IntelligencePage() {
  const { pharmacies, medicines, loading } = usePlatformData()
  const [pharmacyId, setPharmacyId] = useState('')
  const [medicineId, setMedicineId] = useState('')
  const [horizon, setHorizon] = useState(7)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function runForecast(event) {
    event.preventDefault()
    if (!pharmacyId || !medicineId) {
      setError('Select both a pharmacy and a medicine. The model only scores a real pharmacy-medicine pair.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const data = await predictionsApi.get(pharmacyId, medicineId, horizon)
      setResult(data)
    } catch (err) {
      setResult(null)
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="AI-Powered Demand & Stock-out Intelligence"
        title="Demand forecasting"
        description="Predictions come from GET /api/predictions/{pharmacy_id}/{medicine_id}. No synthetic ML numbers are displayed."
      />
      <form className="card" onSubmit={runForecast} style={{ marginBottom: 16 }}>
        <div className="filter-bar">
          <div className="field">
            <label className="label">Pharmacy</label>
            <select className="select" value={pharmacyId} onChange={(e) => setPharmacyId(e.target.value)} disabled={loading}>
              <option value="">Select pharmacy</option>
              {pharmacies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Medicine</label>
            <select className="select" value={medicineId} onChange={(e) => setMedicineId(e.target.value)} disabled={loading}>
              <option value="">Select medicine</option>
              {medicines.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Forecast horizon (days)</label>
            <input className="input" type="number" min="1" max="14" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} />
          </div>
        </div>
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? 'Running model…' : 'Generate forecast'}
        </button>
      </form>
      <ErrorBanner error={error} />

      {result ? (
        <>
          {String(result.stock_out_risk).toUpperCase() === 'HIGH' ? (
            <div className="alert danger" style={{ marginBottom: 16 }}>
              High stock-out risk for {result.medicine_name} at {result.pharmacy_name}. {result.risk_reason}
            </div>
          ) : null}
          <div className="grid grid-3" style={{ marginBottom: 16 }}>
            <div className="card">
              <h3>Predicted demand</h3>
              <p className="sub">{result.model_used}</p>
              <p>Next day: <strong>{result.predicted_next_day_demand}</strong></p>
              <p>7-day: <strong>{result.predicted_7_day_demand}</strong></p>
            </div>
            <div className="card">
              <h3>Stock-out risk</h3>
              <div className="risk-meter" style={{ marginTop: 12 }}>
                {['LOW', 'MEDIUM', 'HIGH'].map((level) => (
                  <span key={level} className={`${level} ${result.stock_out_risk === level ? 'active' : ''}`}>
                    {level}
                  </span>
                ))}
              </div>
              <p className="sub" style={{ marginTop: 12 }}>{result.risk_reason}</p>
            </div>
            <div className="card">
              <h3>Current position</h3>
              <p>Stock: {result.current_stock}</p>
              <p>Safety threshold: {result.safety_threshold}</p>
              <p>Suggested restock: {result.suggested_restock_quantity}</p>
              <StatusBadge tone={riskTone(result.stock_out_risk)}>{result.stock_out_risk}</StatusBadge>
            </div>
          </div>
          <div className="card">
            <h3>Demand forecast chart</h3>
            <p className="sub">Daily predicted demand returned by the model. Historical sales series is not exposed by this endpoint.</p>
            <div style={{ height: 300 }}>
              <ResponsiveContainer>
                <LineChart data={result.daily_forecasts}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="predicted_demand" name="Forecast demand" stroke="#0f5c5c" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="sub">{result.disclaimer}</p>
          </div>
        </>
      ) : (
        <div className="card">
          <p className="sub">Select a pharmacy and medicine, then run the forecast to inspect live model output.</p>
        </div>
      )}
    </div>
  )
}
