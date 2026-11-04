const resolveApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl && !envUrl.includes('127.0.0.1') && !envUrl.includes('localhost')) {
    return envUrl
  }

  if (typeof window !== 'undefined' && window.location) {
    const { hostname, protocol, port } = window.location
    if (port === '5173') {
      return `${protocol}//${hostname}:5173`
    }
    return `${protocol}//${hostname}:8000`
  }

  return 'http://127.0.0.1:8000'
}

export const API_BASE_URL = resolveApiBaseUrl()

export const APP_NAME = 'MediTraceX'
export const APP_TAGLINE = 'Find. Verify. Reach.'

export const DEFAULT_LOCATION = {
  latitude: 20.5937,
  longitude: 78.9629,
  label: 'All India (National Network)',
  zoom: 5,
}

export const INDIAN_CITIES = [
  // Andhra Pradesh
  { name: 'Vijayawada', state: 'Andhra Pradesh', latitude: 16.5062, longitude: 80.6480, zoom: 12 },
  { name: 'Visakhapatnam', state: 'Andhra Pradesh', latitude: 17.6868, longitude: 83.2185, zoom: 12 },
  { name: 'Guntur', state: 'Andhra Pradesh', latitude: 16.3067, longitude: 80.4365, zoom: 13 },
  { name: 'Tirupati', state: 'Andhra Pradesh', latitude: 13.6288, longitude: 79.4192, zoom: 13 },

  // Telangana
  { name: 'Hyderabad', state: 'Telangana', latitude: 17.4435, longitude: 78.3780, zoom: 12 },
  { name: 'Secunderabad', state: 'Telangana', latitude: 17.4399, longitude: 78.4983, zoom: 13 },
  { name: 'Warangal', state: 'Telangana', latitude: 17.9689, longitude: 79.5941, zoom: 13 },

  // Karnataka
  { name: 'Bengaluru', state: 'Karnataka', latitude: 12.9716, longitude: 77.5946, zoom: 12 },
  { name: 'Mysuru', state: 'Karnataka', latitude: 12.2958, longitude: 76.6394, zoom: 13 },
  { name: 'Mangaluru', state: 'Karnataka', latitude: 12.8702, longitude: 74.8435, zoom: 13 },
  { name: 'Hubballi', state: 'Karnataka', latitude: 15.3645, longitude: 75.1245, zoom: 13 },

  // Tamil Nadu
  { name: 'Chennai', state: 'Tamil Nadu', latitude: 13.0827, longitude: 80.2707, zoom: 12 },
  { name: 'Coimbatore', state: 'Tamil Nadu', latitude: 11.0168, longitude: 76.9558, zoom: 12 },
  { name: 'Madurai', state: 'Tamil Nadu', latitude: 9.9288, longitude: 78.1485, zoom: 13 },
  { name: 'Salem', state: 'Tamil Nadu', latitude: 11.6745, longitude: 78.1412, zoom: 13 },

  // Maharashtra
  { name: 'Mumbai', state: 'Maharashtra', latitude: 19.0760, longitude: 72.8777, zoom: 12 },
  { name: 'Pune', state: 'Maharashtra', latitude: 18.5204, longitude: 73.8567, zoom: 12 },
  { name: 'Navi Mumbai', state: 'Maharashtra', latitude: 19.0768, longitude: 72.9985, zoom: 12 },
  { name: 'Thane', state: 'Maharashtra', latitude: 19.2185, longitude: 72.9782, zoom: 12 },
  { name: 'Nagpur', state: 'Maharashtra', latitude: 21.1458, longitude: 79.0882, zoom: 12 },
  { name: 'Nashik', state: 'Maharashtra', latitude: 20.0065, longitude: 73.7650, zoom: 13 },

  // Delhi NCR
  { name: 'New Delhi', state: 'Delhi NCR', latitude: 28.6139, longitude: 77.2090, zoom: 12 },
  { name: 'Gurgaon', state: 'Delhi NCR', latitude: 28.4595, longitude: 77.0266, zoom: 12 },
  { name: 'Noida', state: 'Delhi NCR', latitude: 28.5355, longitude: 77.3910, zoom: 12 },
  { name: 'Ghaziabad', state: 'Delhi NCR', latitude: 28.6385, longitude: 77.3712, zoom: 12 },

  // West Bengal
  { name: 'Kolkata', state: 'West Bengal', latitude: 22.5726, longitude: 88.3639, zoom: 12 },
  { name: 'Siliguri', state: 'West Bengal', latitude: 26.7315, longitude: 88.4312, zoom: 13 },

  // Gujarat
  { name: 'Ahmedabad', state: 'Gujarat', latitude: 23.0225, longitude: 72.5714, zoom: 12 },
  { name: 'Surat', state: 'Gujarat', latitude: 21.1702, longitude: 72.8311, zoom: 12 },
  { name: 'Vadodara', state: 'Gujarat', latitude: 22.3072, longitude: 73.1812, zoom: 13 },
  { name: 'Rajkot', state: 'Gujarat', latitude: 22.2855, longitude: 70.7745, zoom: 13 },

  // Rajasthan
  { name: 'Jaipur', state: 'Rajasthan', latitude: 26.9124, longitude: 75.7873, zoom: 12 },
  { name: 'Jodhpur', state: 'Rajasthan', latitude: 26.2715, longitude: 73.0185, zoom: 13 },
  { name: 'Udaipur', state: 'Rajasthan', latitude: 24.5985, longitude: 73.6895, zoom: 13 },

  // Kerala
  { name: 'Kochi', state: 'Kerala', latitude: 9.9715, longitude: 76.2812, zoom: 12 },
  { name: 'Thiruvananthapuram', state: 'Kerala', latitude: 8.5285, longitude: 76.9412, zoom: 13 },
  { name: 'Kozhikode', state: 'Kerala', latitude: 11.2612, longitude: 75.7945, zoom: 13 },

  // Odisha
  { name: 'Bhubaneswar', state: 'Odisha', latitude: 20.2961, longitude: 85.8245, zoom: 12 },
  { name: 'Cuttack', state: 'Odisha', latitude: 20.4512, longitude: 85.8745, zoom: 13 },

  // Uttar Pradesh
  { name: 'Lucknow', state: 'Uttar Pradesh', latitude: 26.8467, longitude: 80.9462, zoom: 12 },
  { name: 'Kanpur', state: 'Uttar Pradesh', latitude: 26.4685, longitude: 80.3412, zoom: 12 },
  { name: 'Varanasi', state: 'Uttar Pradesh', latitude: 25.3195, longitude: 82.9812, zoom: 13 },
  { name: 'Agra', state: 'Uttar Pradesh', latitude: 27.2015, longitude: 78.0045, zoom: 13 },

  // Madhya Pradesh
  { name: 'Indore', state: 'Madhya Pradesh', latitude: 22.7196, longitude: 75.8577, zoom: 12 },
  { name: 'Bhopal', state: 'Madhya Pradesh', latitude: 23.2325, longitude: 77.4312, zoom: 12 },
  { name: 'Gwalior', state: 'Madhya Pradesh', latitude: 26.2085, longitude: 78.1895, zoom: 13 },

  // Punjab & Chandigarh
  { name: 'Chandigarh', state: 'Punjab / Chandigarh', latitude: 30.7333, longitude: 76.7794, zoom: 12 },
  { name: 'Ludhiana', state: 'Punjab', latitude: 30.8915, longitude: 75.8345, zoom: 12 },
  { name: 'Amritsar', state: 'Punjab', latitude: 31.6395, longitude: 74.8712, zoom: 13 },

  // Bihar
  { name: 'Patna', state: 'Bihar', latitude: 25.6145, longitude: 85.1215, zoom: 12 },
  { name: 'Gaya', state: 'Bihar', latitude: 24.7955, longitude: 85.0012, zoom: 13 },
]

export const CITY_STATE_MAP = {
  Vijayawada: 'Andhra Pradesh',
  Visakhapatnam: 'Andhra Pradesh',
  Guntur: 'Andhra Pradesh',
  Tirupati: 'Andhra Pradesh',
  Hyderabad: 'Telangana',
  Secunderabad: 'Telangana',
  Warangal: 'Telangana',
  Bengaluru: 'Karnataka',
  Mysuru: 'Karnataka',
  Mangaluru: 'Karnataka',
  Hubballi: 'Karnataka',
  Chennai: 'Tamil Nadu',
  Coimbatore: 'Tamil Nadu',
  Madurai: 'Tamil Nadu',
  Salem: 'Tamil Nadu',
  Mumbai: 'Maharashtra',
  Pune: 'Maharashtra',
  'Navi Mumbai': 'Maharashtra',
  Thane: 'Maharashtra',
  Nagpur: 'Maharashtra',
  Nashik: 'Maharashtra',
  'New Delhi': 'Delhi NCR',
  Gurgaon: 'Delhi NCR',
  Noida: 'Delhi NCR',
  Ghaziabad: 'Delhi NCR',
  Kolkata: 'West Bengal',
  Siliguri: 'West Bengal',
  Ahmedabad: 'Gujarat',
  Surat: 'Gujarat',
  Vadodara: 'Gujarat',
  Rajkot: 'Gujarat',
  Jaipur: 'Rajasthan',
  Jodhpur: 'Rajasthan',
  Udaipur: 'Rajasthan',
  Kochi: 'Kerala',
  Thiruvananthapuram: 'Kerala',
  Kozhikode: 'Kerala',
  Bhubaneswar: 'Odisha',
  Cuttack: 'Odisha',
  Lucknow: 'Uttar Pradesh',
  Kanpur: 'Uttar Pradesh',
  Varanasi: 'Uttar Pradesh',
  Agra: 'Uttar Pradesh',
  Indore: 'Madhya Pradesh',
  Bhopal: 'Madhya Pradesh',
  Gwalior: 'Madhya Pradesh',
  Chandigarh: 'Punjab / Chandigarh',
  Ludhiana: 'Punjab',
  Amritsar: 'Punjab',
  Patna: 'Bihar',
  Gaya: 'Bihar',
}

export function getStateForCity(city) {
  return CITY_STATE_MAP[city] || 'India'
}

export const DEFAULT_RADIUS_KM = 35
export const TOKEN_STORAGE_KEY = 'mtx_access_token'
export const USER_STORAGE_KEY = 'mtx_user'

export const REQUEST_STATUSES = [
  'PENDING',
  'ACCEPTED',
  'FULFILLED',
  'CANCELLED',
  'NOT_AVAILABLE',
]
