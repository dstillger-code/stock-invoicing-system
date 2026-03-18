import { Routes, Route, Navigate } from 'react-router-dom'
import { PrivateRoute } from './components/PrivateRoute'
import { Sidebar } from './components/Sidebar'
import { AuthLayout } from './components/auth/AuthLayout'
import { StockLayout } from './components/stock/StockLayout'
import { InvoicingLayout } from './components/invoicing/InvoicingLayout'

function AppLayout() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/stock/*" element={<StockLayout />} />
          <Route path="/invoicing/*" element={<InvoicingLayout />} />
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
