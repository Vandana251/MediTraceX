import { API_BASE_URL, TOKEN_STORAGE_KEY } from '../config'

export class ApiError extends Error {
  constructor(message, { status, details, path } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status ?? 0
    this.details = details
    this.path = path
  }
}

function getStoredToken() {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

function parseDetail(payload) {
  if (!payload) return 'Something went wrong. Please try again.'
  if (typeof payload === 'string') return payload
  if (typeof payload.detail === 'string') return payload.detail
  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((item) => item.msg || item.message || JSON.stringify(item))
      .join(' · ')
  }
  if (payload.message) return payload.message
  return 'Request failed. Please try again.'
}

function friendlyStatusMessage(status, isAuthProtected = false) {
  if (status === 401 && isAuthProtected) return 'Your session has expired. Please sign in again.'
  if (status === 403) return 'You do not have permission to perform this action.'
  if (status === 404) return 'The requested record was not found.'
  if (status === 409) return 'This record already exists.'
  if (status === 422) return 'Some fields could not be validated. Please review and try again.'
  if (status >= 500) return 'The server is temporarily unavailable. Please try again shortly.'
  return null
}

async function request(path, { method = 'GET', body, query, auth = false, signal } = {}) {
  const url = new URL(path.startsWith('http') ? path : `${API_BASE_URL}${path}`)
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.set(key, String(value))
      }
    })
  }

  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getStoredToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  let response
  try {
    response = await fetch(url.toString(), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal,
    })
  } catch (error) {
    if (error?.name === 'AbortError') throw error
    throw new ApiError(
      'Unable to reach MediTraceX services. Check your connection and try again.',
      { status: 0, path }
    )
  }

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => null)
    : await response.text().catch(() => null)

  if (!response.ok) {
    const detailMsg = parseDetail(payload)
    const isGeneric = !detailMsg || detailMsg === 'Request failed. Please try again.' || detailMsg === 'Something went wrong. Please try again.'
    const message = (!isGeneric && detailMsg)
      ? detailMsg
      : (friendlyStatusMessage(response.status, auth) || detailMsg || 'Request failed.')
    if (response.status === 401 && auth) {
      window.dispatchEvent(new CustomEvent('mtx:unauthorized'))
    }
    throw new ApiError(message, { status: response.status, details: payload, path })
  }

  return payload
}

export const healthApi = {
  root: () => request('/'),
  health: () => request('/health'),
}

export const authApi = {
  register: (payload) => request('/api/auth/register', { method: 'POST', body: payload }),
  login: ({ email, identifier, password }) =>
    request('/api/auth/login', {
      method: 'POST',
      body: {
        password,
        email: email || identifier,
        identifier: identifier || email,
      },
    }),
  me: () => request('/api/auth/me', { auth: true }),
  forgotPassword: (payload) => request('/api/auth/forgot-password', { method: 'POST', body: payload }),
  resetPassword: (payload) => request('/api/auth/reset-password', { method: 'POST', body: payload }),
}

export const medicinesApi = {
  search: (q, limit = 12, signal) =>
    request('/api/medicines/search', { query: { q, limit }, signal }),
  getById: (medicineId) => request(`/api/medicines/${medicineId}`),
  list: ({ page = 1, pageSize = 20, category } = {}) =>
    request('/api/medicines', { query: { page, page_size: pageSize, category } }),
}

export const pharmaciesApi = {
  list: () => request('/api/pharmacies'),
  getById: (pharmacyId) => request(`/api/pharmacies/${pharmacyId}`),
  nearby: ({ latitude, longitude, medicineId, radiusKm = 20, limit = 10 }) =>
    request('/api/pharmacies/nearby', {
      query: {
        latitude,
        longitude,
        medicine_id: medicineId,
        radius_km: radiusKm,
        limit,
      },
    }),
  externalNearby: ({ latitude, longitude, radiusKm = 5, limit = 25, signal }) =>
    request('/api/pharmacies/external-nearby', {
      query: {
        latitude,
        longitude,
        radius_km: radiusKm,
        limit,
      },
      signal,
    }),
}

export const inventoryApi = {
  byPharmacy: (pharmacyId) => request(`/api/inventory/pharmacy/${pharmacyId}`),
  byMedicine: (medicineId) => request(`/api/inventory/medicine/${medicineId}`),
  pair: (pharmacyId, medicineId) =>
    request(`/api/inventory/${pharmacyId}/${medicineId}`),
  update: (inventoryId, payload) =>
    request(`/api/inventory/${inventoryId}`, { method: 'PUT', body: payload, auth: true }),
}

export const predictionsApi = {
  get: (pharmacyId, medicineId, forecastDays = 7) =>
    request(`/api/predictions/${pharmacyId}/${medicineId}`, {
      query: { forecast_days: forecastDays },
    }),
}

export const requestsApi = {
  create: (payload) => request('/api/requests', { method: 'POST', body: payload, auth: true }),
  my: () => request('/api/requests/my', { auth: true }),
  pharmacy: () => request('/api/requests/pharmacy', { auth: true }),
  getById: (requestId) => request(`/api/requests/${requestId}`, { auth: true }),
  updateStatus: (requestId, status) =>
    request(`/api/requests/${requestId}/status`, {
      method: 'PUT',
      body: { status },
      auth: true,
    }),
}

export const watchlistApi = {
  list: () => request('/api/watchlist', { auth: true }),
  add: (payload) => request('/api/watchlist', { method: 'POST', body: payload, auth: true }),
  remove: (watchlistId) =>
    request(`/api/watchlist/${watchlistId}`, { method: 'DELETE', auth: true }),
}

export const locationsApi = {
  search: (q, limit = 8, signal) =>
    request('/api/locations/search', { query: { q, limit }, signal }),
}

export async function mapLimited(items, mapper, concurrency = 4) {
  const results = new Array(items.length)
  let index = 0

  async function worker() {
    while (index < items.length) {
      const current = index
      index += 1
      results[current] = await mapper(items[current], current)
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker))
  return results
}
