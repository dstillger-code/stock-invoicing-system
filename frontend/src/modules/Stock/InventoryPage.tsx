import { useEffect, useState } from 'react'
import { getAuthHeader } from '../../store/useAuthStore'

interface InventoryItem {
  product_id: string
  sku: string
  name: string
  category: string | null
  quantity: number
  net_price: number
}

interface InventoryResponse {
  user: string
  country: string
  total_products: number
  items: InventoryItem[]
}

export function InventoryPage() {
  const [data, setData] = useState<InventoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchText, setSearchText] = useState('')
  const [searchCategory, setSearchCategory] = useState('')

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const response = await fetch('/api/inventory/', {
          headers: {
            'Content-Type': 'application/json',
            ...getAuthHeader(),
          },
        })

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.')
          }
          throw new Error('Error al cargar el inventario')
        }

        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido')
      } finally {
        setLoading(false)
      }
    }

    fetchInventory()
  }, [])

  const filteredItems = (data?.items || []).filter((item) => {
    const matchesText =
      !searchText ||
      item.name.toLowerCase().includes(searchText.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchText.toLowerCase())
    const matchesCategory =
      !searchCategory ||
      (item.category || '').toLowerCase().includes(searchCategory.toLowerCase())
    return matchesText && matchesCategory
  })

  const categories = [...new Set((data?.items || []).map((i) => i.category).filter(Boolean))] as string[]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Cargando inventario...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
        {error}
      </div>
    )
  }

  const countryName = data?.country === 'CL' ? 'Chile' : 'Argentina'
  const currency = data?.country === 'CL' ? 'CLP' : 'ARS'

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-2xl font-bold">Inventario</h2>
          <p className="text-sm text-slate-500">
            {data?.total_products || 0} productos · {countryName}
          </p>
        </div>
      </div>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          placeholder="Buscar por nombre o SKU..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
        />
        <select
          value={searchCategory}
          onChange={(e) => setSearchCategory(e.target.value)}
          className="rounded border border-slate-300 px-3 py-2 text-sm"
        >
          <option value="">Todas las categorías</option>
          {categories.map((cat) => (
            <option key={cat} value={cat || ''}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {filteredItems.length === 0 ? (
        <p className="text-slate-500">
          {data?.items.length === 0
            ? 'No hay productos en el inventario.'
            : 'No hay productos que coincidan con la búsqueda.'}
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-slate-200 rounded-lg">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">SKU</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">Producto</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">Categoría</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-slate-700">Cantidad</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-slate-700">Precio ({currency})</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filteredItems.map((item) => (
                <tr key={item.product_id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 text-sm font-mono">{item.sku}</td>
                  <td className="px-4 py-2 text-sm font-medium">{item.name}</td>
                  <td className="px-4 py-2 text-sm text-slate-500">{item.category || '-'}</td>
                  <td className="px-4 py-2 text-sm text-right">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        item.quantity === 0
                          ? 'bg-red-100 text-red-700'
                          : item.quantity < 10
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-green-100 text-green-700'
                      }`}
                    >
                      {item.quantity}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-sm text-right font-medium">
                    ${item.net_price.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
