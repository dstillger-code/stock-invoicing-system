import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../../store/useAuthStore'

interface PrivateRouteProps {
  children: React.ReactNode
  module?: string
}

export function PrivateRoute({ children, module }: PrivateRouteProps) {
  const { hasPermission, isAuthenticated } = useAuthStore()
  const location = useLocation()

  if (!isAuthenticated()) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />
  }

  if (module && !hasPermission(module)) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
