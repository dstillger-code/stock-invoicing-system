import { useState, useEffect } from 'react'

const API_BASE = '/api/stock'

interface StockItem {
  id: number
  sku: string
  nombre: string
  cantidad: number
  precio_base: string
  created_at?: string
  updated_at?: string
}

export function StockItemsPage() {
  const [items, setItems] = useState<StockItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/items`)
      .then((res) => res.json())
      .then((data) => {
        setItems(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-slate-600">Cargando ítems...</p>

  return (
    <div>
      <h2 className="mb-4 text-xl font-semibold text-slate-800">Ítems de stock</h2>
      {items.length === 0 ? (
        <p className="text-slate-500">No hay ítems. Use la API (POST /api/stock/items) para crear.</p>
      ) : (
        <ul className="divide-y divide-slate-200 rounded border border-slate-200 bg-white">
          {items.map((item) => (
            <li key={item.id} className="flex justify-between px-4 py-3">
              <span className="font-mono text-slate-700">{item.sku}</span>
              <span>{item.nombre}</span>
              <span>{item.cantidad} u.</span>
              <span>${item.precio_base}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
