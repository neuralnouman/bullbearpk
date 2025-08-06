import { Routes, Route, Navigate } from 'react-router-dom'

import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import MarketDataPage from './pages/MarketDataPage'
import InvestmentFormPage from './pages/InvestmentFormPage'
import PortfolioPage from './pages/EnhancedPortfolioPage'
import NewsPage from './pages/NewsPage'

import ProtectedRoute from './components/ProtectedRoute'
import { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'

function App() {

  // Global error boundary
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        console.error('🚨 Global Error:', event.error)
      })
      
      window.addEventListener('unhandledrejection', (event) => {
        console.error('🚨 Unhandled Promise Rejection:', event.reason)
      })
    }
  }, [])

  return (
    <div className="min-h-screen bg-background text-foreground">
        <Routes>
          {/* Landing Page - Always accessible as default */}
          <Route path="/" element={<LandingPage />} />
          
          {/* Authentication Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected Routes - Require authentication */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/investment-form" element={
            <ProtectedRoute>
              <InvestmentFormPage />
            </ProtectedRoute>
          } />
          <Route path="/market-data" element={
            <ProtectedRoute>
              <MarketDataPage />
            </ProtectedRoute>
          } />
          <Route path="/portfolio" element={
            <ProtectedRoute>
              <PortfolioPage />
            </ProtectedRoute>
          } />
          <Route path="/news" element={
            <ProtectedRoute>
              <NewsPage />
            </ProtectedRoute>
          } />
          
          
          {/* Fallback - Redirect to landing page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        {/* Global Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--toast-bg)',
              color: 'var(--toast-color)',
              border: '1px solid var(--toast-border)',
            },
            success: {
              iconTheme: {
                primary: '#22c55e',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#ffffff',
              },
            },
          }}
        />
      </div>
  )
}

export default App