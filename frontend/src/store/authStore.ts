import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  createdAt: string
  riskTolerance: 'low' | 'moderate' | 'high'
  investmentGoal: string
  preferredSectors: string[]
  portfolio?: {
    totalValue: number
    totalInvested: number
    cashBalance: number
    availableCash: number
  }
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (userData: {
    name: string
    email: string
    password: string
    riskTolerance: 'low' | 'moderate' | 'high'
    investmentGoal: string
    preferredSectors: string[]
  }) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  getProfile: (userId: string) => Promise<void>
}

const API_BASE_URL = 'http://localhost:5000/api'

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      token: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          })

          const data = await response.json()

          if (!response.ok) {
            throw new Error(data.error || 'Login failed')
          }

          if (data.success && data.user) {
            const user: User = {
              id: data.user.id,
              email: data.user.email,
              name: data.user.name,
              createdAt: data.user.created_at,
              riskTolerance: data.user.risk_tolerance,
              investmentGoal: data.user.investment_goal,
              preferredSectors: data.user.preferred_sectors || [],
              portfolio: data.user.portfolio ? {
                totalValue: data.user.portfolio.total_value,
                totalInvested: data.user.portfolio.total_invested,
                cashBalance: data.user.portfolio.cash_balance,
                availableCash: data.user.portfolio.available_cash,
              } : undefined
            }
            
            set({
              user,
              isAuthenticated: true,
              token: `user_${user.id}`, // Simple token for now
              isLoading: false
            })
          } else {
            throw new Error('Invalid response from server')
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (userData: {
        name: string
        email: string
        password: string
        riskTolerance: 'low' | 'moderate' | 'high'
        investmentGoal: string
        preferredSectors: string[]
      }) => {
        set({ isLoading: true })
        try {
          const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: userData.name,
              email: userData.email,
              password: userData.password,
              risk_tolerance: userData.riskTolerance,
              investment_goal: userData.investmentGoal,
              preferred_sectors: userData.preferredSectors,
            }),
          })

          const data = await response.json()

          if (!response.ok) {
            throw new Error(data.error || 'Registration failed')
          }

          if (data.success && data.user) {
            const user: User = {
              id: data.user.id,
              email: data.user.email,
              name: data.user.name,
              createdAt: data.user.created_at,
              riskTolerance: data.user.risk_tolerance,
              investmentGoal: data.user.investment_goal,
              preferredSectors: data.user.preferred_sectors || [],
              portfolio: data.user.portfolio ? {
                totalValue: data.user.portfolio.total_value,
                totalInvested: data.user.portfolio.total_invested,
                cashBalance: data.user.portfolio.cash_balance,
                availableCash: data.user.portfolio.available_cash,
              } : undefined
            }
            
            set({
              user,
              isAuthenticated: true,
              token: `user_${user.id}`, // Simple token for now
              isLoading: false
            })
          } else {
            throw new Error('Invalid response from server')
          }
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: async () => {
        try {
          // Call logout endpoint
          await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          })
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({
            user: null,
            isAuthenticated: false,
            token: null,
            isLoading: false
          })
        }
      },

      getProfile: async (userId: string) => {
        try {
          const response = await fetch(`${API_BASE_URL}/auth/profile?user_id=${userId}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          })

          const data = await response.json()

          if (!response.ok) {
            throw new Error(data.error || 'Failed to get profile')
          }

          if (data.success && data.user) {
            const user: User = {
              id: data.user.id,
              email: data.user.email,
              name: data.user.name,
              createdAt: data.user.created_at,
              riskTolerance: data.user.risk_tolerance,
              investmentGoal: data.user.investment_goal,
              preferredSectors: data.user.preferred_sectors || [],
              portfolio: data.user.portfolio ? {
                totalValue: data.user.portfolio.total_value,
                totalInvested: data.user.portfolio.total_invested,
                cashBalance: data.user.portfolio.cash_balance,
                availableCash: data.user.portfolio.available_cash,
              } : undefined
            }
            
            set({ user })
          }
        } catch (error) {
          console.error('Get profile error:', error)
          throw error
        }
      },

      updateUser: (updatedUser: Partial<User>) => {
        const { user } = get()
        if (user) {
          set({
            user: { ...user, ...updatedUser }
          })
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        token: state.token
      })
    }
  )
) 