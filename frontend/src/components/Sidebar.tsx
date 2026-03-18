import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import { useConfigStore } from '../store/useConfigStore'

interface NavItem {
  path: string
  label: string
  module?: string
}

const navItems: NavItem[] = [
  { path: '/stock', label: 'Stock', module: 'stock' },
  { path: '/invoicing', label: 'Facturación', module: 'invoicing' },
  { path: '/negocio', label: 'Negocios', module: 'negocio' },
]

export function Sidebar() {
  const { user, hasPermission, logout } = useAuthStore()
  const { country, taxRateName, setCountry } = useConfigStore()

  const handleCountryToggle = () => {
    setCountry(country === 'CL' ? 'AR' : 'CL')
  }

  const handleLogout = () => {
    logout()
    window.location.href = '/auth/login'
  }

  return (
    <aside className="w-64 bg-slate-800 text-white min-h-screen p-4 flex flex-col">
      <div className="mb-6">
        <h1 className="text-xl font-bold">Stock & Facturación</h1>
        <p className="text-sm text-slate-400 mt-1">{user?.full_name || user?.email}</p>
        <span className="inline-block mt-1 px-2 py-0.5 bg-slate-700 rounded text-xs">
          {user?.role || 'operator'}
        </span>
      </div>

      <div className="mb-4 p-3 bg-slate-700 rounded">
        <p className="text-xs text-slate-400 mb-1">País / Tasa IVA</p>
        <button
          onClick={handleCountryToggle}
          className="flex items-center gap-2 w-full"
        >
          <span className="text-lg font-bold">{country}</span>
          <span className="text-sm text-slate-300">{taxRateName}</span>
        </button>
      </div>

      <nav className="space-y-2 flex-1">
        {navItems.map((item) => {
          if (item.module && !hasPermission(item.module)) {
            return null
          }
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `block px-4 py-2 rounded transition ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700'
                }`
              }
            >
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-auto">
        <button
          onClick={handleLogout}
          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition text-sm"
        >
          Cerrar Sesión
        </button>
      </div>
    </aside>
  )
}
