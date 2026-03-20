import { Routes, Route } from 'react-router-dom'
import { UsersPage } from './UsersPage'
import { SettingsPage } from './SettingsPage'

export function AdminLayout() {
  return (
    <div className="mx-auto max-w-6xl p-6">
      <header className="mb-6 border-b border-slate-200 pb-4">
        <h1 className="text-lg font-semibold text-slate-800">Administración</h1>
      </header>
      <main>
        <Routes>
          <Route index element={<UsersPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}
