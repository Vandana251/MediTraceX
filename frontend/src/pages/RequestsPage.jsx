import { useEffect, useState } from 'react'
import { requestsApi, medicinesApi, pharmaciesApi } from '../services/api'
import { REQUEST_STATUSES } from '../config'
import { useAuth } from '../context/AuthContext'
import { RequireAuth } from '../components/AppShell'
import { EmptyState, ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { formatDateTime, requestStage } from '../utils/format'

function Timeline({ status }) {
  const current = requestStage(status)
  const steps = [
    { key: 'REQUESTED', label: 'Requested' },
    { key: 'PENDING', label: 'Pending' },
    { key: 'ACCEPTED', label: 'Approved' },
    { key: 'CLOSED', label: 'Fulfilled / Rejected' },
  ]
  const index = status === 'PENDING' ? 1 : status === 'ACCEPTED' ? 2 : ['FULFILLED', 'CANCELLED', 'NOT_AVAILABLE'].includes(status) ? 3 : 0
  return (
    <div className="timeline">
      {steps.map((step, i) => (
        <div key={step.key} className={`tl-step ${i < index ? 'done' : ''} ${i === index ? 'current' : ''}`}>
          <span className="tl-dot" />
          {step.label}
          {i < steps.length - 1 ? <span className="tl-line" /> : null}
        </div>
      ))}
      <StatusBadge tone={current.tone}>{current.label}</StatusBadge>
    </div>
  )
}

function RequestsInner() {
  const { isPharmacyStaff } = useAuth()
  const [mine, setMine] = useState([])
  const [incoming, setIncoming] = useState([])
  const [error, setError] = useState(null)
  const [medicines, setMedicines] = useState([])
  const [pharmacies, setPharmacies] = useState([])
  const [form, setForm] = useState({ medicine_id: '', pharmacy_id: '', quantity_requested: 1, notes: '' })
  const [busy, setBusy] = useState(false)

  async function load() {
    setError(null)
    try {
      const [myRows, meds, pharms] = await Promise.all([
        requestsApi.my(),
        medicinesApi.list({ page: 1, pageSize: 100 }),
        pharmaciesApi.list(),
      ])
      setMine(Array.isArray(myRows) ? myRows : [])
      setMedicines(meds?.items || [])
      setPharmacies(Array.isArray(pharms) ? pharms : [])
      if (isPharmacyStaff) {
        const rows = await requestsApi.pharmacy()
        setIncoming(Array.isArray(rows) ? rows : [])
      }
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
  }, [isPharmacyStaff])

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await requestsApi.create({
        medicine_id: Number(form.medicine_id),
        pharmacy_id: form.pharmacy_id ? Number(form.pharmacy_id) : null,
        quantity_requested: Number(form.quantity_requested),
        notes: form.notes || null,
      })
      setForm({ medicine_id: '', pharmacy_id: '', quantity_requested: 1, notes: '' })
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function updateStatus(id, status) {
    try {
      await requestsApi.updateStatus(id, status)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const rows = isPharmacyStaff ? incoming : mine

  return (
    <div className="page">
      <PageHeader
        eyebrow="Medicine requests"
        title="Request lifecycle"
        description="Statuses come from the API: PENDING, ACCEPTED, FULFILLED, CANCELLED, and NOT_AVAILABLE."
      />
      <ErrorBanner error={error} onRetry={load} />
      <form className="card" onSubmit={submit} style={{ marginBottom: 16 }}>
        <h3>New request</h3>
        <div className="filter-bar">
          <div className="field">
            <label className="label">Medicine</label>
            <select className="select" required value={form.medicine_id} onChange={(e) => setForm((f) => ({ ...f, medicine_id: e.target.value }))}>
              <option value="">Select</option>
              {medicines.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Pharmacy (optional)</label>
            <select className="select" value={form.pharmacy_id} onChange={(e) => setForm((f) => ({ ...f, pharmacy_id: e.target.value }))}>
              <option value="">Broadcast</option>
              {pharmacies.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label">Quantity</label>
            <input className="input" type="number" min="1" value={form.quantity_requested} onChange={(e) => setForm((f) => ({ ...f, quantity_requested: e.target.value }))} />
          </div>
        </div>
        <label className="label">Notes</label>
        <textarea className="textarea" value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
        <div style={{ marginTop: 12 }}>
          <button className="btn btn-primary" disabled={busy} type="submit">Submit request</button>
        </div>
      </form>
      <div className="card">
        {rows.map((req) => (
          <div key={req.id} style={{ padding: '14px 0', borderBottom: '1px solid var(--line)' }}>
            <strong>{req.medicine_name}</strong>
            <p className="sub">
              Qty {req.quantity_requested} · {req.pharmacy_name || 'Any pharmacy'} · {formatDateTime(req.created_at)}
            </p>
            <Timeline status={req.status} />
            {isPharmacyStaff ? (
              <div className="chips" style={{ marginTop: 10 }}>
                {REQUEST_STATUSES.map((status) => (
                  <button key={status} className="btn btn-ghost" type="button" onClick={() => updateStatus(req.id, status)}>
                    {status}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        ))}
        {rows.length === 0 ? (
          <EmptyState title="No requests yet" description="Submit a request above to start the PENDING → APPROVED → FULFILLED lifecycle." />
        ) : null}
      </div>
    </div>
  )
}

export default function RequestsPage() {
  return (
    <RequireAuth>
      <RequestsInner />
    </RequireAuth>
  )
}
