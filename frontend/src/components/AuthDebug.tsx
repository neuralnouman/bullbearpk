import React from 'react'
import { useAuthStore } from '../store/authStore'

const AuthDebug: React.FC = () => {
  const { isAuthenticated, isLoading, user, token } = useAuthStore()

  return (
    <div className="fixed top-4 right-4 bg-black/80 text-white p-4 rounded-lg text-xs z-50">
      <h3 className="font-bold mb-2">🔍 Auth Debug</h3>
      <div className="space-y-1">
        <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
        <div>Loading: {isLoading ? '⏳' : '✅'}</div>
        <div>User: {user?.name || 'None'}</div>
        <div>Token: {token ? '✅' : '❌'}</div>
        <div>User ID: {user?.id || 'None'}</div>
      </div>
    </div>
  )
}

export default AuthDebug 