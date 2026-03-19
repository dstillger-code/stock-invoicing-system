import { useState, useEffect } from 'react'
import { getAuthHeader, useAuthStore } from '../../store/useAuthStore'

interface BillingProduct {
  id: string
  sku: string
  name: string
  description: string | null
  category: string | null
  is_active: boolean
  created_at: string | null
  quantity: number
  country_code: string
  prices: { id: string; net_price: number }[]
}

export function ProductsPage() {
  const [products, setProducts] = useState<BillingProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [showInventoryModal, setShowInventoryModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState<BillingProduct | null>(null)
  const [inventoryProduct, setInventoryProduct] = useState<BillingProduct | null>(null)
  const [saving, setSaving] = useState(false)
  const { isAdmin, isAccountant } = useAuthStore()

  const canEdit = isAccountant()
  const canDelete = isAdmin()

  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category: '',
    net_price: 0,
    quantity: 0,
  })

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/products/', {
        headers: { ...getAuthHeader() },
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al cargar productos')
      }
      const data = await response.json()
      setProducts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProducts()
  }, [])

  const getNetPrice = (product: BillingProduct) => {
    return product.prices?.[0]?.net_price || 0
  }

  const openCreateModal = () => {
    setEditingProduct(null)
    setFormData({ sku: '', name: '', description: '', category: '', net_price: 0, quantity: 0 })
    setShowModal(true)
  }

  const openEditModal = (product: BillingProduct) => {
    setEditingProduct(product)
    setFormData({
      sku: product.sku,
      name: product.name,
      description: product.description || '',
      category: product.category || '',
      net_price: getNetPrice(product),
      quantity: product.quantity,
    })
    setShowModal(true)
  }

  const openInventoryModal = (product: BillingProduct) => {
    setInventoryProduct(product)
    setFormData((prev) => ({ ...prev, quantity: product.quantity }))
    setShowInventoryModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const body = {
        sku: formData.sku,
        name: formData.name,
        description: formData.description || null,
        category: formData.category || null,
        net_price: formData.net_price,
        initial_quantity: formData.quantity,
      }

      const url = editingProduct ? `/api/products/${editingProduct.id}` : '/api/products/'
      const method = editingProduct ? 'PATCH' : 'POST'

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al guardar producto')
      }

      setShowModal(false)
      fetchProducts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setSaving(false)
    }
  }

  const handleInventorySubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inventoryProduct) return
    setSaving(true)
    setError(null)

    try {
      const response = await fetch(`/api/inventory/${inventoryProduct.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({ quantity: formData.quantity }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al actualizar stock')
      }

      setShowInventoryModal(false)
      fetchProducts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (productId: string) => {
    if (!confirm('¿Eliminar este producto? Esta acción no se puede deshacer.')) return
    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: 'DELETE',
        headers: { ...getAuthHeader() },
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al eliminar')
      }
      fetchProducts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const toggleActive = async (product: BillingProduct) => {
    try {
      const response = await fetch(`/api/products/${product.id}/toggle-active`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      })
      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al cambiar estado')
      }
      fetchProducts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Cargando productos...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Productos</h2>
        {canEdit && (
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + Nuevo Producto
          </button>
        )}
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
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">SKU</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Nombre</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Categoría</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Stock</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase">Precio</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Activo</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {products.map((product) => (
              <tr key={product.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-mono">{product.sku}</td>
                <td className="px-4 py-3 text-sm font-medium">{product.name}</td>
                <td className="px-4 py-3 text-sm text-slate-500">{product.category || '-'}</td>
                <td className="px-4 py-3 text-sm text-right">
                  {canEdit ? (
                    <button
                      onClick={() => openInventoryModal(product)}
                      className={`px-2 py-1 rounded text-xs font-medium cursor-pointer ${
                        product.quantity === 0
                          ? 'bg-red-100 text-red-700'
                          : product.quantity < 10
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {product.quantity}
                    </button>
                  ) : (
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        product.quantity === 0
                          ? 'bg-red-100 text-red-700'
                          : product.quantity < 10
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {product.quantity}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-right font-medium">
                  ${getNetPrice(product).toFixed(2)}
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      product.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {product.is_active ? 'Sí' : 'No'}
                  </span>
                </td>
                <td className="px-4 py-3 text-center space-x-2">
                  {canEdit && (
                    <>
                      <button
                        onClick={() => openEditModal(product)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => toggleActive(product)}
                        className={`text-sm hover:underline ${
                          product.is_active ? 'text-orange-600' : 'text-green-600'
                        }`}
                      >
                        {product.is_active ? 'Desactivar' : 'Activar'}
                      </button>
                    </>
                  )}
                  {canDelete && (
                    <button
                      onClick={() => handleDelete(product.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Eliminar
                    </button>
                  )}
                  {!canEdit && (
                    <span className="text-slate-400 text-xs">Solo lectura</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {products.length === 0 && (
          <p className="p-6 text-center text-slate-500">No hay productos registrados.</p>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">
              {editingProduct ? 'Editar Producto' : 'Nuevo Producto'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">SKU *</label>
                <input
                  type="text"
                  value={formData.sku}
                  onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  required
                  disabled={!!editingProduct}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nombre *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Descripción</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Categoría</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full rounded border border-slate-300 px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Precio unitario</label>
                <input
                  type="number"
                  value={formData.net_price || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, net_price: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  min={0}
                  step="0.01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Stock inicial</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })
                  }
                  className="w-full rounded border border-slate-300 px-3 py-2"
                  min={0}
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showInventoryModal && inventoryProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold mb-1">Actualizar Stock</h3>
            <p className="text-sm text-slate-500 mb-4">{inventoryProduct.name}</p>

            <form onSubmit={handleInventorySubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Cantidad en stock</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })
                  }
                  className="w-full rounded border border-slate-300 px-3 py-2 text-lg"
                  min={0}
                  autoFocus
                />
                <p className="text-xs text-slate-500 mt-1">
                  Si el stock llega a 0, el producto se desactivará automáticamente.
                </p>
              </div>

              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowInventoryModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? 'Guardando...' : 'Actualizar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
