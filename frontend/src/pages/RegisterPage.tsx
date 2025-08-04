import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  ArrowLeft, 
  TrendingUp, 
  Shield, 
  Zap,
  CheckCircle,
  AlertCircle,
  Target,
  BarChart3
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

interface RegisterFormData {
  name: string
  email: string
  password: string
  confirmPassword: string
  riskTolerance: 'low' | 'moderate' | 'high'
  investmentGoal: string
  preferredSectors: string[]
}

interface FormErrors {
  name?: string
  email?: string
  password?: string
  confirmPassword?: string
  riskTolerance?: string
  investmentGoal?: string
  general?: string
}

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading } = useAuthStore()
  
  const [formData, setFormData] = useState<RegisterFormData>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    riskTolerance: 'moderate',
    investmentGoal: 'growth',
    preferredSectors: []
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState(1)
  const [progress, setProgress] = useState(0)

  // Floating particles effect
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, size: number, speed: number}>>([])

  useEffect(() => {
    // Generate floating particles
    const newParticles = Array.from({ length: 25 }, (_, i) => ({
      id: i,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      size: Math.random() * 4 + 1,
      speed: Math.random() * 2 + 0.5
    }))
    setParticles(newParticles)

    // Animate particles
    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        y: particle.y - particle.speed,
        x: particle.x + Math.sin(particle.y / 100) * 0.5
      })))
    }, 50)

    return () => clearInterval(interval)
  }, [])

  // Update progress based on form completion
  useEffect(() => {
    const completedFields = Object.values(formData).filter(value => 
      value !== '' && value !== 'moderate' && value !== 'growth' && value.length > 0
    ).length
    const totalFields = 7
    setProgress((completedFields / totalFields) * 100)
  }, [formData])

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = 'Full name is required'
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters'
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number'
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }
    
    if (!formData.riskTolerance) {
      newErrors.riskTolerance = 'Please select your risk tolerance'
    }
    
    if (!formData.investmentGoal) {
      newErrors.investmentGoal = 'Please select your investment goal'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    
    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        riskTolerance: formData.riskTolerance,
        investmentGoal: formData.investmentGoal,
        preferredSectors: formData.preferredSectors
      })
      toast.success('Account created successfully! 🎉')
      navigate('/dashboard')
    } catch (error: any) {
      setErrors({ general: error.message || 'Registration failed. Please try again.' })
      toast.error('Registration failed. Please check your information.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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

  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.8,
        staggerChildren: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.6 }
    }
  }

  const inputVariants = {
    unfocused: { scale: 1 },
    focused: { scale: 1.02 }
  }

  const riskToleranceOptions = [
    { value: 'low', label: 'Conservative', description: 'Stable returns, lower risk' },
    { value: 'moderate', label: 'Balanced', description: 'Moderate risk and returns' },
    { value: 'high', label: 'Aggressive', description: 'Higher potential returns' }
  ]

  const investmentGoalOptions = [
    { value: 'growth', label: 'Growth', description: 'Long-term capital appreciation' },
    { value: 'income', label: 'Income', description: 'Regular dividend income' },
    { value: 'balanced', label: 'Balanced', description: 'Growth and income combined' },
    { value: 'preservation', label: 'Capital Preservation', description: 'Protect your capital' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-950 dark:to-indigo-900 relative overflow-hidden">
      {/* Floating Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {particles.map(particle => (
          <motion.div
            key={particle.id}
            className="absolute w-1 h-1 bg-purple-400/20 rounded-full"
            style={{
              left: particle.x,
              top: particle.y,
              width: particle.size,
              height: particle.size
            }}
            animate={{
              y: [0, -100],
              opacity: [0.3, 0, 0.3],
              scale: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 3 + particle.speed,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="w-full max-w-2xl"
        >
          {/* Back to Home */}
          <motion.div variants={itemVariants}>
            <Link 
              to="/" 
              className="inline-flex items-center text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 mb-8 transition-all duration-300 hover:scale-105"
            >
              <ArrowLeft size={20} className="mr-2" />
              Back to Home
            </Link>
          </motion.div>

          {/* Logo and Title */}
          <motion.div variants={itemVariants} className="text-center mb-8">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="mb-4"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full mb-4">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent mb-2">
              Join BullBearPK
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Start your investment journey with AI-powered insights
            </p>
          </motion.div>

          {/* Progress Bar */}
          <motion.div variants={itemVariants} className="mb-8">
            <div className="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-white/20 dark:border-gray-700/50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Profile Completion</span>
                <span className="text-sm font-bold text-purple-600">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <motion.div
                  className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                />
              </div>
            </div>
          </motion.div>

          {/* Registration Form */}
          <motion.div 
            variants={itemVariants}
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 p-8"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <motion.div variants={itemVariants}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <User className="w-5 h-5 mr-2 text-purple-600" />
                  Personal Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Name Field */}
                  <div>
                    <label htmlFor="name" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Full Name
                    </label>
                    <motion.div
                      variants={inputVariants}
                      animate={focusedField === 'name' ? 'focused' : 'unfocused'}
                      className="relative group"
                    >
                      <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-600 transition-colors duration-300" size={20} />
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        onFocus={() => handleFocus('name')}
                        onBlur={handleBlur}
                        className={`w-full pl-12 pr-4 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-500/20 ${
                          errors.name 
                            ? 'border-red-300 bg-red-50 dark:bg-red-900/20' 
                            : focusedField === 'name'
                            ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700'
                        }`}
                        placeholder="Enter your full name"
                      />
                      <AnimatePresence>
                        {errors.name && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex items-center mt-2 text-red-600 text-sm"
                          >
                            <AlertCircle size={16} className="mr-1" />
                            {errors.name}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </div>

                  {/* Email Field */}
                  <div>
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Email Address
                    </label>
                    <motion.div
                      variants={inputVariants}
                      animate={focusedField === 'email' ? 'focused' : 'unfocused'}
                      className="relative group"
                    >
                      <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-600 transition-colors duration-300" size={20} />
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        onFocus={() => handleFocus('email')}
                        onBlur={handleBlur}
                        className={`w-full pl-12 pr-4 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-500/20 ${
                          errors.email 
                            ? 'border-red-300 bg-red-50 dark:bg-red-900/20' 
                            : focusedField === 'email'
                            ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
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
                    </motion.div>
                  </div>
                </div>
              </motion.div>

              {/* Security Information */}
              <motion.div variants={itemVariants}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-purple-600" />
                  Security
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Password Field */}
                  <div>
                    <label htmlFor="password" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Password
                    </label>
                    <motion.div
                      variants={inputVariants}
                      animate={focusedField === 'password' ? 'focused' : 'unfocused'}
                      className="relative group"
                    >
                      <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-600 transition-colors duration-300" size={20} />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        onFocus={() => handleFocus('password')}
                        onBlur={handleBlur}
                        className={`w-full pl-12 pr-12 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-500/20 ${
                          errors.password 
                            ? 'border-red-300 bg-red-50 dark:bg-red-900/20' 
                            : focusedField === 'password'
                            ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700'
                        }`}
                        placeholder="Create a strong password"
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
                    </motion.div>
                  </div>

                  {/* Confirm Password Field */}
                  <div>
                    <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Confirm Password
                    </label>
                    <motion.div
                      variants={inputVariants}
                      animate={focusedField === 'confirmPassword' ? 'focused' : 'unfocused'}
                      className="relative group"
                    >
                      <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-purple-600 transition-colors duration-300" size={20} />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        onFocus={() => handleFocus('confirmPassword')}
                        onBlur={handleBlur}
                        className={`w-full pl-12 pr-12 py-4 border-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-500/20 ${
                          errors.confirmPassword 
                            ? 'border-red-300 bg-red-50 dark:bg-red-900/20' 
                            : focusedField === 'confirmPassword'
                            ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                            : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700'
                        }`}
                        placeholder="Confirm your password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-300"
                      >
                        {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                      <AnimatePresence>
                        {errors.confirmPassword && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex items-center mt-2 text-red-600 text-sm"
                          >
                            <AlertCircle size={16} className="mr-1" />
                            {errors.confirmPassword}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </div>
                </div>
              </motion.div>

              {/* Investment Preferences */}
              <motion.div variants={itemVariants}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-purple-600" />
                  Investment Preferences
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Risk Tolerance */}
                  <div>
                    <label htmlFor="riskTolerance" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Risk Tolerance
                    </label>
                    <div className="space-y-3">
                      {riskToleranceOptions.map((option) => (
                        <motion.label
                          key={option.value}
                          whileHover={{ scale: 1.02 }}
                          className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-300 ${
                            formData.riskTolerance === option.value
                              ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                              : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name="riskTolerance"
                            value={option.value}
                            checked={formData.riskTolerance === option.value}
                            onChange={handleInputChange}
                            className="sr-only"
                          />
                          <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                            formData.riskTolerance === option.value
                              ? 'border-purple-600 bg-purple-600'
                              : 'border-gray-300'
                          }`}>
                            {formData.riskTolerance === option.value && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-2 h-2 bg-white rounded-full m-0.5"
                              />
                            )}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{option.description}</div>
                          </div>
                        </motion.label>
                      ))}
                    </div>
                  </div>

                  {/* Investment Goal */}
                  <div>
                    <label htmlFor="investmentGoal" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                      Investment Goal
                    </label>
                    <div className="space-y-3">
                      {investmentGoalOptions.map((option) => (
                        <motion.label
                          key={option.value}
                          whileHover={{ scale: 1.02 }}
                          className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all duration-300 ${
                            formData.investmentGoal === option.value
                              ? 'border-purple-400 bg-purple-50 dark:bg-purple-900/20'
                              : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name="investmentGoal"
                            value={option.value}
                            checked={formData.investmentGoal === option.value}
                            onChange={handleInputChange}
                            className="sr-only"
                          />
                          <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                            formData.investmentGoal === option.value
                              ? 'border-purple-600 bg-purple-600'
                              : 'border-gray-300'
                          }`}>
                            {formData.investmentGoal === option.value && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="w-2 h-2 bg-white rounded-full m-0.5"
                              />
                            )}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900 dark:text-white">{option.label}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{option.description}</div>
                          </div>
                        </motion.label>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>

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
              <motion.div variants={itemVariants}>
                <motion.button
                  type="submit"
                  disabled={isSubmitting || isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-300 ${
                    isSubmitting || isLoading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isSubmitting || isLoading ? (
                    <div className="flex items-center justify-center">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                      />
                      Creating account...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <CheckCircle size={20} className="mr-2" />
                      Create Account
                    </div>
                  )}
                </motion.button>
              </motion.div>
            </form>
          </motion.div>

          {/* Sign In Link */}
          <motion.div variants={itemVariants} className="text-center mt-8">
            <p className="text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-semibold transition-colors duration-300 hover:underline"
              >
                Sign in here
              </Link>
            </p>
          </motion.div>

          {/* Features Preview */}
          <motion.div 
            variants={itemVariants}
            className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center"
          >
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50"
            >
              <TrendingUp className="w-6 h-6 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">AI Analysis</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Smart recommendations</p>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50"
            >
              <BarChart3 className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Portfolio Tracking</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Real-time monitoring</p>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl border border-white/20 dark:border-gray-700/50"
            >
              <Zap className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
              <h3 className="font-semibold text-sm">Market Data</h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">Live PSX updates</p>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default RegisterPage 