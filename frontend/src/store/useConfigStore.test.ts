import { describe, it, expect, beforeEach } from 'vitest'
import { useConfigStore, TAX_RATES } from './useConfigStore'

describe('useConfigStore', () => {
  beforeEach(() => {
    useConfigStore.setState({
      country: 'CL',
      taxRateName: TAX_RATES.CL.name,
    })
  })

  describe('initial state', () => {
    it('should have CL as default country', () => {
      expect(useConfigStore.getState().country).toBe('CL')
    })

    it('should have CL tax rate name', () => {
      expect(useConfigStore.getState().taxRateName).toBe('IVA Chile')
    })
  })

  describe('setCountry', () => {
    it('should change country to AR', () => {
      useConfigStore.getState().setCountry('AR')

      expect(useConfigStore.getState().country).toBe('AR')
      expect(useConfigStore.getState().taxRateName).toBe('IVA Argentina')
    })

    it('should change country back to CL', () => {
      useConfigStore.setState({ country: 'AR', taxRateName: 'IVA Argentina' })
      useConfigStore.getState().setCountry('CL')

      expect(useConfigStore.getState().country).toBe('CL')
      expect(useConfigStore.getState().taxRateName).toBe('IVA Chile')
    })
  })

  describe('getTaxRate', () => {
    it('should return 19% for Chile', () => {
      useConfigStore.setState({ country: 'CL' })
      expect(useConfigStore.getState().getTaxRate()).toBe(19)
    })

    it('should return 21% for Argentina', () => {
      useConfigStore.setState({ country: 'AR' })
      expect(useConfigStore.getState().getTaxRate()).toBe(21)
    })
  })

  describe('TAX_RATES constant', () => {
    it('should have Chile defined', () => {
      expect(TAX_RATES.CL).toBeDefined()
      expect(TAX_RATES.CL.default).toBe(19)
      expect(TAX_RATES.CL.name).toBe('IVA Chile')
    })

    it('should have Argentina defined', () => {
      expect(TAX_RATES.AR).toBeDefined()
      expect(TAX_RATES.AR.default).toBe(21)
      expect(TAX_RATES.AR.name).toBe('IVA Argentina')
      expect(TAX_RATES.AR.extra).toEqual([10.5, 27])
    })
  })
})
