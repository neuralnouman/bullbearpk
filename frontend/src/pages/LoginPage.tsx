import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  ArrowLeft,
  TrendingUp,
  Shield,
  Zap,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

interface LoginFormData {
  email: string
  password: string
}

interface FormErrors {
  email?: string
  password?: string
  general?: string
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, isLoading } = useAuthStore()
  
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    
    try {
      await login(formData.email, formData.password)
      toast.success('Welcome back! 🚀')
      navigate('/dashboard')
    } catch (error: any) {
      setErrors({ general: error.message || 'Invalid credentials. Please try again.' })
      toast.error('Login failed. Please check your credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Clear field-specific error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }
  }

  const handleFocus = (fieldName: string) => {
    setFocusedField(fieldName)
  }

  const handleBlur = () => {
    setFocusedField(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-900 relative overflow-hidden">
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="w-full max-w-md"
        >
          {/* Back to Home */}
          <div>
            <Link
              to="/"
              className="inline-flex items-center text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 mb-8 transition-all duration-300 hover:scale-105"
            >
              <ArrowLeft size={20} className="mr-2" />
              Back to Home
            </Link>
          </div>

          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="mb-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full mb-4">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
              BullBearPK
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Welcome back to your investment journey
            </p>
          </div>

          {/* Login Form */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Email Address
                </label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-blue-600 transition-colors duration-300" size={20} />
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    onFocus={() => handleFocus('email')}
                    onBlur={handleBlur}
                    className={`w-full pl-12 pr-4 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/20 ${
                      errors.email
                        ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                        : focusedField === 'email'
                        ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700'
                    }`}
                    placeholder="Enter your email"
                  />
                  <AnimatePresence>
                    {errors.email && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center mt-2 text-red-600 text-sm"
                      >
                        <AlertCircle size={16} className="mr-1" />
                        {errors.email}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-blue-600 transition-colors duration-300" size={20} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    onFocus={() => handleFocus('password')}
                    onBlur={handleBlur}
                    className={`w-full pl-12 pr-12 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/20 ${
                      errors.password
                        ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
                        : focusedField === 'password'
                        ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700'
                    }`}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-300"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                  <AnimatePresence>
                    {errors.password && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center mt-2 text-red-600 text-sm"
                      >
                        <AlertCircle size={16} className="mr-1" />
                        {errors.password}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>

              {/* General Error */}
              <AnimatePresence>
                {errors.general && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="flex items-center p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 text-sm"
                  >
                    <AlertCircle size={16} className="mr-2" />
                    {errors.general}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit Button */}
              <div>
                <motion.button
                  type="submit"
                  disabled={isSubmitting || isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 ${
                    isSubmitting || isLoading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isSubmitting || isLoading ? (
                    <div className="flex items-center justify-center">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                      />
                      Signing in...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <Zap size={20} className="mr-2" />
                      Sign In
                    </div>
                  )}
                </motion.button>
              </div>

              {/* Forgot Password Link */}
              <div className="text-center">
                <Link
                  to="/forgot-password"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium transition-colors duration-300"
                >
                  Forgot your password?
                </Link>
              </div>
            </form>
          </div>

          {/* Sign Up Link */}
          <div className="text-center mt-8">
            <p className="text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-semibold transition-colors duration-300 hover:underline"
              >
                Sign up here
              </Link>
            </p>
          </div>

          {/* Features Preview */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50">
              <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">AI Analysis</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Smart recommendations</p>
            </div>
            <div className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50">
              <Shield className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Secure</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Bank-level security</p>
            </div>
            <div className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50">
              <Zap className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Real-time</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Live market data</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginPage 