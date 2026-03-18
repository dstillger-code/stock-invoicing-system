import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthLayout } from './components/auth/AuthLayout'
import { StockLayout } from './components/stock/StockLayout'
import { InvoicingLayout } from './components/invoicing/InvoicingLayout'

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Routes>
        <Route path="/auth/*" element={<AuthLayout />} />
        <Route path="/stock/*" element={<StockLayout />} />
        <Route path="/invoicing/*" element={<InvoicingLayout />} />
        <Route path="/" element={<Navigate to="/stock" replace />} />
      </Routes>
    </div>
  )
}

export default App
