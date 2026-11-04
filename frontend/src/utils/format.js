export function formatInr(value) {
  const amount = Number(value)
  if (Number.isNaN(amount)) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatNumber(value) {
  const amount = Number(value)
  if (Number.isNaN(amount)) return '—'
  return new Intl.NumberFormat('en-IN').format(amount)
}

export function formatKm(value) {
  const amount = Number(value)
  if (Number.isNaN(amount)) return '—'
  return `${amount.toFixed(2)} km`
}

export function calculateDistanceKm(lat1, lon1, lat2, lon2) {
  if (lat1 == null || lon1 == null || lat2 == null || lon2 == null) return null
  const R = 6371 // Earth radius in km
  const dLat = ((Number(lat2) - Number(lat1)) * Math.PI) / 180
  const dLon = ((Number(lon2) - Number(lon1)) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((Number(lat1) * Math.PI) / 180) *
      Math.cos((Number(lat2) * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

export function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(date)
}

export function stockTone(status) {
  const normalized = String(status || '').toLowerCase()
  if (normalized.includes('out')) return 'danger'
  if (normalized.includes('low')) return 'warning'
  if (normalized.includes('in stock') || normalized.includes('available')) return 'success'
  return 'neutral'
}

export function riskTone(level) {
  const normalized = String(level || '').toUpperCase()
  if (normalized === 'HIGH') return 'danger'
  if (normalized === 'MEDIUM') return 'warning'
  if (normalized === 'LOW') return 'success'
  return 'neutral'
}

export function matchLabel(matchType, editDistance) {
  if (Number(editDistance) > 0 || matchType === 'fuzzy') return 'Typo recovery'
  if (matchType === 'exact') return 'Exact match'
  if (matchType === 'prefix') return 'Prefix match'
  return matchType || 'Match'
}

export function requestStage(status) {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'PENDING') return { label: 'Pending', step: 1, tone: 'warning' }
  if (normalized === 'ACCEPTED') return { label: 'Approved', step: 2, tone: 'info' }
  if (normalized === 'FULFILLED') return { label: 'Fulfilled', step: 3, tone: 'success' }
  if (normalized === 'CANCELLED') return { label: 'Cancelled', step: 3, tone: 'neutral' }
  if (normalized === 'NOT_AVAILABLE') return { label: 'Not available', step: 3, tone: 'danger' }
  return { label: status || 'Requested', step: 0, tone: 'neutral' }
}

export function initials(name) {
  return String(name || 'U')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('')
}

export function uniqueBy(items, keyFn) {
  const seen = new Set()
  const result = []
  for (const item of items) {
    const key = keyFn(item)
    if (seen.has(key)) continue
    seen.add(key)
    result.push(item)
  }
  return result
}
