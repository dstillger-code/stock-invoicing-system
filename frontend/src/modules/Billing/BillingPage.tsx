import { useState } from 'react'
import { useConfigStore } from '../../store/useConfigStore'
import { getAuthHeader } from '../../store/useAuthStore'

interface CalculationResult {
  net_price: number
  tax_rate: number
  tax_type: string | null
  tax_amount: number
  total: number
  country_code: string
}

export function BillingPage() {
  const { country, taxRateName } = useConfigStore()
  const [netPrice, setNetPrice] = useState('')
  const [taxType, setTaxType] = useState<string>('')
  const [result, setResult] = useState<CalculationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        net_price: netPrice,
        country_code: country,
      })
      if (taxType) {
        params.append('tax_type', taxType)
      }

      const response = await fetch(`/api/inventory/calculate?${params}`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeader(),
        },
      })

      if (!response.ok) {
        throw new Error('Error al calcular')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-4">Facturación</h2>
      <p className="text-sm text-slate-500 mb-6">
        País activo: <span className="font-medium">{country}</span> ({taxRateName})
      </p>

      <div className="bg-white border border-slate-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium mb-4">Calculadora de Impuestos</h3>
        
        <form onSubmit={handleCalculate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Precio Neto
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={netPrice}
              onChange={(e) => setNetPrice(e.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              placeholder="0.00"
              required
            />
          </div>

          {country === 'AR' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Tipo de IVA
              </label>
              <select
                value={taxType}
                onChange={(e) => setTaxType(e.target.value)}
                className="w-full rounded border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              >
                <option value="">Default (21%)</option>
                <option value="reduced">Reducido (10.5%)</option>
                <option value="additional">Adicional (27%)</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !netPrice}
            className="w-full rounded bg-blue-600 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Calculando...' : 'Calcular Total'}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="bg-white border border-slate-200 rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">Resultado</h3>
          <dl className="space-y-2">
            <div className="flex justify-between">
              <dt className="text-slate-600">Precio Neto:</dt>
              <dd className="font-medium">${result.net_price.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-600">IVA ({result.tax_rate}%):</dt>
              <dd className="font-medium">${result.tax_amount.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between border-t border-slate-200 pt-2">
              <dt className="text-lg font-medium">Total:</dt>
              <dd className="text-lg font-bold text-blue-600">${result.total.toFixed(2)}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  )
}
