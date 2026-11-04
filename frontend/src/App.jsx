import { HashRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { PlatformDataProvider } from './hooks/usePlatformData.jsx'
import { AppShell } from './components/AppShell'

import DashboardPage from './pages/DashboardPage'
import MedicinesPage from './pages/MedicinesPage'
import MedicineDetailPage from './pages/MedicineDetailPage'
import PharmaciesPage from './pages/PharmaciesPage'
import InventoryPage from './pages/InventoryPage'
import IntelligencePage from './pages/IntelligencePage'
import RiskPage from './pages/RiskPage'
import AnalyticsPage from './pages/AnalyticsPage'
import RequestsPage from './pages/RequestsPage'
import WatchlistPage from './pages/WatchlistPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import NotFoundPage from './pages/NotFoundPage'

function AuthenticatedShell() {
  return (
    <PlatformDataProvider>
      <AppShell />
    </PlatformDataProvider>
  )
}

export default function App() {
  return (
    <HashRouter>
      <AuthProvider>
        <Routes>
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route element={<AuthenticatedShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="medicines" element={<MedicinesPage />} />
            <Route path="medicines/:medicineId" element={<MedicineDetailPage />} />
            <Route path="pharmacies" element={<PharmaciesPage />} />
            <Route path="inventory" element={<InventoryPage />} />
            <Route path="intelligence" element={<IntelligencePage />} />
            <Route path="risk" element={<RiskPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="requests" element={<RequestsPage />} />
            <Route path="watchlist" element={<WatchlistPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </HashRouter>
  )
}
