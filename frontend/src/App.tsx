import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { useAuthStore } from './store/authStore'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import MarketDataPage from './pages/MarketDataPage'
import InvestmentFormPage from './pages/InvestmentFormPage'
import PortfolioPage from './pages/PortfolioPage'
import AuthDebug from './components/AuthDebug'
import { useEffect } from 'react'

function App() {
  const { isAuthenticated, isLoading, user } = useAuthStore()

  // Debug authentication state
  useEffect(() => {
    console.log('🔍 Auth State Debug:', { 
      isAuthenticated, 
      isLoading, 
      user: user?.name,
      userId: user?.id 
    })
  }, [isAuthenticated, isLoading, user])

  // Test render
  console.log('🎯 App: Rendering app')

  // Add error boundary
  if (typeof window !== 'undefined') {
    window.addEventListener('error', (event) => {
      console.error('🚨 Global Error:', event.error)
    })
  }

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-background text-foreground">
        {/* Test Banner */}
        <div className="bg-green-600 text-white text-center py-1 text-sm">
          ✅ App is Loading - BullBearPK Investment Platform
        </div>
        
        {/* Debug component - remove in production */}
        <AuthDebug />
        
        <Routes>
          {/* Landing Page - Always accessible as default */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Dashboard and Features - No authentication required */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/investment-form" element={<InvestmentFormPage />} />
          <Route path="/market-data" element={<MarketDataPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          
          {/* Fallback - Redirect to landing page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </ThemeProvider>
  )
}

export default App