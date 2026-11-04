import { useEffect, useState } from 'react'
import { watchlistApi, medicinesApi, pharmaciesApi, inventoryApi } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { RequireAuth } from '../components/AppShell'
import { EmptyState, ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { formatDateTime, stockTone } from '../utils/format'

function WatchlistInner() {
  const { isAuthenticated } = useAuth()
  const [items, setItems] = useState([])
  const [stockMap, setStockMap] = useState({})
  const [medicines, setMedicines] = useState([])
  const [pharmacies, setPharmacies] = useState([])
  const [form, setForm] = useState({ medicine_id: '', pharmacy_id: '', notify_on_restock: true })
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function load() {
    setError(null)
    try {
      const [list, meds, pharms] = await Promise.all([
        watchlistApi.list(),
        medicinesApi.list({ page: 1, pageSize: 100 }),
        pharmaciesApi.list(),
      ])
      const rows = Array.isArray(list) ? list : []
      setItems(rows)
      setMedicines(meds?.items || [])
      setPharmacies(Array.isArray(pharms) ? pharms : [])
      const nextStock = {}
      await Promise.all(
        rows.map(async (row) => {
          if (!row.pharmacy_id) return
          try {
            const inv = await inventoryApi.pair(row.pharmacy_id, row.medicine_id)
            nextStock[row.id] = inv
          } catch {
            nextStock[row.id] = null
          }
        })
      )
      setStockMap(nextStock)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    if (isAuthenticated) load()
  }, [isAuthenticated])

  async function add(event) {
    event.preventDefault()
    setBusy(true)
    try {
      await watchlistApi.add({
        medicine_id: Number(form.medicine_id),
        pharmacy_id: form.pharmacy_id ? Number(form.pharmacy_id) : null,
        notify_on_restock: Boolean(form.notify_on_restock),
      })
      setForm({ medicine_id: '', pharmacy_id: '', notify_on_restock: true })
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function remove(id) {
    try {
      await watchlistApi.remove(id)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Notify me"
        title="Restock watchlist"
        description="Subscribe to restock events for a medicine, optionally scoped to a pharmacy."
      />
      <ErrorBanner error={error} onRetry={load} />
      <form className="card" onSubmit={add} style={{ marginBottom: 16 }}>
        <h3>Notify me when available</h3>
        <div className="filter-bar">
          <div className="field">
            <label className="label">Medicine</label>
            <select className="select" required value={form.medicine_id} onChange={(e) => setForm((f) => ({ ...f, medicine_id: e.target.value }))}>
              <option value="">Select medicine</option>
              {medicines.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Pharmacy (optional)</label>
            <select className="select" value={form.pharmacy_id} onChange={(e) => setForm((f) => ({ ...f, pharmacy_id: e.target.value }))}>
              <option value="">Any pharmacy</option>
              {pharmacies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        </div>
        <label className="chips" style={{ margin: '8px 0 14px', display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={form.notify_on_restock}
            onChange={(e) => setForm((f) => ({ ...f, notify_on_restock: e.target.checked }))}
          />
          Notify on restock
        </label>
        <button className="btn btn-primary" disabled={busy} type="submit">Add to watchlist</button>
      </form>
      <div className="grid grid-2">
        {items.map((item) => {
          const stock = stockMap[item.id]
          return (
            <div className="card" key={item.id}>
              <h3>{item.medicine_name}</h3>
              <p className="sub">{item.pharmacy_name || 'Network-wide watch'} · added {formatDateTime(item.created_at)}</p>
              <div className="chips">
                <StatusBadge tone={item.is_active ? 'success' : 'neutral'}>
                  {item.is_active ? 'Watching' : 'Inactive'}
                </StatusBadge>
                <StatusBadge tone={item.notify_on_restock ? 'info' : 'neutral'}>
                  {item.notify_on_restock ? 'Notifications on' : 'Notifications off'}
                </StatusBadge>
                {stock ? (
                  <StatusBadge tone={stockTone(stock.stock_status)}>
                    {stock.stock_status} · {stock.stock_quantity}
                  </StatusBadge>
                ) : (
                  <StatusBadge tone="neutral">Stock checked when a pharmacy is set</StatusBadge>
                )}
              </div>
              <div style={{ marginTop: 14 }}>
                <button className="btn btn-ghost" type="button" onClick={() => remove(item.id)}>Remove</button>
              </div>
            </div>
          )
        })}
      </div>
      {items.length === 0 ? (
        <div className="card">
          <EmptyState title="No watchlist items yet" description="Add a medicine to get notified when stock returns." />
        </div>
      ) : null}
    </div>
  )
}

export default function WatchlistPage() {
  return (
    <RequireAuth>
      <WatchlistInner />
    </RequireAuth>
  )
}
