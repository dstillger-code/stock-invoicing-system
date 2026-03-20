import { useState, useEffect } from 'react'
import { getAuthHeader } from '../../store/useAuthStore'

interface CompanySettings {
  country_code: string
  company_name: string
  logo_url: string | null
  tax_id: string | null
  address: string | null
  phone: string | null
  email: string | null
  updated_at: string | null
}

export function SettingsPage() {
  const [data, setData] = useState<CompanySettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [uploading, setUploading] = useState(false)

  const [form, setForm] = useState({
    company_name: '',
    tax_id: '',
    address: '',
    phone: '',
    email: '',
  })

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/settings/', { headers: { ...getAuthHeader() } })
      if (!res.ok) throw new Error('Error al cargar configuración')
      const json = await res.json()
      setData(json)
      setForm({
        company_name: json.company_name || '',
        tax_id: json.tax_id || '',
        address: json.address || '',
        phone: json.phone || '',
        email: json.email || '',
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      const res = await fetch('/api/settings/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error('Error al guardar')
      const json = await res.json()
      setData(json)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setSaving(false)
    }
  }

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      const body = new FormData()
      body.append('file', file)
      const res = await fetch('/api/settings/logo', {
        method: 'POST',
        headers: { ...getAuthHeader() },
        body,
      })
      if (!res.ok) {
        const json = await res.json()
        throw new Error(json.detail || 'Error al subir logo')
      }
      const json = await res.json()
      setData((prev) => prev ? { ...prev, logo_url: json.logo_url } : prev)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteLogo = async () => {
    setError(null)
    try {
      const res = await fetch('/api/settings/logo', {
        method: 'DELETE',
        headers: { ...getAuthHeader() },
      })
      if (!res.ok) throw new Error('Error al eliminar logo')
      setData((prev) => prev ? { ...prev, logo_url: null } : prev)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Cargando configuración...</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">Configuración de Empresa</h2>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 border border-red-200">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 rounded bg-green-50 p-3 text-sm text-green-600 border border-green-200">
          Cambios guardados correctamente
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-lg p-6 mb-6">
        <h3 className="font-semibold mb-4">Logo de la empresa</h3>
        <div className="flex items-center gap-6">
          <div className="w-32 h-32 border-2 border-dashed border-slate-300 rounded-lg flex items-center justify-center bg-slate-50 overflow-hidden">
            {data?.logo_url ? (
              <img
                src={data.logo_url}
                alt="Logo"
                className="max-w-full max-h-full object-contain"
              />
            ) : (
              <span className="text-slate-400 text-4xl font-bold">
                {form.company_name.charAt(0).toUpperCase() || '?'}
              </span>
            )}
          </div>
          <div className="flex flex-col gap-2">
            <label className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 cursor-pointer text-sm text-center disabled:opacity-50">
              {uploading ? 'Subiendo...' : 'Subir logo'}
              <input
                type="file"
                accept="image/png,image/jpeg,image/gif,image/webp"
                onChange={handleLogoUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
            {data?.logo_url && (
              <button
                onClick={handleDeleteLogo}
                className="px-4 py-2 text-red-600 border border-red-300 rounded hover:bg-red-50 text-sm"
              >
                Eliminar
              </button>
            )}
            <p className="text-xs text-slate-400">PNG, JPG o WebP · Máx 2MB</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-lg p-6 space-y-4">
        <h3 className="font-semibold">Datos de la empresa</h3>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Nombre de la empresa *
          </label>
          <input
            type="text"
            value={form.company_name}
            onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            className="w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            RUT / Tax ID
          </label>
          <input
            type="text"
            value={form.tax_id}
            onChange={(e) => setForm({ ...form, tax_id: e.target.value })}
            className="w-full rounded border border-slate-300 px-3 py-2"
            placeholder="ej: 12.345.678-9"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Dirección
          </label>
          <input
            type="text"
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            className="w-full rounded border border-slate-300 px-3 py-2"
            placeholder="Calle, número, ciudad"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Teléfono
            </label>
            <input
              type="text"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full rounded border border-slate-300 px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full rounded border border-slate-300 px-3 py-2"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  )
}
