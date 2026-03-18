import { Routes, Route } from 'react-router-dom'
import { BillingPage } from './BillingPage'

export function BillingLayout() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 border-b border-slate-200 pb-4">
        <h1 className="text-lg font-semibold text-slate-800">Facturación</h1>
      </header>
      <main>
        <Routes>
          <Route index element={<BillingPage />} />
        </Routes>
      </main>
    </div>
  )
}
