import { createContext, useContext, useEffect, useState } from 'react'
import { inventoryApi, mapLimited, medicinesApi, pharmaciesApi } from '../services/api'

function summarizeInventory(records) {
  const available = records.filter((item) => String(item.stock_status).toLowerCase().includes('in stock'))
  const low = records.filter((item) => String(item.stock_status).toLowerCase().includes('low'))
  const out = records.filter((item) => String(item.stock_status).toLowerCase().includes('out'))
  const units = records.reduce((sum, item) => sum + Number(item.stock_quantity || 0), 0)
  const belowSafety = records.filter(
    (item) => Number(item.stock_quantity || 0) <= Number(item.safety_stock_threshold || 0)
  )
  return {
    total: records.length,
    available: available.length,
    low: low.length,
    out: out.length,
    units,
    uniqueLowMedicines: new Set(low.map((item) => item.medicine_id)).size,
    uniqueOutMedicines: new Set(out.map((item) => item.medicine_id)).size,
    uniqueAtRiskMedicines: new Set(belowSafety.map((item) => item.medicine_id)).size,
  }
}

const PlatformDataContext = createContext(null)

export function PlatformDataProvider({ children }) {
  const [state, setState] = useState({
    loading: true,
    error: null,
    medicines: [],
    medicineTotal: 0,
    pharmacies: [],
    inventory: [],
    summary: summarizeInventory([]),
  })

  async function load() {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const [catalog, pharmacies] = await Promise.all([
        medicinesApi.list({ page: 1, pageSize: 100 }),
        pharmaciesApi.list(),
      ])
      const items = catalog?.items || []
      let allMedicines = items
      if ((catalog?.total || 0) > items.length) {
        const page2 = await medicinesApi.list({ page: 2, pageSize: 100 })
        allMedicines = [...items, ...(page2?.items || [])]
      }

      const pharmacyList = Array.isArray(pharmacies) ? pharmacies : []
      const sampledPharmacies = pharmacyList.length > 25 ? pharmacyList.slice(0, 25) : pharmacyList
      const inventoryChunks = await mapLimited(
        sampledPharmacies,
        async (pharmacy) => {
          try {
            return await inventoryApi.byPharmacy(pharmacy.id)
          } catch {
            return []
          }
        },
        8
      )
      const inventory = inventoryChunks.flat().filter(Boolean)
      setState({
        loading: false,
        error: null,
        medicines: allMedicines,
        medicineTotal: catalog?.total ?? allMedicines.length,
        pharmacies: pharmacyList,
        inventory,
        summary: summarizeInventory(inventory),
      })
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: error.message || 'Unable to load platform data.',
      }))
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <PlatformDataContext.Provider value={{ ...state, reload: load }}>
      {children}
    </PlatformDataContext.Provider>
  )
}

export function usePlatformData() {
  const context = useContext(PlatformDataContext)
  if (!context) {
    throw new Error('usePlatformData must be used within PlatformDataProvider')
  }
  return context
}
