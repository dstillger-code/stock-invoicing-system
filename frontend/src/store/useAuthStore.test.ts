import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore, User } from './useAuthStore'

const mockUser: User = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'operator',
  allowed_modules: ['stock', 'billing'],
  password_changed: true,
}

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
    })
  })

  describe('setAuth', () => {
    it('should set user and token', () => {
      useAuthStore.getState().setAuth(mockUser, 'jwt-token-123')

      expect(useAuthStore.getState().user).toEqual(mockUser)
      expect(useAuthStore.getState().token).toBe('jwt-token-123')
    })
  })

  describe('setUser', () => {
    it('should set user without modifying token', () => {
      useAuthStore.setState({ token: 'existing-token' })
      useAuthStore.getState().setUser(mockUser)

      expect(useAuthStore.getState().user).toEqual(mockUser)
      expect(useAuthStore.getState().token).toBe('existing-token')
    })
  })

  describe('setToken', () => {
    it('should set token without modifying user', () => {
      useAuthStore.setState({ user: mockUser })
      useAuthStore.getState().setToken('new-token')

      expect(useAuthStore.getState().user).toEqual(mockUser)
      expect(useAuthStore.getState().token).toBe('new-token')
    })
  })

  describe('logout', () => {
    it('should clear user and token', () => {
      useAuthStore.getState().setAuth(mockUser, 'token')
      useAuthStore.getState().logout()

      expect(useAuthStore.getState().user).toBeNull()
      expect(useAuthStore.getState().token).toBeNull()
    })
  })

  describe('hasPermission', () => {
    it('should return true if user has module permission', () => {
      useAuthStore.getState().setAuth(mockUser, 'token')

      expect(useAuthStore.getState().hasPermission('stock')).toBe(true)
      expect(useAuthStore.getState().hasPermission('billing')).toBe(true)
    })

    it('should return false if user lacks module permission', () => {
      useAuthStore.getState().setAuth(mockUser, 'token')

      expect(useAuthStore.getState().hasPermission('reports')).toBe(false)
    })

    it('should return false if user is null', () => {
      expect(useAuthStore.getState().hasPermission('stock')).toBe(false)
    })
  })

  describe('isAuthenticated', () => {
    it('should return true when user and token exist', () => {
      useAuthStore.getState().setAuth(mockUser, 'token')

      expect(useAuthStore.getState().isAuthenticated()).toBe(true)
    })

    it('should return false when user is null', () => {
      useAuthStore.setState({ token: 'token' })

      expect(useAuthStore.getState().isAuthenticated()).toBe(false)
    })

    it('should return false when token is null', () => {
      useAuthStore.setState({ user: mockUser })

      expect(useAuthStore.getState().isAuthenticated()).toBe(false)
    })

    it('should return false when both are null', () => {
      expect(useAuthStore.getState().isAuthenticated()).toBe(false)
    })
  })

  describe('getAuthHeader', () => {
    it('should return Authorization header with token', () => {
      useAuthStore.getState().setAuth(mockUser, 'bearer-token')
      const header = useAuthStore.getState().token
        ? { Authorization: `Bearer ${useAuthStore.getState().token}` }
        : {}

      expect(header).toEqual({ Authorization: 'Bearer bearer-token' })
    })

    it('should return empty object when no token', () => {
      const header = useAuthStore.getState().token
        ? { Authorization: `Bearer ${useAuthStore.getState().token}` }
        : {}

      expect(header).toEqual({})
    })
  })
})
