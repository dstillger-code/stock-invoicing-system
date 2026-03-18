import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type CountryCode = 'CL' | 'AR'

export const TAX_RATES = {
  CL: {
    default: 19,
    name: 'IVA Chile',
  },
  AR: {
    default: 21,
    name: 'IVA Argentina',
    extra: [10.5, 27],
  },
} as const

interface ConfigState {
  country: CountryCode
  setCountry: (country: CountryCode) => void
  getTaxRate: () => number
  taxRateName: string
}

export const useConfigStore = create<ConfigState>()(
  persist(
    (set, get) => ({
      country: 'CL',
      taxRateName: TAX_RATES.CL.name,

      setCountry: (country) =>
        set({
          country,
          taxRateName: TAX_RATES[country].name,
        }),

      getTaxRate: () => {
        const { country } = get()
        return TAX_RATES[country].default
      },
    }),
    {
      name: 'config-storage',
    }
  )
)
