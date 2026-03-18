import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  full_name: string | null
  role: string
  allowed_modules: string[]
}

interface AuthState {
  user: User | null
  token: string | null
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setAuth: (user: User, token: string) => void
  logout: () => void
  hasPermission: (module: string) => boolean
  isAuthenticated: boolean
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

      get isAuthenticated() {
        return get().user !== null
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
