import { Routes, Route } from 'react-router-dom'

export function InvoicingLayout() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 border-b border-slate-200 pb-4">
        <h1 className="text-lg font-semibold text-slate-800">Facturación</h1>
      </header>
      <main>
        <Routes>
          <Route index element={<div className="text-slate-600">Módulo Facturación (impuestos por país, Strategy). Configuración Chile 19% y estructura Argentina lista.</div>} />
        </Routes>
      </main>
    </div>
  )
}
