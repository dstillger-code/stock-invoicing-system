import { Outlet, Routes, Route } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-md">
        <h1 className="mb-6 text-center text-2xl font-semibold text-slate-800">
          Módulo Auth
        </h1>
        <Routes>
          <Route index element={<div className="rounded border border-slate-200 bg-white p-6 text-slate-600">Login (próximamente)</div>} />
          <Route path="*" element={<Outlet />} />
        </Routes>
      </div>
    </div>
  )
}
