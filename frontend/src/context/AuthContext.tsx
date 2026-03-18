import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  id: number
  email: string
  full_name: string | null
  rol: string
  permisos_modulos: string[]
}

interface AuthContextType {
  user: User | null
  setUser: (user: User | null) => void
  hasPermission: (module: string) => boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        setUser(JSON.parse(stored))
      } catch {
        localStorage.removeItem('user')
      }
    }
  }, [])

  const hasPermission = (module: string): boolean => {
    if (!user) return false
    return user.permisos_modulos.includes(module)
  }

  const isAuthenticated = user !== null

  return (
    <AuthContext.Provider value={{ user, setUser, hasPermission, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
