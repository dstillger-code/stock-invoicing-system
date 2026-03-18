import { Outlet, Routes, Route } from 'react-router-dom'
import { LoginPage } from './LoginPage'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-md">
        <h1 className="mb-6 text-center text-2xl font-semibold text-slate-800">
          Stock & Facturación
        </h1>
        <Routes>
          <Route index element={<LoginPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="*" element={<Outlet />} />
        </Routes>
      </div>
    </div>
  )
}
