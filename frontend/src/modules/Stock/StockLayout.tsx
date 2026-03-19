import { NavLink, Routes, Route } from 'react-router-dom'
import { StockItemsPage } from './StockItemsPage'
import { InventoryPage } from './InventoryPage'
import { ProductsPage } from './ProductsPage'

export function StockLayout() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 flex items-center gap-4 border-b border-slate-200 pb-4">
        <span className="text-lg font-semibold text-slate-800">Stock</span>
        <nav className="flex gap-4">
          <NavLink
            to="/stock/inventory"
            className={({ isActive }) =>
              isActive ? 'text-blue-600 font-medium' : 'text-slate-600 hover:text-slate-800'
            }
          >
            Inventario
          </NavLink>
          <NavLink
            to="/stock/items"
            className={({ isActive }) =>
              isActive ? 'text-blue-600 font-medium' : 'text-slate-600 hover:text-slate-800'
            }
          >
            Ítems
          </NavLink>
          <NavLink
            to="/stock/products"
            className={({ isActive }) =>
              isActive ? 'text-blue-600 font-medium' : 'text-slate-600 hover:text-slate-800'
            }
          >
            Productos
          </NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route index element={<InventoryPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="items" element={<StockItemsPage />} />
          <Route path="products" element={<ProductsPage />} />
        </Routes>
      </main>
    </div>
  )
}
