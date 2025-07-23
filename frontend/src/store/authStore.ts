import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  createdAt: string
  investmentProfile?: {
    totalInvested: number
    totalReturns: number
    riskTolerance: 'low' | 'medium' | 'high'
    preferredSectors: string[]
  }
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      token: null,

      login: async (email: string, _password: string) => {
        set({ isLoading: true })
        try {
          // TODO: Replace with actual API call
          const mockUser: User = {
            id: '1',
            email,
            name: email.split('@')[0],
            createdAt: new Date().toISOString(),
            investmentProfile: {
              totalInvested: 0,
              totalReturns: 0,
              riskTolerance: 'medium',
              preferredSectors: []
            }
          }
          
          set({
            user: mockUser,
            isAuthenticated: true,
            token: 'mock-jwt-token',
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (name: string, email: string, _password: string) => {
        set({ isLoading: true })
        try {
          // TODO: Replace with actual API call
          const mockUser: User = {
            id: Date.now().toString(),
            email,
            name,
            createdAt: new Date().toISOString(),
            investmentProfile: {
              totalInvested: 0,
              totalReturns: 0,
              riskTolerance: 'medium',
              preferredSectors: []
            }
          }
          
          set({
            user: mockUser,
            isAuthenticated: true,
            token: 'mock-jwt-token',
            isLoading: false
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
          token: null,
          isLoading: false
        })
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