import { NavLink, Routes, Route } from 'react-router-dom'
import { StockItemsPage } from './StockItemsPage'

export function StockLayout() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 flex items-center gap-4 border-b border-slate-200 pb-4">
        <NavLink
          to="/stock"
          className="text-lg font-semibold text-slate-800 hover:text-slate-600"
        >
          Stock
        </NavLink>
        <nav className="flex gap-4">
          <NavLink
            to="/stock/items"
            className={({ isActive }) =>
              isActive ? 'text-blue-600 font-medium' : 'text-slate-600 hover:text-slate-800'
            }
          >
            Ítems
          </NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route index element={<div className="text-slate-600">Seleccione una opción del menú Stock.</div>} />
          <Route path="items" element={<StockItemsPage />} />
        </Routes>
      </main>
    </div>
  )
}
