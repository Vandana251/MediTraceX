import { useEffect, useMemo, useRef, useState } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Compass,
  Filter,
  Globe,
  Info,
  Layers,
  Loader2,
  LocateFixed,
  MapPin,
  Navigation,
  Phone,
  Pill,
  Search,
  ShieldCheck,
  Store,
  X,
} from 'lucide-react'
import { locationsApi, medicinesApi, pharmaciesApi } from '../services/api'
import {
  CITY_STATE_MAP,
  DEFAULT_LOCATION,
  DEFAULT_RADIUS_KM,
  getStateForCity,
  INDIAN_CITIES,
} from '../config'
import { calculateDistanceKm, formatKm, formatNumber, stockTone } from '../utils/format'
import { ErrorBanner, PageHeader, StatusBadge } from '../components/ui'
import { MedicineSearchBar } from '../components/MedicineSearchBar'

function MapController({ center, zoom }) {
  const map = useMap()
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, zoom || 13, { animate: true })
    }
  }, [center, zoom, map])
  return null
}

export default function PharmaciesPage() {
  const [pharmacies, setPharmacies] = useState([])
  const [error, setError] = useState(null)
  const [medicine, setMedicine] = useState(null)
  const [nearby, setNearby] = useState(null)
  const [radius, setRadius] = useState(DEFAULT_RADIUS_KM)
  const [selectedCity, setSelectedCity] = useState('All')
  const [selectedState, setSelectedState] = useState('All')
  const [coords, setCoords] = useState(DEFAULT_LOCATION)
  const [zoom, setZoom] = useState(5)
  const [loadingRank, setLoadingRank] = useState(false)

  // Real External Pharmacy Discovery state (Overpass POI)
  const [externalPharmacies, setExternalPharmacies] = useState([])
  const [loadingExternal, setLoadingExternal] = useState(false)
  const [activeTab, setActiveTab] = useState('all') // 'all', 'verified', 'directory'

  // Location Autocomplete state
  const [locationQuery, setLocationQuery] = useState('')
  const [locationSuggestions, setLocationSuggestions] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [activeLocationBadge, setActiveLocationBadge] = useState(null)
  const [detectingGps, setDetectingGps] = useState(false)
  const suggestionBoxRef = useRef(null)

  useEffect(() => {
    pharmaciesApi
      .list()
      .then((data) => setPharmacies(Array.isArray(data) ? data : []))
      .catch((err) => setError(err.message))
  }, [])

  // Fetch real external local pharmacies whenever search coords or radius change
  useEffect(() => {
    if (!coords || !coords.latitude || !coords.longitude) return
    const controller = new AbortController()
    setLoadingExternal(true)

    pharmaciesApi
      .externalNearby({
        latitude: coords.latitude,
        longitude: coords.longitude,
        radiusKm: Math.min(radius, 50),
        limit: 30,
        signal: controller.signal,
      })
      .then((res) => {
        if (res && Array.isArray(res.results)) {
          setExternalPharmacies(res.results)
        } else {
          setExternalPharmacies([])
        }
      })
      .catch((err) => {
        if (err?.name !== 'AbortError') {
          console.warn('External pharmacy discovery error:', err)
          setExternalPharmacies([])
        }
      })
      .finally(() => {
        setLoadingExternal(false)
      })

    return () => controller.abort()
  }, [coords.latitude, coords.longitude, radius])

  // Debounced location search
  useEffect(() => {
    if (!locationQuery || locationQuery.trim().length < 2) {
      setLocationSuggestions([])
      setLoadingSuggestions(false)
      return
    }

    const controller = new AbortController()
    setLoadingSuggestions(true)

    const timer = setTimeout(async () => {
      try {
        const res = await locationsApi.search(locationQuery.trim(), 8, controller.signal)
        if (res?.results) {
          setLocationSuggestions(res.results)
        }
      } catch (err) {
        if (err?.name !== 'AbortError') {
          console.warn('Location search error:', err)
        }
      } finally {
        setLoadingSuggestions(false)
      }
    }, 220)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [locationQuery])

  // Handle outside click for suggestions dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (suggestionBoxRef.current && !suggestionBoxRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const uniqueStates = useMemo(() => {
    const states = new Set(Object.values(CITY_STATE_MAP))
    return ['All', ...Array.from(states).sort()]
  }, [])

  const uniqueCities = useMemo(() => {
    const cities = new Set(pharmacies.map((p) => p.city))
    return ['All', ...Array.from(cities).sort()]
  }, [pharmacies])

  function handleSelectLocation(item) {
    setShowSuggestions(false)
    setLocationQuery(item.display_name)
    setActiveLocationBadge(item)

    const newCoords = {
      latitude: item.latitude,
      longitude: item.longitude,
      label: item.display_name,
      type: item.result_type,
      isInNetwork: item.is_in_network || item.is_verified_network,
      pharmacyId: item.matched_pharmacy_id || item.pharmacy_id,
    }
    setCoords(newCoords)

    // Dynamic zoom based on location resolution
    const type = (item.result_type || '').toLowerCase()
    let targetZoom = 13
    if (type === 'pharmacy') targetZoom = 15
    else if (type === 'locality') targetZoom = 14
    else if (type === 'pincode') targetZoom = 13
    else if (type === 'city') targetZoom = 12
    setZoom(targetZoom)

    if (item.city) {
      setSelectedCity(item.city)
      const st = getStateForCity(item.city)
      if (st) setSelectedState(st)
    }

    // Trigger proximity re-ranking if medicine is already selected
    if (medicine) {
      rankForMedicine(medicine, item.latitude, item.longitude)
    }
  }

  async function fallbackToNetworkOrCity(notice) {
    try {
      const res = await fetch('https://ipapi.co/json/').then((r) => r.json())
      if (res && res.latitude && res.longitude) {
        const lat = Number(res.latitude)
        const lon = Number(res.longitude)
        const city = res.city || 'Your Area'
        const label = `Network Location: ${city}, ${res.region || ''} (${lat.toFixed(3)}° N, ${lon.toFixed(3)}° E)`
        setCoords({ latitude: lat, longitude: lon, label })
        setLocationQuery(label)
        setActiveLocationBadge({
          display_name: label,
          result_type: 'NETWORK_IP',
          is_in_network: false,
        })
        setZoom(13)
        if (medicine) {
          rankForMedicine(medicine, lat, lon)
        }
        if (notice) setError(notice)
        return
      }
    } catch {
      // ignore
    }

    // Default to Vijayawada area hub
    const defaultCity = INDIAN_CITIES.find((c) => c.name === 'Vijayawada') || INDIAN_CITIES[0]
    setCoords({
      latitude: defaultCity.latitude,
      longitude: defaultCity.longitude,
      label: `${defaultCity.name}, ${defaultCity.state} (Area Hub)`,
    })
    setZoom(13)
    setSelectedCity(defaultCity.name)
    setSelectedState(defaultCity.state)
    if (medicine) {
      rankForMedicine(medicine, defaultCity.latitude, defaultCity.longitude)
    }
    if (notice) {
      setError(notice)
    } else {
      setError(
        'Notice: Browser satellite GPS requires HTTPS or http://localhost:5173. Switched to Vijayawada regional network so all local pharmacies are visible.'
      )
    }
  }

  async function handleUseGps() {
    setError(null)

    // Check if origin is secure for hardware GPS (localhost or https)
    const isSecure =
      window.isSecureContext ||
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'

    if (!navigator.geolocation || !isSecure) {
      setDetectingGps(true)
      await fallbackToNetworkOrCity(
        'Notice: Browser satellite GPS requires HTTPS or http://localhost:5173. Automatically positioned via Network so nearby medical shops appear.'
      )
      setDetectingGps(false)
      return
    }

    setDetectingGps(true)

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setDetectingGps(false)
        const lat = pos.coords.latitude
        const lon = pos.coords.longitude
        const label = `Current Device GPS (${lat.toFixed(3)}° N, ${lon.toFixed(3)}° E)`
        setCoords({ latitude: lat, longitude: lon, label })
        setLocationQuery(label)
        setActiveLocationBadge({
          display_name: label,
          result_type: 'DEVICE_GPS',
          is_in_network: false,
        })
        setZoom(14)
        if (medicine) {
          rankForMedicine(medicine, lat, lon)
        }
      },
      async (err) => {
        await fallbackToNetworkOrCity(
          `GPS unavailable (${err.message}). Switched to Network Location so nearby pharmacies remain visible.`
        )
        setDetectingGps(false)
      },
      { timeout: 8000, enableHighAccuracy: true }
    )
  }

  function handleCitySelect(cityName) {
    setSelectedCity(cityName)
    setLocationQuery('')
    setActiveLocationBadge(null)

    if (cityName === 'All') {
      setSelectedState('All')
      setCoords(DEFAULT_LOCATION)
      setZoom(5)
      setNearby(null)
      return
    }

    const cityMeta = INDIAN_CITIES.find((c) => c.name.toLowerCase() === cityName.toLowerCase())
    if (cityMeta) {
      setCoords({
        latitude: cityMeta.latitude,
        longitude: cityMeta.longitude,
        label: `${cityMeta.name}, ${cityMeta.state}`,
      })
      setZoom(cityMeta.zoom || 12)
      setSelectedState(cityMeta.state)
      if (medicine) {
        rankForMedicine(medicine, cityMeta.latitude, cityMeta.longitude)
      }
    }
  }

  function handleStateSelect(stateName) {
    setSelectedState(stateName)
    setLocationQuery('')
    setActiveLocationBadge(null)

    if (stateName === 'All') {
      setSelectedCity('All')
      setCoords(DEFAULT_LOCATION)
      setZoom(5)
      return
    }

    // Pick first city in state
    const firstCity = INDIAN_CITIES.find((c) => c.state === stateName)
    if (firstCity) {
      handleCitySelect(firstCity.name)
    }
  }

  async function rankForMedicine(selected, lat = coords.latitude, lon = coords.longitude) {
    setMedicine(selected)
    setLoadingRank(true)
    setError(null)
    try {
      const data = await pharmaciesApi.nearby({
        latitude: lat,
        longitude: lon,
        medicineId: selected.id,
        radiusKm: radius,
        limit: 15,
      })
      setNearby(data)
    } catch (err) {
      setError(err.message)
      setNearby(null)
    } finally {
      setLoadingRank(false)
    }
  }

  // Filtered and proximity-sorted MediTraceX database directory
  const filteredVerifiedPharmacies = useMemo(() => {
    const list = pharmacies.filter((p) => {
      const state = getStateForCity(p.city)
      const matchesState = selectedState === 'All' || state === selectedState
      const matchesCity = selectedCity === 'All' || p.city === selectedCity
      return matchesState && matchesCity
    })

    // Calculate distance to current reference coordinate and sort by distance
    const withDistances = list.map((p) => {
      const dist = calculateDistanceKm(coords.latitude, coords.longitude, p.latitude, p.longitude)
      return { ...p, calculated_distance: dist }
    })

    withDistances.sort((a, b) => {
      if (a.calculated_distance == null) return 1
      if (b.calculated_distance == null) return -1
      return a.calculated_distance - b.calculated_distance
    })

    return withDistances
  }, [pharmacies, selectedState, selectedCity, coords])

  // Map markers: Both Verified MediTraceX stores & Real External POI stores
  const markers = useMemo(() => {
    const list = []

    // 1. Verified Stores (Teal pins)
    if (nearby?.ranked_pharmacies?.length) {
      nearby.ranked_pharmacies.forEach((item) => {
        list.push({
          id: `verified-${item.pharmacy_id}`,
          name: item.pharmacy_name,
          lat: item.latitude,
          lng: item.longitude,
          city: item.city,
          state: getStateForCity(item.city),
          extra: `${item.availability_status} · ${formatKm(item.distance_km)}`,
          status: item.availability_status,
          isVerified: true,
          phone: item.contact_phone,
          hours: item.operating_hours,
        })
      })
    } else {
      filteredVerifiedPharmacies.forEach((item) => {
        list.push({
          id: `verified-${item.id}`,
          name: item.name,
          lat: item.latitude,
          lng: item.longitude,
          city: item.city,
          state: getStateForCity(item.city),
          extra: `${formatKm(item.calculated_distance)} away · ${item.city}`,
          status: item.is_24_7 ? '24/7 Service' : 'Active Store',
          isVerified: true,
          phone: item.contact_phone,
          hours: item.is_24_7 ? 'Open 24/7' : 'Standard',
        })
      })
    }

    // 2. Real External Local Directory Stores (Blue pins)
    externalPharmacies.forEach((item, idx) => {
      list.push({
        id: `external-${idx}-${item.latitude}`,
        name: item.name,
        lat: item.latitude,
        lng: item.longitude,
        city: item.city || 'Local Area',
        state: item.state || '',
        extra: `${formatKm(item.distance_km)} · Local Directory Chemist`,
        status: 'Inventory Not Verified',
        isVerified: false,
        address: item.address,
        phone: item.phone,
        hours: item.opening_hours,
      })
    })

    return list
  }, [nearby, filteredVerifiedPharmacies, externalPharmacies])

  const center = [Number(coords.latitude), Number(coords.longitude)]

  return (
    <div className="page">
      <PageHeader
        eyebrow="Two-Tier Geospatial Discovery"
        title="Ranked Proximity & Real Local Pharmacy Discovery"
        description="Search any locality (e.g. Patamata, Labbipet, Benz Circle), pincode (e.g. 520010), city, or pharmacy name across India. Displays verified MediTraceX inventory alongside real-world local directory chemists."
      />

      {/* Required Architecture Notice Banner */}
      <div
        style={{
          background: 'var(--teal-soft)',
          border: '1px solid var(--teal-medium)',
          borderRadius: 8,
          padding: '10px 14px',
          marginBottom: 16,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          fontSize: '0.88rem',
          color: 'var(--teal-deep)',
        }}
      >
        <Info size={18} style={{ flexShrink: 0 }} />
        <span>
          <strong>Data Notice:</strong> Nearby pharmacies found from connected location data. Medicine availability is shown only for pharmacies with verified MediTraceX inventory.
        </span>
      </div>

      <div className="insight-strip">
        <div className="insight">
          <b>✓ MediTraceX Verified Stores</b>
          Real-time stock counts, verified batch inventory, and ML forecast intelligence.
        </div>
        <div className="insight">
          <b>Local Directory Chemists</b>
          Hyperlocal medical shops discovered via connected place data with phone and address.
        </div>
        <div className="insight">
          <b>Min-Heap Proximity Engine</b>
          Sub-millisecond priority queue ranking based on Haversine physical distance.
        </div>
      </div>

      <ErrorBanner error={error} />

      {/* Primary Location & Search Controls Card */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h4 style={{ margin: '0 0 14px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--ink)' }}>
          <Compass size={18} color="var(--teal)" /> Location-Based Pharmacy Discovery
        </h4>

        {/* Location Search Bar with Suggestions */}
        <div style={{ position: 'relative', marginBottom: 16 }} ref={suggestionBoxRef}>
          <label className="label" style={{ marginBottom: 6, fontWeight: 600 }}>
            <MapPin size={14} style={{ display: 'inline', marginRight: 4, color: 'var(--teal)' }} />
            Search Any Locality, Area, Pincode, or Pharmacy Name
          </label>
          <div style={{ display: 'flex', gap: 8 }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                className="input"
                type="text"
                placeholder="e.g. Patamata, Labbipet, Benz Circle, 520010, Apollo Pharmacy Patamata..."
                value={locationQuery}
                onChange={(e) => {
                  setLocationQuery(e.target.value)
                  setShowSuggestions(true)
                }}
                onFocus={() => {
                  if (locationSuggestions.length > 0) setShowSuggestions(true)
                }}
                style={{ paddingLeft: 36 }}
              />
              <Search
                size={16}
                style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--muted)' }}
              />
              {locationQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setLocationQuery('')
                    setLocationSuggestions([])
                    setShowSuggestions(false)
                  }}
                  style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)' }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleUseGps}
              disabled={detectingGps}
              style={{ display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap' }}
              title="Detect device GPS location"
            >
              {detectingGps ? <Loader2 size={16} className="spin" /> : <LocateFixed size={16} color="var(--teal)" />}
              <span>{detectingGps ? 'Locating…' : 'Use My Location'}</span>
            </button>
          </div>

          {/* Autocomplete Dropdown */}
          {showSuggestions && (loadingSuggestions || locationSuggestions.length > 0) && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                zIndex: 1000,
                background: '#ffffff',
                border: '1px solid var(--line-strong)',
                borderRadius: 8,
                boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                marginTop: 4,
                maxHeight: 280,
                overflowY: 'auto',
              }}
            >
              {loadingSuggestions && (
                <div style={{ padding: '10px 14px', fontSize: '0.85rem', color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Loader2 size={14} className="spin" /> Geocoding location across India…
                </div>
              )}
              {locationSuggestions.map((item, idx) => (
                <div
                  key={`${item.display_name}-${idx}`}
                  onClick={() => handleSelectLocation(item)}
                  style={{
                    padding: '10px 14px',
                    borderBottom: idx < locationSuggestions.length - 1 ? '1px solid var(--line)' : 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--sand)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = '#ffffff')}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    {(item.result_type || '').toLowerCase() === 'pharmacy' ? (
                      <Store size={16} color="var(--teal)" />
                    ) : (item.result_type || '').toLowerCase() === 'pincode' ? (
                      <Navigation size={16} color="#d97706" />
                    ) : (item.result_type || '').toLowerCase() === 'locality' ? (
                      <MapPin size={16} color="#2563eb" />
                    ) : (
                      <Globe size={16} color="#475569" />
                    )}
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--ink)' }}>
                        {item.display_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
                        {item.latitude.toFixed(4)}° N, {item.longitude.toFixed(4)}° E · {item.city || 'India'} ({item.state || 'IN'})
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    {item.is_verified_network || item.is_in_network ? (
                      <span className="status-badge status-success" style={{ fontSize: '0.7rem' }}>
                        ✓ MediTraceX Store
                      </span>
                    ) : (
                      <span className="status-badge status-neutral" style={{ fontSize: '0.7rem', textTransform: 'capitalize' }}>
                        {item.result_type?.replace('_', ' ') || 'Place'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Area Shortcuts */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 14, alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--teal-deep)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span>🚨</span> Emergency Area Shortcuts:
          </span>
          {[
            { label: 'Benz Circle (VJA)', query: 'Benz Circle' },
            { label: 'Patamata (VJA)', query: 'Patamata' },
            { label: 'Governorpet (VJA)', query: 'Governorpet' },
            { label: 'Hitec City (HYD)', query: 'Hitec City' },
            { label: 'Gachibowli (HYD)', query: 'Gachibowli' },
            { label: 'Dwaraka Nagar (Vizag)', query: 'Dwaraka Nagar' },
            { label: 'Guntur (Brodipet)', query: 'Brodipet' },
            { label: '520010 (Pincode)', query: '520010' },
          ].map((item) => (
            <button
              key={item.label}
              type="button"
              className="btn btn-secondary"
              onClick={async () => {
                setLocationQuery(item.query)
                try {
                  const res = await locationsApi.search(item.query, 1)
                  if (res?.results?.[0]) {
                    handleSelectLocation(res.results[0])
                  }
                } catch (e) {
                  console.warn(e)
                }
              }}
              style={{
                padding: '4px 10px',
                fontSize: '0.78rem',
                borderRadius: 20,
                background: 'var(--sand)',
                border: '1px solid var(--line-strong)',
                fontWeight: 600,
                color: 'var(--ink)'
              }}
            >
              📍 {item.label}
            </button>
          ))}
        </div>

        {/* Region & Radius Filters */}
        <div className="filter-bar" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          <div className="field">
            <label className="label">Filter State</label>
            <select
              className="select"
              value={selectedState}
              onChange={(e) => handleStateSelect(e.target.value)}
            >
              {uniqueStates.map((s) => (
                <option key={s} value={s}>
                  {s === 'All' ? '🇮🇳 All India (Pan-National)' : s}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label className="label">Filter City</label>
            <select
              className="select"
              value={selectedCity}
              onChange={(e) => handleCitySelect(e.target.value)}
            >
              <option value="All">All Cities</option>
              {uniqueCities.filter((c) => c !== 'All').map((c) => (
                <option key={c} value={c}>
                  {c} ({getStateForCity(c)})
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label className="label">Proximity Radius</label>
            <select
              className="select"
              value={radius}
              onChange={(e) => {
                const r = Number(e.target.value)
                setRadius(r)
                if (medicine) rankForMedicine(medicine)
              }}
            >
              <option value={1}>1 km (Immediate Neighbourhood)</option>
              <option value={5}>5 km (Local Suburb / Zone)</option>
              <option value={10}>10 km (City Center)</option>
              <option value={25}>25 km (Metropolitan Area)</option>
              <option value={50}>50 km (District & Suburbs)</option>
            </select>
          </div>
        </div>

        {/* Medicine specific proximity search */}
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--line)' }}>
          <label className="label" style={{ marginBottom: 6 }}>
            <Pill size={14} style={{ display: 'inline', marginRight: 4, color: 'var(--teal)' }} />
            Check Live Stock for Specific Medicine
          </label>
          <div style={{ maxWidth: 480 }}>
            <MedicineSearchBar
              compact
              onSelect={(med) => rankForMedicine(med)}
              onSubmit={async (q) => {
                const hits = await medicinesApi.search(q, 1)
                if (hits?.[0]) rankForMedicine(hits[0])
              }}
            />
          </div>
        </div>

        <p className="sub" style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span>Active Origin:</span>
          <strong style={{ color: 'var(--teal-deep)' }}>
            {coords.label || `${coords.latitude.toFixed(4)}° N, ${coords.longitude.toFixed(4)}° E`}
          </strong>
          {medicine ? ` · Proximity ranking for "${medicine.name}" within ${radius} km` : ` · Finding nearby verified and local chemists within ${radius} km.`}
          {loadingRank ? ' (Calculating Min-Heap ranking…)' : ''}
          {loadingExternal ? ' (Discovering real local shops…)' : ''}
        </p>
      </div>

      {/* Main Map + Directory Grid */}
      <div className="grid grid-2">
        {/* Interactive Map Visualizer */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ margin: 0 }}>Interactive Geospatial Map</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>
              {markers.length} total pins plotted
            </span>
          </div>
          <p className="sub" style={{ margin: '0 0 12px' }}>
            Click pins to view store classification. Teal pins represent verified MediTraceX partners with inventory; Blue pins represent local directory medical shops.
          </p>

          {/* Map Legend */}
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 10, fontSize: '0.8rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#d97706', display: 'inline-block' }} /> Search Origin
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#0f5c5c', display: 'inline-block' }} /> Verified MediTraceX Store
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#2563eb', display: 'inline-block' }} /> Local Directory Chemist
            </span>
          </div>

          <div className="map" style={{ height: 480 }}>
            <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
              <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <MapController center={center} zoom={zoom} />
              
              {/* Searched Location Origin marker */}
              <CircleMarker center={center} radius={10} pathOptions={{ color: '#b7791f', fillColor: '#d97706', fillOpacity: 0.9 }}>
                <Popup>
                  <strong>📍 Active Reference Location</strong>
                  <br />
                  {coords.label}
                  <br />
                  <small>{coords.latitude.toFixed(4)}° N, {coords.longitude.toFixed(4)}° E</small>
                </Popup>
              </CircleMarker>

              {/* Verified & External Pharmacy Pins */}
              {markers.map((marker) => (
                <CircleMarker
                  key={marker.id}
                  center={[Number(marker.lat), Number(marker.lng)]}
                  radius={marker.isVerified ? 8 : 6}
                  pathOptions={{
                    color: marker.isVerified ? '#0f5c5c' : '#2563eb',
                    fillColor: marker.isVerified ? '#1b6b57' : '#3b82f6',
                    fillOpacity: 0.85,
                  }}
                >
                  <Popup>
                    <div style={{ maxWidth: 220 }}>
                      <strong style={{ fontSize: '0.95rem' }}>{marker.name}</strong>
                      <div style={{ margin: '4px 0' }}>
                        {marker.isVerified ? (
                          <span style={{ background: '#e6f4ea', color: '#137333', padding: '2px 6px', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 }}>
                            ✓ Verified MediTraceX Partner
                          </span>
                        ) : (
                          <span style={{ background: '#eff6ff', color: '#1d4ed8', padding: '2px 6px', borderRadius: 4, fontSize: '0.75rem', fontWeight: 600 }}>
                            Local Directory Store
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#555' }}>
                        {marker.address ? `${marker.address}, ` : ''}{marker.city}
                      </div>
                      <div style={{ fontSize: '0.8rem', marginTop: 4, fontWeight: 600, color: marker.isVerified ? '#0f5c5c' : '#1d4ed8' }}>
                        {marker.extra}
                      </div>
                      {marker.phone && (
                        <div style={{ fontSize: '0.75rem', marginTop: 2 }}>
                          📞 {marker.phone}
                        </div>
                      )}
                      {!marker.isVerified && (
                        <div style={{ fontSize: '0.7rem', color: '#777', marginTop: 4, borderTop: '1px solid #eee', paddingTop: 3 }}>
                          * Medicine availability not verified
                        </div>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
            </MapContainer>
          </div>
        </div>

        {/* Directory / Ranked List with Two-Tier Navigation */}
        <div className="card" style={{ maxHeight: 580, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
              Nearby Pharmacies
            </h3>
            {medicine ? (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setNearby(null)}
                style={{ fontSize: '0.75rem', padding: '4px 8px' }}
              >
                Clear Medicine Filter
              </button>
            ) : null}
          </div>

          {/* Two-Tier Filter Tabs */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 12, borderBottom: '1px solid var(--line)', paddingBottom: 8 }}>
            <button
              type="button"
              className={`btn btn-secondary ${activeTab === 'all' ? 'btn-primary' : ''}`}
              onClick={() => setActiveTab('all')}
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              All Stores ({(nearby?.ranked_pharmacies?.length || filteredVerifiedPharmacies.length) + externalPharmacies.length})
            </button>
            <button
              type="button"
              className={`btn btn-secondary ${activeTab === 'verified' ? 'btn-primary' : ''}`}
              onClick={() => setActiveTab('verified')}
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              ✓ Verified Partner Stores ({nearby?.ranked_pharmacies?.length || filteredVerifiedPharmacies.length})
            </button>
            <button
              type="button"
              className={`btn btn-secondary ${activeTab === 'directory' ? 'btn-primary' : ''}`}
              onClick={() => setActiveTab('directory')}
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              Local Directory Chemists ({externalPharmacies.length})
            </button>
          </div>

          {/* List Scroll Area */}
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: 4 }}>
            {/* TIER 1: VERIFIED MEDITRACEX STORES */}
            {(activeTab === 'all' || activeTab === 'verified') && (
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <ShieldCheck size={16} color="var(--teal)" />
                  <strong style={{ fontSize: '0.9rem', color: 'var(--teal-deep)' }}>
                    Verified MediTraceX Stores ({nearby?.ranked_pharmacies?.length || filteredVerifiedPharmacies.length})
                  </strong>
                </div>

                {/* Ranked nearby search results with live medicine stock */}
                {nearby?.ranked_pharmacies?.map((item) => (
                  <div className="rank-card" key={`verified-${item.pharmacy_id}`} style={{ marginBottom: 10, borderLeft: '3px solid var(--teal)' }}>
                    <div className="rank-num">{item.rank}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <strong>{item.pharmacy_name}</strong>
                        <span className="status-badge status-success" style={{ fontSize: '0.65rem' }}>✓ Verified Partner</span>
                      </div>
                      <p className="sub" style={{ margin: '3px 0 0' }}>
                        {item.address}, <strong>{item.city}</strong> · {item.contact_phone}
                        <br />
                        {item.operating_hours} {item.is_24_7 ? '· 24/7 Service' : ''}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right', minWidth: 105 }}>
                      <StatusBadge tone={stockTone(item.availability_status)}>{item.availability_status}</StatusBadge>
                      <div className="sub" style={{ marginTop: 4, fontWeight: 600, color: 'var(--teal-deep)' }}>
                        {formatKm(item.distance_km)}
                      </div>
                      <div className="sub">
                        Stock: {formatNumber(item.stock_quantity)} units
                      </div>
                    </div>
                  </div>
                ))}

                {/* Default directory view when no medicine is chosen */}
                {!nearby && filteredVerifiedPharmacies.map((item, index) => (
                  <div className="rank-card" key={`verified-list-${item.id}`} style={{ marginBottom: 10, borderLeft: '3px solid var(--teal)' }}>
                    <div className="rank-num" style={{ background: '#0f5c5c' }}>#{index + 1}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <strong>{item.name}</strong>
                        <span className="status-badge status-success" style={{ fontSize: '0.65rem' }}>✓ Verified Partner</span>
                      </div>
                      <p className="sub" style={{ margin: '3px 0 0' }}>
                        {item.address}, <strong>{item.city}</strong> ({getStateForCity(item.city)}) - {item.pincode}
                        <br />
                        📞 {item.contact_phone} · ✉️ {item.contact_email}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right', minWidth: 100 }}>
                      <StatusBadge tone={item.is_24_7 ? 'success' : 'neutral'}>
                        {item.is_24_7 ? '24/7' : 'Standard'}
                      </StatusBadge>
                      {item.calculated_distance != null && (
                        <div className="sub" style={{ marginTop: 4, fontWeight: 600, color: 'var(--teal-deep)' }}>
                          {formatKm(item.calculated_distance)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TIER 2: REAL EXTERNAL LOCAL DIRECTORY STORES */}
            {(activeTab === 'all' || activeTab === 'directory') && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, marginTop: activeTab === 'all' ? 12 : 0 }}>
                  <Store size={16} color="#2563eb" />
                  <strong style={{ fontSize: '0.9rem', color: '#1e40af' }}>
                    Real Local Directory Stores ({externalPharmacies.length})
                  </strong>
                  {loadingExternal && <Loader2 size={14} className="spin" />}
                </div>

                {externalPharmacies.map((item, idx) => (
                  <div
                    className="rank-card"
                    key={`external-item-${idx}-${item.latitude}`}
                    style={{ marginBottom: 10, borderLeft: '3px solid #3b82f6', background: 'var(--surface)' }}
                  >
                    <div className="rank-num" style={{ background: '#2563eb' }}>
                      {idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <strong>{item.name}</strong>
                        <span className="status-badge status-neutral" style={{ fontSize: '0.65rem', background: '#eff6ff', color: '#1e40af', border: '1px solid #bfdbfe' }}>
                          Local Chemist
                        </span>
                      </div>
                      <p className="sub" style={{ margin: '3px 0 0' }}>
                        {item.address ? `${item.address} · ` : ''}{item.city || 'Nearby area'}
                        {item.phone ? ` · 📞 ${item.phone}` : ''}
                        {item.opening_hours ? ` · 🕒 ${item.opening_hours}` : ''}
                      </p>
                      {medicine && (
                        <p style={{ margin: '3px 0 0', fontSize: '0.75rem', color: 'var(--muted)' }}>
                          <em>{medicine.name}: Inventory Not Verified</em>
                        </p>
                      )}
                    </div>
                    <div style={{ textAlign: 'right', minWidth: 125 }}>
                      <StatusBadge tone="neutral" style={{ background: '#f1f5f9', color: '#475569', fontSize: '0.72rem' }}>
                        Inventory Not Verified
                      </StatusBadge>
                      <div className="sub" style={{ marginTop: 4, fontWeight: 600, color: '#1e40af' }}>
                        {formatKm(item.distance_km)}
                      </div>
                      <div className="sub" style={{ fontSize: '0.7rem' }}>
                        Local Place POI
                      </div>
                    </div>
                  </div>
                ))}

                {!loadingExternal && externalPharmacies.length === 0 && (
                  <div style={{ textAlign: 'center', padding: '20px', color: 'var(--muted)', fontSize: '0.85rem' }}>
                    No external directory pharmacies found within {radius} km. Try increasing the proximity radius.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
