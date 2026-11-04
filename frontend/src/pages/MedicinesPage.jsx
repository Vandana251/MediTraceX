import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { medicinesApi } from '../services/api'
import { formatInr, matchLabel } from '../utils/format'
import { EmptyState, ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { MedicineSearchBar } from '../components/MedicineSearchBar'
import { recordSearch } from '../utils/sessionSearch'

export default function MedicinesPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const query = params.get('q') || ''
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [catalog, setCatalog] = useState({ items: [], total: 0, page: 1 })
  const [category, setCategory] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadCatalog() {
      try {
        const data = await medicinesApi.list({ page: 1, pageSize: 20, category: category || undefined })
        if (!cancelled) setCatalog(data)
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }
    loadCatalog()
    return () => {
      cancelled = true
    }
  }, [category])

  useEffect(() => {
    const controller = new AbortController()
    async function search() {
      if (!query) {
        setResults([])
        return
      }
      setLoading(true)
      setError(null)
      try {
        const data = await medicinesApi.search(query, 20, controller.signal)
        recordSearch(query)
        setResults(Array.isArray(data) ? data : [])
      } catch (err) {
        if (err.name !== 'AbortError') setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    search()
    return () => controller.abort()
  }, [query])

  const suggestion = useMemo(() => {
    if (!results.length) return null
    const fuzzy = results.find((item) => Number(item.edit_distance) > 0)
    return fuzzy ? fuzzy.name : null
  }, [results])

  const rows = query ? results : catalog.items || []

  return (
    <div className="page">
      <PageHeader
        eyebrow="DSA search engine"
        title="Medicine intelligence"
        description="Prefix trie search across names, brands, and generic molecules, with Levenshtein recovery when the query is misspelled."
      />
      <div className="card" style={{ marginBottom: 16 }}>
        <MedicineSearchBar
          onSelect={(item) => navigate(`/medicines/${item.id}`)}
          onSubmit={(q) => setParams(q ? { q } : {})}
        />
        {query && suggestion ? (
          <div className="alert warning" style={{ marginTop: 14 }}>
            Did you mean <strong>{suggestion}</strong>? Showing typo-tolerant matches for “{query}”.
          </div>
        ) : null}
      </div>
      <ErrorBanner error={error} />
      <div className="card">
        <div className="filter-bar">
          <div className="field">
            <label className="label">Therapeutic category</label>
            <input
              className="input"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Filter catalog, e.g. Antibiotic"
              disabled={Boolean(query)}
            />
          </div>
        </div>
        {loading ? <p className="sub">Searching the trie index…</p> : null}
        {!loading && rows.length === 0 ? (
          <EmptyState title="No medicines found" description="Try a shorter prefix or a nearby spelling." />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Medicine</th>
                  <th>Generic</th>
                  <th>Brand</th>
                  <th>Dosage</th>
                  <th>Form</th>
                  <th>Category</th>
                  <th>Price</th>
                  {query ? <th>Match</th> : null}
                </tr>
              </thead>
              <tbody>
                {rows.map((item) => (
                  <tr className="row-link" key={item.id} onClick={() => navigate(`/medicines/${item.id}`)}>
                    <td>
                      <strong>{item.name}</strong>
                    </td>
                    <td>{item.generic_name}</td>
                    <td>{item.brand_name}</td>
                    <td>{item.dosage}</td>
                    <td>{item.dosage_form}</td>
                    <td>{item.category}</td>
                    <td>{formatInr(item.unit_price)}</td>
                    {query ? (
                      <td>
                        <StatusBadge tone={item.edit_distance > 0 ? 'warning' : 'info'}>
                          {matchLabel(item.match_type, item.edit_distance)}
                          {item.edit_distance > 0 ? ` · d=${item.edit_distance}` : ''}
                        </StatusBadge>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!query ? <p className="sub" style={{ marginTop: 12 }}>Showing page 1 of {catalog.total || 0} catalog records.</p> : null}
      </div>
    </div>
  )
}
