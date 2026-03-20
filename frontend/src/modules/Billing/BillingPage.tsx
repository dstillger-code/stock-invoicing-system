import { useState, useEffect, useRef } from 'react'
import { getAuthHeader } from '../../store/useAuthStore'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'

interface BillingProduct {
  id: string
  sku: string
  name: string
  category: string | null
  stock: number
  unit_price: number
}

interface InvoiceItem {
  product_id: string
  quantity: number
}

interface InvoiceResponse {
  document_type: string
  document_number: string
  country_code: string
  country_name: string
  issued_at: string
  issuer_name: string
  items: {
    product_id: string
    sku: string
    name: string
    quantity: number
    unit_price: number
    net_amount: number
    tax_rate: number
    tax_amount: number
    total: number
  }[]
  subtotal: number
  tax_rate: number
  tax_type: string | null
  tax_amount: number
  total: number
  currency: string
  company_name: string
  company_tax_id: string | null
  company_address: string | null
  company_phone: string | null
  company_email: string | null
}

interface TaxRates {
  country_code: string
  rates: { default: number; [key: string]: number }
  document_types: string[]
}

export function BillingPage() {
  const [products, setProducts] = useState<BillingProduct[]>([])
  const [taxRates, setTaxRates] = useState<TaxRates | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [invoice, setInvoice] = useState<InvoiceResponse | null>(null)
  const [generating, setGenerating] = useState(false)
  const invoiceRef = useRef<HTMLDivElement>(null)

  const [documentType, setDocumentType] = useState('factura')
  const [taxType, setTaxType] = useState<string>('')
  const [cartItems, setCartItems] = useState<InvoiceItem[]>([])
  const [quantities, setQuantities] = useState<Record<string, number>>({})

  useEffect(() => {
    fetchBillingData()
  }, [])

  const fetchBillingData = async () => {
    setLoading(true)
    try {
      const [productsRes, ratesRes] = await Promise.all([
        fetch('/api/billing/products', { headers: { ...getAuthHeader() } }),
        fetch('/api/billing/tax-rates', { headers: { ...getAuthHeader() } }),
      ])

      if (!productsRes.ok || !ratesRes.ok) {
        throw new Error('Error al cargar datos de facturación')
      }

      const [productsData, ratesData] = await Promise.all([
        productsRes.json(),
        ratesRes.json(),
      ])

      setProducts(productsData)
      setTaxRates(ratesData)
      setDocumentType(ratesData.document_types[0] || 'factura')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const addToCart = (product: BillingProduct) => {
    const qty = quantities[product.id] || 1
    if (qty <= 0) return
    if (product.stock < qty) {
      alert(`Stock insuficiente. Disponible: ${product.stock}`)
      return
    }

    setCartItems((prev) => {
      const existing = prev.find((i) => i.product_id === product.id)
      if (existing) {
        return prev.map((i) =>
          i.product_id === product.id ? { ...i, quantity: i.quantity + qty } : i
        )
      }
      return [...prev, { product_id: product.id, quantity: qty }]
    })
    setQuantities((prev) => ({ ...prev, [product.id]: 1 }))
  }

  const updateCartQuantity = (productId: string, qty: number) => {
    if (qty <= 0) {
      removeFromCart(productId)
      return
    }
    setCartItems((prev) =>
      prev.map((i) => (i.product_id === productId ? { ...i, quantity: qty } : i))
    )
  }

  const removeFromCart = (productId: string) => {
    setCartItems((prev) => prev.filter((i) => i.product_id !== productId))
  }

  const getCartProduct = (productId: string) => products.find((p) => p.id === productId)

  const subtotal = cartItems.reduce((sum, item) => {
    const p = getCartProduct(item.product_id)
    return sum + (p ? p.unit_price * item.quantity : 0)
  }, 0)

  const getTaxRate = () => {
    if (!taxRates) return 0
    const country = taxRates.country_code
    if (country === 'CL') return taxRates.rates.default
    if (country === 'AR') {
      if (documentType === 'boleta') return 0
      if (taxType === 'reduced') return taxRates.rates.reduced || 10.5
      if (taxType === 'additional') return taxRates.rates.additional || 27
      return taxRates.rates.default
    }
    return 0
  }

  const taxAmount = subtotal * (getTaxRate() / 100)
  const total = subtotal + taxAmount

  const generateInvoice = async () => {
    if (cartItems.length === 0) {
      alert('Agregue productos al carrito primero')
      return
    }

    setGenerating(true)
    setError(null)

    try {
      const body: Record<string, unknown> = {
        document_type: documentType,
        items: cartItems,
      }
      if (taxRates?.country_code === 'AR' && taxType) {
        body.tax_type = taxType
      }

      const response = await fetch('/api/billing/invoice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Error al generar documento')
      }

      const invoiceData = await response.json()
      setInvoice(invoiceData)
      setCartItems([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setGenerating(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  const handleExportPDF = () => {
    if (!invoice) return
    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    const docTypeLabel = invoice.document_type === 'factura' ? 'FACTURA' : 'BOLETA'

    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.text(docTypeLabel, pageWidth / 2, 18, { align: 'center' })

    doc.setFontSize(12)
    doc.setFont('helvetica', 'normal')
    doc.text(`N° ${invoice.document_number}`, pageWidth / 2, 25, { align: 'center' })

    doc.setFontSize(10)
    const leftCol = 14
    let y = 36

    doc.setFont('helvetica', 'bold')
    doc.text(invoice.company_name, leftCol, y)
    doc.setFont('helvetica', 'normal')
    y += 5
    if (invoice.company_address) {
      doc.text(invoice.company_address, leftCol, y)
      y += 5
    }
    const contactParts = [
      invoice.company_phone,
      invoice.company_email,
      invoice.company_tax_id ? `RUT: ${invoice.company_tax_id}` : null,
    ].filter(Boolean)
    if (contactParts.length) {
      doc.text(contactParts.join('  ·  '), leftCol, y)
      y += 5
    }

    y += 4
    doc.setFontSize(9)
    doc.text(`Fecha: ${new Date(invoice.issued_at).toLocaleString('es-CL')}`, leftCol, y)
    y += 5
    doc.text(`Moneda: ${invoice.currency}`, leftCol, y)
    y += 5
    doc.text(`IVA: ${invoice.tax_rate}%${invoice.tax_type ? ` (${invoice.tax_type})` : ''}`, leftCol, y)
    y += 5
    doc.text(`Emitido por: ${invoice.issuer_name}`, leftCol, y)

    autoTable(doc, {
      startY: y + 6,
      head: [['Producto / SKU', 'Cantidad', 'P. Unit.', 'Neto', `IVA ${invoice.tax_rate}%`, 'Total']],
      body: invoice.items.map((item) => [
        `${item.name}\n(${item.sku})`,
        item.quantity.toString(),
        `$${item.unit_price.toFixed(2)}`,
        `$${item.net_amount.toFixed(2)}`,
        `$${item.tax_amount.toFixed(2)}`,
        `$${item.total.toFixed(2)}`,
      ]),
      foot: [
        ['', '', '', 'Subtotal:', `$${invoice.subtotal.toFixed(2)}`],
        ['', '', '', `IVA (${invoice.tax_rate}%):`, `$${invoice.tax_amount.toFixed(2)}`],
        ['', '', '', 'TOTAL:', `$${invoice.total.toFixed(2)}`],
      ],
      styles: { fontSize: 9, cellPadding: 3 },
      headStyles: { fillColor: [51, 65, 85], textColor: 255, fontStyle: 'bold' },
      footStyles: { fontStyle: 'bold' },
      columnStyles: {
        0: { cellWidth: 50 },
        1: { cellWidth: 20, halign: 'center' },
        2: { cellWidth: 25, halign: 'right' },
        3: { cellWidth: 25, halign: 'right' },
        4: { cellWidth: 25, halign: 'right' },
        5: { cellWidth: 30, halign: 'right' },
      },
      didParseCell: (data) => {
        if (data.section === 'foot' && data.column.index >= 3) {
          data.cell.styles.halign = 'right'
        }
      },
    })

    doc.save(`${invoice.document_number}.pdf`)
  }

  const handleExportCSV = () => {
    if (!invoice) return
    const separator = ','
    const lines: string[] = []

    lines.push(`\uFEFF"${docHeader('Factura')} - ${invoice.document_number}"`)
    lines.push(`"${docHeader('Pais')}",${invoice.country_name}`)
    lines.push(`"${docHeader('Emisor')}",${escapeCSV(invoice.issuer_name)}`)
    lines.push(`"${docHeader('Fecha')}",${new Date(invoice.issued_at).toLocaleString('es-CL')}`)
    lines.push(`"${docHeader('Moneda')}",${invoice.currency}`)
    lines.push(`"${docHeader('Tipo IVA')}",${invoice.tax_rate}%${invoice.tax_type ? ` (${invoice.tax_type})` : ''}`)
    lines.push('')
    lines.push(`"${docHeader('Producto / SKU')}","${docHeader('Cantidad')}","${docHeader('P. Unit.')}","${docHeader('Neto')}","${docHeader(`IVA ${invoice.tax_rate}%`)}","${docHeader('Total')}"`)

    for (const item of invoice.items) {
      lines.push(
        `"${escapeCSV(item.name)} (${escapeCSV(item.sku)})"${separator}` +
        `${item.quantity}${separator}` +
        `${item.unit_price.toFixed(2)}${separator}` +
        `${item.net_amount.toFixed(2)}${separator}` +
        `${item.tax_amount.toFixed(2)}${separator}` +
        `${item.total.toFixed(2)}`
      )
    }

    lines.push('')
    lines.push(`"${docHeader('Subtotal')}",,,,${invoice.subtotal.toFixed(2)}`)
    lines.push(`"${docHeader(`IVA (${invoice.tax_rate}%)`)}",,,,${invoice.tax_amount.toFixed(2)}`)
    lines.push(`"${docHeader('TOTAL')}",,,,${invoice.total.toFixed(2)}`)

    const csv = lines.join('\r\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${invoice.document_number}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  function escapeCSV(value: string): string {
    return value.replace(/"/g, '""')
  }

  function docHeader(label: string): string {
    return label
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Cargando datos de facturación...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">Facturación</h2>
          <p className="text-sm text-slate-500 mt-1">
            {taxRates?.country_code === 'CL' ? 'Chile' : 'Argentina'} · IVA: {getTaxRate()}%
          </p>
        </div>
        <button
          onClick={fetchBillingData}
          className="px-3 py-1 text-sm text-slate-600 border border-slate-300 rounded hover:bg-slate-50"
        >
          Actualizar
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 border border-red-200">
          {error}
        </div>
      )}

      {invoice ? (
        <div className="bg-white border border-slate-200 rounded-lg p-6 invoice-print-area" ref={invoiceRef}>
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-xl font-bold">
                {invoice.document_type === 'factura' ? 'FACTURA' : 'BOLETA'}
              </h3>
              <p className="text-sm text-slate-500">N° {invoice.document_number}</p>
              <p className="font-medium mt-1">{invoice.company_name}</p>
              {invoice.company_address && (
                <p className="text-sm text-slate-500">{invoice.company_address}</p>
              )}
              {invoice.company_tax_id && (
                <p className="text-sm text-slate-500">RUT: {invoice.company_tax_id}</p>
              )}
              {invoice.company_phone && (
                <p className="text-sm text-slate-500">{invoice.company_phone}</p>
              )}
            </div>
            <div className="flex gap-2 flex-wrap print:hidden">
              <button
                onClick={handleExportPDF}
                className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                PDF
              </button>
              <button
                onClick={handleExportCSV}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                CSV
              </button>
              <button
                onClick={handlePrint}
                className="px-3 py-1.5 text-sm bg-slate-600 text-white rounded hover:bg-slate-700 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Imprimir
              </button>
              <button
                onClick={() => setInvoice(null)}
                className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Nueva Venta
              </button>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6 text-sm">
            <div>
              <p className="text-slate-500">Emisor</p>
              <p className="font-medium">{invoice.issuer_name}</p>
            </div>
            <div>
              <p className="text-slate-500">Fecha</p>
              <p className="font-medium">
                {new Date(invoice.issued_at).toLocaleString('es-CL')}
              </p>
            </div>
            <div>
              <p className="text-slate-500">Moneda</p>
              <p className="font-medium">{invoice.currency}</p>
            </div>
          </div>

          <table className="w-full text-sm mb-4">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 text-slate-500">Producto</th>
                <th className="text-right py-2 text-slate-500">Cantidad</th>
                <th className="text-right py-2 text-slate-500">P. Unit.</th>
                <th className="text-right py-2 text-slate-500">Neto</th>
                <th className="text-right py-2 text-slate-500">IVA {invoice.tax_rate}%</th>
                <th className="text-right py-2 text-slate-500">Total</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items.map((item) => (
                <tr key={item.product_id} className="border-b border-slate-100">
                  <td className="py-2">
                    {item.name} <span className="text-slate-400">({item.sku})</span>
                  </td>
                  <td className="py-2 text-right">{item.quantity}</td>
                  <td className="py-2 text-right">${item.unit_price.toFixed(2)}</td>
                  <td className="py-2 text-right">${item.net_amount.toFixed(2)}</td>
                  <td className="py-2 text-right">${item.tax_amount.toFixed(2)}</td>
                  <td className="py-2 text-right font-medium">${item.total.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-end">
            <div className="text-right space-y-1">
              <div className="flex justify-between gap-8">
                <span className="text-slate-500">Subtotal:</span>
                <span className="font-medium">${invoice.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between gap-8">
                <span className="text-slate-500">
                  IVA ({invoice.tax_rate}%{invoice.tax_type ? ` (${invoice.tax_type})` : ''}):
                </span>
                <span className="font-medium">${invoice.tax_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between gap-8 text-lg font-bold border-t border-slate-200 pt-1">
                <span>TOTAL:</span>
                <span className="text-blue-600">${invoice.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-lg p-4">
            <h3 className="font-semibold mb-3">Productos disponibles</h3>
            <div className="overflow-auto max-h-96">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-2 text-slate-500">Producto</th>
                    <th className="text-right py-2 text-slate-500">Precio</th>
                    <th className="text-center py-2 text-slate-500">Stock</th>
                    <th className="text-center py-2 text-slate-500">Cantidad</th>
                    <th className="text-center py-2 text-slate-500"></th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p) => (
                    <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-2">
                        <span className="font-medium">{p.name}</span>
                        <span className="block text-xs text-slate-400">{p.sku}</span>
                      </td>
                      <td className="py-2 text-right font-medium">${p.unit_price.toFixed(2)}</td>
                      <td className="py-2 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${
                            p.stock === 0
                              ? 'bg-red-100 text-red-700'
                              : p.stock < 5
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          {p.stock}
                        </span>
                      </td>
                      <td className="py-2 text-center">
                        <input
                          type="number"
                          min={1}
                          max={p.stock}
                          value={quantities[p.id] || 1}
                          onChange={(e) =>
                            setQuantities((prev) => ({
                              ...prev,
                              [p.id]: parseInt(e.target.value) || 1,
                            }))
                          }
                          className="w-16 rounded border border-slate-300 px-2 py-1 text-center"
                        />
                      </td>
                      <td className="py-2 text-center">
                        <button
                          onClick={() => addToCart(p)}
                          disabled={p.stock === 0}
                          className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-30"
                        >
                          +
                        </button>
                      </td>
                    </tr>
                  ))}
                  {products.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-6 text-center text-slate-400">
                        No hay productos disponibles
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <h3 className="font-semibold mb-3">Carrito de venta</h3>

            {cartItems.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">
                Agregue productos para comenzar
              </p>
            ) : (
              <>
                <div className="space-y-2 mb-4">
                  {cartItems.map((item) => {
                    const p = getCartProduct(item.product_id)
                    if (!p) return null
                    return (
                      <div
                        key={item.product_id}
                        className="flex justify-between items-center text-sm border-b border-slate-50 pb-2"
                      >
                        <div className="flex-1">
                          <span className="font-medium">{p.name}</span>
                          <div className="flex items-center gap-1 mt-1">
                            <button
                              onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                              className="w-6 h-6 rounded bg-slate-100 text-xs hover:bg-slate-200"
                            >
                              -
                            </button>
                            <span className="px-2">{item.quantity}</span>
                            <button
                              onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                              className="w-6 h-6 rounded bg-slate-100 text-xs hover:bg-slate-200"
                            >
                              +
                            </button>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="font-medium">${(p.unit_price * item.quantity).toFixed(2)}</span>
                          <button
                            onClick={() => removeFromCart(item.product_id)}
                            className="block text-xs text-red-500 hover:underline mt-1"
                          >
                            Quitar
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="border-t border-slate-200 pt-3 space-y-2 mb-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Subtotal</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">IVA ({getTaxRate()}%)</span>
                    <span>${taxAmount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between font-bold text-lg border-t border-slate-200 pt-2">
                    <span>Total</span>
                    <span className="text-blue-600">${total.toFixed(2)}</span>
                  </div>
                </div>
              </>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Tipo de documento
              </label>
              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
              >
                {taxRates?.document_types.map((dt) => (
                  <option key={dt} value={dt}>
                    {dt === 'factura' ? 'Factura' : 'Boleta'}
                  </option>
                ))}
              </select>
            </div>

            {taxRates?.country_code === 'AR' && documentType === 'factura' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Tipo de IVA
                </label>
                <select
                  value={taxType}
                  onChange={(e) => setTaxType(e.target.value)}
                  className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="">Default (21%)</option>
                  <option value="reduced">Reducido (10.5%)</option>
                  <option value="additional">Adicional (27%)</option>
                </select>
              </div>
            )}

            <button
              onClick={generateInvoice}
              disabled={cartItems.length === 0 || generating}
              className="w-full py-3 bg-green-600 text-white font-semibold rounded hover:bg-green-700 disabled:opacity-40"
            >
              {generating ? 'Generando...' : `Generar ${documentType === 'factura' ? 'Factura' : 'Boleta'}`}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
