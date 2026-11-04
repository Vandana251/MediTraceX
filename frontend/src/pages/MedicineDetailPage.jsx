import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Bell, ClipboardList, MapPin, ShieldCheck } from 'lucide-react'
import { inventoryApi, medicinesApi, pharmaciesApi, predictionsApi, requestsApi, watchlistApi } from '../services/api'
import { DEFAULT_LOCATION, DEFAULT_RADIUS_KM, INDIAN_CITIES } from '../config'
import { formatInr, formatKm, formatNumber, riskTone, stockTone } from '../utils/format'
import { ErrorBanner, PageHeader, Spinner, StatusBadge } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function MedicineDetailPage() {
  const { medicineId } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [medicine, setMedicine] = useState(null)
  const [inventory, setInventory] = useState([])
  const [nearby, setNearby] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [selectedCity, setSelectedCity] = useState('Hyderabad')
  const [coords, setCoords] = useState(
    INDIAN_CITIES.find((c) => c.name === 'Hyderabad') || DEFAULT_LOCATION
  )
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [note, setNote] = useState('')

  async function loadLocationRanking(lat, lon, cityLabel) {
    try {
      const ranked = await pharmaciesApi.nearby({
        latitude: lat,
        longitude: lon,
        medicineId,
        radiusKm: 75,
        limit: 10,
      })
      setNearby(ranked)
      const first = ranked?.ranked_pharmacies?.[0]
      if (first) {
        const forecast = await predictionsApi.get(first.pharmacy_id, medicineId, 7)
        setPrediction(forecast)
      } else {
        setPrediction(null)
      }
    } catch (err) {
      setError(err.message)
    }
  }

  function handleCityChange(cityName) {
    setSelectedCity(cityName)
    const cityMeta = INDIAN_CITIES.find((c) => c.name === cityName)
    if (cityMeta) {
      setCoords(cityMeta)
      loadLocationRanking(cityMeta.latitude, cityMeta.longitude, `${cityMeta.name}, ${cityMeta.state}`)
    }
  }

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      setPrediction(null)
      try {
        const [med, inv] = await Promise.all([
          medicinesApi.getById(medicineId),
          inventoryApi.byMedicine(medicineId),
        ])
        if (cancelled) return
        setMedicine(med)
        setInventory(Array.isArray(inv) ? inv : [])

        const initialCity = INDIAN_CITIES.find((c) => c.name === 'Hyderabad') || DEFAULT_LOCATION
        const ranked = await pharmaciesApi.nearby({
          latitude: initialCity.latitude,
          longitude: initialCity.longitude,
          medicineId,
          radiusKm: 75,
          limit: 10,
        })
        if (cancelled) return
        setNearby(ranked)
        const first = ranked?.ranked_pharmacies?.[0]
        if (first) {
          const forecast = await predictionsApi.get(first.pharmacy_id, medicineId, 7)
          if (!cancelled) setPrediction(forecast)
        }
      } catch (err) {
        if (!cancelled) setError(err.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [medicineId])

  async function notifyMe() {
    setBusy('watch')
    setNote('')
    try {
      await watchlistApi.add({
        medicine_id: Number(medicineId),
        pharmacy_id: nearby?.ranked_pharmacies?.[0]?.pharmacy_id ?? null,
        notify_on_restock: true,
      })
      setNote('You will be notified when this medicine is restocked.')
    } catch (err) {
      setNote(err.message)
    } finally {
      setBusy('')
    }
  }

  async function requestMedicine() {
    setBusy('request')
    setNote('')
    try {
      await requestsApi.create({
        medicine_id: Number(medicineId),
        pharmacy_id: nearby?.ranked_pharmacies?.[0]?.pharmacy_id ?? null,
        quantity_requested: 1,
        notes: `Requested for ${coords.name || 'selected city'}`,
      })
      setNote('Request submitted. Track it on the Requests page.')
    } catch (err) {
      setNote(err.message)
    } finally {
      setBusy('')
    }
  }

  if (loading) {
    return (
      <div className="page">
        <Spinner label="Loading medicine dossier, Pan-India inventory, and nearby ranking…" />
      </div>
    )
  }

  if (!medicine) {
    return (
      <div className="page">
        <ErrorBanner error={error || 'Medicine not found.'} onRetry={() => navigate('/medicines')} />
      </div>
    )
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Medicine Dossier"
        title={medicine.name}
        description={`${medicine.generic_name} · Brand: ${medicine.brand_name} · Manufacturer: ${medicine.manufacturer}`}
        actions={
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn btn-ghost" type="button" onClick={() => navigate('/pharmacies')}>
              <MapPin size={16} /> Pan-India Map
            </button>
            <button className="btn btn-soft" disabled={!isAuthenticated || busy === 'watch'} onClick={notifyMe}>
              <Bell size={16} /> Notify Me
            </button>
            <button className="btn btn-primary" disabled={!isAuthenticated || busy === 'request'} onClick={requestMedicine}>
              <ClipboardList size={16} /> Request Medicine
            </button>
          </div>
        }
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
        <span className="status-badge status-neutral" style={{ background: 'var(--teal-soft)', color: 'var(--teal-deep)', border: '1px solid var(--line-strong)' }}>
          <ShieldCheck size={14} style={{ display: 'inline', marginRight: 4 }} /> Pan-India Inventory Verified
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
          Track availability across 125+ branches in Andhra Pradesh, Telangana, Karnataka, Maharashtra, Delhi NCR, and nationwide.
        </span>
      </div>

      <ErrorBanner error={error} />
      {note ? <div className="alert info" style={{ marginBottom: 16 }}>{note}</div> : null}

      <div className="grid grid-3" style={{ marginBottom: 16 }}>
        <div className="card">
          <h3>Product Specifications</h3>
          <p className="sub">{medicine.category}</p>
          <p><strong>Dosage:</strong> {medicine.dosage} · {medicine.dosage_form}</p>
          <p><strong>Rx Required:</strong> {medicine.is_prescription_required ? 'Prescription Needed' : 'Over the counter (OTC)'}</p>
          <p><strong>Unit MRP:</strong> {formatInr(medicine.unit_price)}</p>
        </div>
        <div className="card">
          <h3>National Stock Health</h3>
          <p className="sub">{inventory.length} total branch records</p>
          <p>🟢 In stock: {inventory.filter((i) => /in stock/i.test(i.stock_status)).length} branches</p>
          <p>🟡 Low stock: {inventory.filter((i) => /low/i.test(i.stock_status)).length} branches</p>
          <p>🔴 Out of stock: {inventory.filter((i) => /out/i.test(i.stock_status)).length} branches</p>
        </div>
        <div className="card">
          <h3>AI Demand Forecasting</h3>
          {prediction ? (
            <>
              <p className="sub">{prediction.pharmacy_name}</p>
              <StatusBadge tone={riskTone(prediction.stock_out_risk)}>{prediction.stock_out_risk} Stock-out Risk</StatusBadge>
              <p style={{ marginTop: 10 }}>Predicted Next-Day Demand: <strong>{prediction.predicted_next_day_demand} units</strong></p>
              <p>Predicted 7-Day Demand: <strong>{prediction.predicted_7_day_demand} units</strong></p>
              <p style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>Suggested Restock: {prediction.suggested_restock_quantity} units</p>
            </>
          ) : (
            <p className="sub">Select a city with available stock to inspect ML demand forecasts.</p>
          )}
        </div>
      </div>

      {/* City Switcher Card */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h4 style={{ margin: '0 0 4px', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: 6 }}>
              <MapPin size={16} color="var(--teal)" /> Select User City for Nearby Availability Ranking
            </h4>
            <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>
              Change city to discover pharmacies stocking {medicine.name} in your region:
            </span>
          </div>
          <div style={{ minWidth: 220 }}>
            <select
              className="select"
              value={selectedCity}
              onChange={(e) => handleCityChange(e.target.value)}
            >
              {INDIAN_CITIES.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} ({c.state})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card" style={{ maxHeight: 520, overflowY: 'auto' }}>
          <h3>Nearby Pharmacies in {coords.name || coords.label}</h3>
          <p className="sub">
            Ranked with Haversine distance and Min-Heap priority queue.
          </p>
          {(nearby?.ranked_pharmacies || []).map((pharmacy) => (
            <div className="rank-card" key={pharmacy.pharmacy_id} style={{ marginBottom: 10 }}>
              <div className="rank-num">{pharmacy.rank}</div>
              <div style={{ flex: 1 }}>
                <strong>{pharmacy.pharmacy_name}</strong>
                <p className="sub" style={{ margin: '3px 0 0' }}>
                  {pharmacy.address}, <strong>{pharmacy.city}</strong> · {pharmacy.contact_phone}
                  <br />
                  {pharmacy.operating_hours} {pharmacy.is_24_7 ? '· 24/7' : ''}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <StatusBadge tone={stockTone(pharmacy.availability_status)}>
                  {pharmacy.availability_status}
                </StatusBadge>
                <div className="sub" style={{ marginTop: 4, fontWeight: 600 }}>
                  {formatKm(pharmacy.distance_km)}
                </div>
                <div className="sub">
                  Stock: {formatNumber(pharmacy.stock_quantity)}
                </div>
              </div>
            </div>
          ))}
          {(nearby?.ranked_pharmacies || []).length === 0 && (
            <p className="sub" style={{ textAlign: 'center', padding: '30px 0' }}>
              No pharmacies within 75 km for {coords.name || coords.label}.
            </p>
          )}
        </div>

        <div className="card">
          <h3>7-Day Trajectory Forecast ({prediction?.pharmacy_name || 'Hub'})</h3>
          <p className="sub">{prediction?.disclaimer || 'Forecast is generated dynamically by ML HistGradientBoostingRegressor.'}</p>
          {prediction ? (
            <div style={{ height: 320 }}>
              <ResponsiveContainer>
                <LineChart data={prediction.daily_forecasts}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#dce6e8" />
                  <XAxis dataKey="day_name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="predicted_demand" stroke="#0f5c5c" strokeWidth={2.5} dot={{ r: 4, fill: '#0f5c5c' }} name="Predicted Demand Units" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: 280, display: 'grid', placeItems: 'center', color: 'var(--muted)' }}>
              Select a city above to view real-time ML demand trajectory.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
