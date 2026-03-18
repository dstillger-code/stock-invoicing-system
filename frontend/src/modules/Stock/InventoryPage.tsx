import { useEffect, useState } from 'react'
import { useAuthStore, getAuthHeader } from '../../store/useAuthStore'

interface InventoryItem {
  product_id: string
  sku: string
  name: string
  category: string | null
  quantity: number
  prices: {
    country_code: string
    net_price: number
    tax_rate: number
    is_exempt: boolean
  }[]
}

export function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user } = useAuthStore()

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

        const data = await response.json()
        setItems(data.items)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido')
      } finally {
        setLoading(false)
      }
    }

    fetchInventory()
  }, [])

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

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Inventario</h2>
      <p className="text-sm text-slate-500 mb-4">Usuario: {user?.email}</p>
      
      {items.length === 0 ? (
        <p className="text-slate-500">No hay productos en el inventario.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-slate-200 rounded-lg">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">SKU</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">Producto</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-slate-700">Categoría</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-slate-700">Cantidad</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-slate-700">Precio CL</th>
                <th className="px-4 py-2 text-right text-sm font-medium text-slate-700">Precio AR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {items.map((item) => {
                const priceCL = item.prices.find((p) => p.country_code === 'CL')
                const priceAR = item.prices.find((p) => p.country_code === 'AR')
                return (
                  <tr key={item.product_id} className="hover:bg-slate-50">
                    <td className="px-4 py-2 text-sm">{item.sku}</td>
                    <td className="px-4 py-2 text-sm font-medium">{item.name}</td>
                    <td className="px-4 py-2 text-sm text-slate-500">{item.category || '-'}</td>
                    <td className="px-4 py-2 text-sm text-right">{item.quantity}</td>
                    <td className="px-4 py-2 text-sm text-right">
                      {priceCL ? `$${priceCL.net_price.toFixed(2)}` : '-'}
                    </td>
                    <td className="px-4 py-2 text-sm text-right">
                      {priceAR ? `$${priceAR.net_price.toFixed(2)}` : '-'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
