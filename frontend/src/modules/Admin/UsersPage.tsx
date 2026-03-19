import { useState, useEffect } from 'react'
import { getAuthHeader } from '../../store/useAuthStore'

interface User {
  id: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  allowed_modules: string[]
  password_changed: boolean
  expiration_days: number
  created_at: string
}

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'operator',
    allowed_modules: ['stock'],
    expiration_days: 30,
  })

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/auth/admin/users', {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
      })

      if (!response.ok) {
        throw new Error('No tiene permisos para acceder')
      }

      const data = await response.json()
      setUsers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const url = editingUser
        ? `/api/auth/admin/users/${editingUser.id}`
        : '/api/auth/admin/users'
      const method = editingUser ? 'PATCH' : 'POST'

      const body: Record<string, unknown> = {}
      if (!editingUser) {
        body.email = formData.email
        body.password = formData.password
      }
      body.full_name = formData.full_name || null
      body.role = formData.role
      body.allowed_modules = formData.allowed_modules
      body.expiration_days = formData.expiration_days

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al guardar usuario')
      }

      setShowModal(false)
      setEditingUser(null)
      setFormData({
        email: '',
        password: '',
        full_name: '',
        role: 'operator',
        allowed_modules: ['stock'],
        expiration_days: 30,
      })
      fetchUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    setFormData({
      email: user.email,
      password: '',
      full_name: user.full_name || '',
      role: user.role,
      allowed_modules: user.allowed_modules,
      expiration_days: user.expiration_days,
    })
    setShowModal(true)
  }

  const handleDelete = async (userId: string) => {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return

    try {
      const response = await fetch(`/api/auth/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al eliminar usuario')
      }

      fetchUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const toggleActive = async (user: User) => {
    try {
      const response = await fetch(`/api/auth/admin/users/${user.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
        body: JSON.stringify({ is_active: !user.is_active }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al actualizar usuario')
      }

      fetchUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const openCreateModal = () => {
    setEditingUser(null)
    setFormData({
      email: '',
      password: '',
      full_name: '',
      role: 'operator',
      allowed_modules: ['stock'],
      expiration_days: 30,
    })
    setShowModal(true)
  }

  if (loading && users.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Cargando usuarios...</p>
      </div>
    )
  }

  if (error && users.length === 0) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
        {error}
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Administración de Usuarios</h2>
        <button
          onClick={openCreateModal}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Nuevo Usuario
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 border border-red-200">
          {error}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Email</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Nombre</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Rol</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Módulos</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Días</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Activo</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm">{user.email}</td>
                <td className="px-4 py-3 text-sm">{user.full_name || '-'}</td>
                <td className="px-4 py-3 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-700'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {user.allowed_modules.join(', ')}
                </td>
                <td className="px-4 py-3 text-sm text-center">
                  <span className={`px-2 py-1 rounded text-xs ${
                    user.expiration_days <= 5 ? 'bg-red-100 text-red-700' :
                    user.expiration_days <= 10 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {user.expiration_days}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    onClick={() => toggleActive(user)}
                    className={`px-2 py-1 rounded text-xs ${
                      user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {user.is_active ? 'Sí' : 'No'}
                  </button>
                </td>
                <td className="px-4 py-3 text-center space-x-2">
                  <button
                    onClick={() => handleEdit(user)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Editar
                  </button>
                  {user.email !== 'admin@stock.com' && (
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">
              {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {!editingUser && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full rounded border border-slate-300 px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full rounded border border-slate-300 px-3 py-2"
                      required={!editingUser}
                      minLength={6}
                    />
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nombre</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Rol</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                >
                  <option value="operator">Operador</option>
                  <option value="accountant">Contador</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Días de Expiración</label>
                <input
                  type="number"
                  value={formData.expiration_days}
                  onChange={(e) => setFormData({ ...formData, expiration_days: parseInt(e.target.value) || 0 })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  min={0}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Módulos</label>
                <div className="space-x-4">
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.allowed_modules.includes('stock')}
                      onChange={(e) => {
                        const modules = e.target.checked
                          ? [...formData.allowed_modules, 'stock']
                          : formData.allowed_modules.filter(m => m !== 'stock')
                        setFormData({ ...formData, allowed_modules: modules })
                      }}
                      className="mr-2"
                    />
                    Stock
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.allowed_modules.includes('billing')}
                      onChange={(e) => {
                        const modules = e.target.checked
                          ? [...formData.allowed_modules, 'billing']
                          : formData.allowed_modules.filter(m => m !== 'billing')
                        setFormData({ ...formData, allowed_modules: modules })
                      }}
                      className="mr-2"
                    />
                    Facturación
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
