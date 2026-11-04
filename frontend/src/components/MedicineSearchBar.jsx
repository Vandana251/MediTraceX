import { useEffect, useRef, useState } from 'react'
import { Search } from 'lucide-react'
import { medicinesApi } from '../services/api'
import { matchLabel } from '../utils/format'

export function useDebounce(value, delay = 280) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return debounced
}

export function MedicineSearchBar({
  placeholder = 'Search medicines by name, brand, or molecule',
  onSelect,
  onSubmit,
  compact = false,
}) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const debounced = useDebounce(query)
  const boxRef = useRef(null)

  useEffect(() => {
    const onClick = (event) => {
      if (boxRef.current && !boxRef.current.contains(event.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    async function run() {
      if (!debounced.trim()) {
        setResults([])
        return
      }
      setLoading(true)
      try {
        const data = await medicinesApi.search(debounced.trim(), 8, controller.signal)
        setResults(Array.isArray(data) ? data : [])
        setOpen(true)
      } catch (error) {
        if (error.name !== 'AbortError') setResults([])
      } finally {
        setLoading(false)
      }
    }
    run()
    return () => controller.abort()
  }, [debounced])

  function submit(event) {
    event.preventDefault()
    setOpen(false)
    onSubmit?.(query.trim())
  }

  return (
    <form className="search-wrap" onSubmit={submit} ref={boxRef}>
      <Search className="search-icon" size={18} />
      <input
        className="input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length && setOpen(true)}
        placeholder={placeholder}
        aria-label="Medicine search"
        style={compact ? { height: 40 } : undefined}
      />
      {open && (results.length > 0 || loading) ? (
        <div className="suggest">
          {loading ? <div className="dropdown-item">Searching catalog…</div> : null}
          {results.map((item) => (
            <button
              type="button"
              key={item.id}
              onClick={() => {
                setQuery(item.name)
                setOpen(false)
                onSelect?.(item)
              }}
            >
              <span>
                <strong>{item.name}</strong>
                <br />
                <small style={{ color: 'var(--muted)' }}>
                  {item.generic_name} · {item.brand_name}
                </small>
              </span>
              <span className={`badge ${item.edit_distance > 0 ? 'fuzzy' : 'info'}`}>
                {matchLabel(item.match_type, item.edit_distance)}
              </span>
            </button>
          ))}
        </div>
      ) : null}
    </form>
  )
}
