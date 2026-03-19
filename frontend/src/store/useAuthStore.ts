import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  full_name: string | null
  role: string
  allowed_modules: string[]
  password_changed: boolean
  country_code: string
}

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setAuth: (user: User, token: string) => void
  logout: () => void
  hasPermission: (module: string) => boolean
  isAuthenticated: () => boolean
  isAdmin: () => boolean
  isAccountant: () => boolean
  mustChangePassword: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      setUser: (user) => set({ user }),

      setToken: (token) => set({ token }),

      setAuth: (user, token) =>
        set({
          user,
          token,
        }),

      logout: () =>
        set({
          user: null,
          token: null,
        }),

      hasPermission: (module) => {
        const { user } = get()
        if (!user) return false
        return user.allowed_modules.includes(module)
      },

      isAuthenticated: () => {
        const { user, token } = get()
        return user !== null && token !== null
      },

      isAdmin: () => {
        const { user } = get()
        return user?.role === 'admin'
      },

      isAccountant: () => {
        const { user } = get()
        return user?.role === 'accountant' || user?.role === 'admin'
      },

      mustChangePassword: () => {
        const { user } = get()
        return user?.password_changed === false
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
      }),
    }
  )
)

export const getAuthHeader = (): Record<string, string> => {
  const token = useAuthStore.getState().token
  return token ? { Authorization: `Bearer ${token}` } : {}
}
