import { Routes, Route, Navigate } from 'react-router-dom'
import { PrivateRoute } from './components/ui/PrivateRoute'
import { Sidebar } from './components/Sidebar'
import { AuthLayout } from './modules/Auth/AuthLayout'
import { StockLayout } from './modules/Stock/StockLayout'
import { BillingLayout } from './modules/Billing/BillingLayout'

function AppLayout() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/stock/*" element={<StockLayout />} />
          <Route path="/billing/*" element={<BillingLayout />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/auth/*" element={<AuthLayout />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/stock" replace />} />
    </Routes>
  )
}

export default App
