import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { TrendingUp, DollarSign, MessageSquare, LogOut, User, LogIn, Send, Bot, RefreshCw, Target, Shield, ArrowRight, TrendingDown, Calendar, Clock, Star, AlertCircle, CheckCircle, XCircle, Info, ChevronRight, Plus, Minus, Percent, Zap, Globe, PlusCircle, FileText, Sparkles, Activity } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { sendChatMessage, ChatMessage as AIChatMessage } from '../services/aiAssistantService'

interface ChatMessage {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

interface PortfolioItem {
  symbol: string
  name: string
  quantity: number
  avgPrice: number
  currentPrice: number
  change: number
  changePercent: number
}

interface RecentActivity {
  id: string
  type: 'buy' | 'sell' | 'dividend' | 'alert'
  symbol: string
  amount: number
  timestamp: Date
  status: 'completed' | 'pending' | 'failed'
}

const Dashboard: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI investment assistant powered by Groq. How can I help you with your Pakistani stock market investments today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [newMessage, setNewMessage] = useState('')
  const [showChat, setShowChat] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview'>('overview')
  const [isTyping, setIsTyping] = useState(false)

  // User data - only show if authenticated
  const userPortfolio = user?.portfolio || {
    cashBalance: 0,
    totalInvested: 0,
    totalReturn: 0,
    returnPercent: 0
  }

  const userProfile = user ? {
    name: user.name,
    riskTolerance: user.riskTolerance,
    investmentGoal: user.investmentGoal,
    lastLogin: new Date()
  } : null

  const dashboardCards = [
    {
      title: 'Investment Form',
      description: 'Get AI-powered investment recommendations',
      icon: <TrendingUp className="w-8 h-8" />,
      link: '/investment-form',
      color: 'from-blue-500 via-blue-600 to-blue-700',
      bgColor: 'bg-gradient-to-br from-blue-50/80 via-blue-100/60 to-blue-200/40 dark:from-blue-950/40 dark:via-blue-900/30 dark:to-blue-800/20',
      borderColor: 'border-blue-200/60 dark:border-blue-700/50',
      iconBg: 'bg-gradient-to-br from-blue-500 to-blue-600',
      stats: '12 recommendations'
    },
    {
      title: 'Market Data',
      description: 'Real-time PSX market information',
      icon: <Globe className="w-8 h-8" />,
      link: '/market-data',
      color: 'from-emerald-500 via-emerald-600 to-emerald-700',
      bgColor: 'bg-gradient-to-br from-emerald-50/80 via-emerald-100/60 to-emerald-200/40 dark:from-emerald-950/40 dark:via-emerald-900/30 dark:to-emerald-800/20',
      borderColor: 'border-emerald-200/60 dark:border-emerald-700/50',
      iconBg: 'bg-gradient-to-br from-emerald-500 to-emerald-600',
      stats: 'Live updates'
    },
    {
      title: 'Portfolio',
      description: 'Track your investments and performance',
      icon: <DollarSign className="w-8 h-8" />,
      link: '/portfolio',
      color: 'from-purple-500 via-purple-600 to-purple-700',
      bgColor: 'bg-gradient-to-br from-purple-50/80 via-purple-100/60 to-purple-200/40 dark:from-purple-950/40 dark:via-purple-900/30 dark:to-purple-800/20',
      borderColor: 'border-purple-200/60 dark:border-purple-700/50',
      iconBg: 'bg-gradient-to-br from-purple-500 to-purple-600',
      stats: '5 holdings'
    },
    {
      title: 'AI Assistant',
      description: 'Get personalized investment advice',
      icon: <Bot className="w-8 h-8" />,
      link: '#',
      color: 'from-orange-500 via-orange-600 to-orange-700',
      bgColor: 'bg-gradient-to-br from-orange-50/80 via-orange-100/60 to-orange-200/40 dark:from-orange-950/40 dark:via-orange-900/30 dark:to-orange-800/20',
      borderColor: 'border-orange-200/60 dark:border-orange-700/50',
      iconBg: 'bg-gradient-to-br from-orange-500 to-orange-600',
      stats: 'Always available',
      onClick: () => setShowChat(true)
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15
      }
    }
  }

  const cardHoverVariants = {
    hover: { 
      scale: 1.03, 
      y: -8,
      transition: {
        type: "spring",
        stiffness: 400,
        damping: 25
      }
    },
    tap: { scale: 0.97 }
  }

  const handleLogout = async () => {
    setIsLoading(true)
    try {
      await logout()
      toast.success('Logged out successfully', {
        style: {
          background: 'linear-gradient(135deg, #10b981, #059669)',
          color: 'white',
          borderRadius: '12px',
          padding: '16px',
          fontWeight: '500'
        }
      })
      navigate('/login')
    } catch (error) {
      console.error('Logout error:', error)
      toast.error('Logout failed', {
        style: {
          background: 'linear-gradient(135deg, #ef4444, #dc2626)',
          color: 'white',
          borderRadius: '12px',
          padding: '16px',
          fontWeight: '500'
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !user?.id) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setIsTyping(true)

    try {
      const aiChatHistory: AIChatMessage[] = chatMessages
        .map(msg => ({
          id: msg.id,
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text,
          timestamp: msg.timestamp.toISOString()
        }))

      const response = await sendChatMessage(newMessage, user.id, aiChatHistory)

      setIsTyping(false)
      setChatMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: response.message,
        sender: 'bot',
        timestamp: new Date()
      }])
    } catch (error: any) {
      setIsTyping(false)
      setChatMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      }])
      toast.error('Failed to get AI response. Please try again.', {
        style: {
          background: 'linear-gradient(135deg, #ef4444, #dc2626)',
          color: 'white',
          borderRadius: '12px',
          padding: '16px',
          fontWeight: '500'
        }
      })
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    setTimeout(() => {
      setIsRefreshing(false)
      toast.success('Dashboard refreshed!', {
        style: {
          background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
          color: 'white',
          borderRadius: '12px',
          padding: '16px',
          fontWeight: '500'
        }
      })
    }, 1200)
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60)
      return `${hours}h ago`
    } else {
      const days = Math.floor(diffInMinutes / 1440)
      return `${days}d ago`
    }
  }

  // If not authenticated, show login prompt
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 100, damping: 20 }}
          className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl p-10 border border-gray-200/50 dark:border-gray-700/50 shadow-2xl max-w-lg w-full"
        >
          <div className="text-center">
            <motion.div 
              className="w-20 h-20 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <TrendingUp className="w-10 h-10 text-white" />
            </motion.div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent mb-4">
              Welcome to BullBearPK
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg leading-relaxed">
              Please sign in to access your personalized dashboard and investment portfolio.
            </p>
            <div className="space-y-4">
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link
                  to="/login"
                  className="w-full bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-300 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 shadow-xl hover:shadow-2xl flex items-center justify-center space-x-3 group"
                >
                  <LogIn className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span>Sign In</span>
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link
                  to="/register"
                  className="w-full border-2 border-blue-600 text-blue-600 dark:text-blue-400 px-8 py-4 rounded-2xl font-semibold transition-all duration-300 hover:bg-blue-600 hover:text-white hover:shadow-xl flex items-center justify-center space-x-3 group backdrop-blur-sm"
                >
                  <PlusCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span>Create Account</span>
                </Link>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-900">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <motion.div 
                className="flex items-center space-x-3"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 rounded-2xl flex items-center justify-center shadow-xl">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 bg-clip-text text-transparent">
                    BullBearPK
                  </h1>
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Investment Platform</p>
                </div>
              </motion.div>
            </div>
            
            <div className="flex items-center space-x-4">
              <motion.button 
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-all duration-300 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 shadow-md hover:shadow-lg"
                whileHover={{ scale: 1.1, rotate: 180 }}
                whileTap={{ scale: 0.9 }}
                title="Refresh Dashboard"
              >
                <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              </motion.button>
              
              <motion.div 
                className="flex items-center space-x-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-2xl px-4 py-3 shadow-lg"
                whileHover={{ scale: 1.02 }}
              >
                <div className="w-10 h-10 bg-gradient-to-br from-purple-600 via-purple-700 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    {userProfile?.name || 'User'}
                  </span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                      Premium User
                    </span>
                  </div>
                </div>
              </motion.div>
              
              <motion.button
                onClick={handleLogout}
                disabled={isLoading}
                className="flex items-center space-x-2 px-5 py-3 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-all duration-300 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 shadow-md hover:shadow-lg font-medium"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm">Logout</span>
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.main 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10"
      >
        {/* Welcome Section */}
        <motion.div variants={itemVariants} className="mb-10">
          <div className="flex items-center justify-between">
            <div>
              <motion.h2 
                className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent mb-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                Welcome back, {userProfile?.name}! 
                <motion.span 
                  className="inline-block ml-2"
                  animate={{ rotate: [0, 14, -8, 14, -4, 10, 0] }}
                  transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                >
                  👋
                </motion.span>
              </motion.h2>
              <motion.p 
                className="text-gray-600 dark:text-gray-400 text-lg"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                Start building your investment portfolio today with AI-powered insights.
              </motion.p>
            </div>
            <motion.div 
              className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl px-4 py-2 shadow-lg"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Clock className="w-4 h-4" />
              <span>Last updated {formatTimeAgo(userProfile?.lastLogin || new Date())}</span>
            </motion.div>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <motion.div variants={itemVariants} className="mb-8">
          <div className="flex space-x-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-2 shadow-xl border border-gray-200/50 dark:border-gray-700/50">
            {[
              { id: 'overview', label: 'Overview', icon: <TrendingUp className="w-4 h-4" /> }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.3, type: "spring", stiffness: 100 }}
              className="space-y-8"
            >
              {/* Dashboard Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {dashboardCards.map((card, index) => (
                  <motion.div
                    key={index}
                    variants={cardHoverVariants}
                    whileHover="hover"
                    whileTap="tap"
                    className={`${card.bgColor} backdrop-blur-xl rounded-3xl p-8 border ${card.borderColor} transition-all duration-500 cursor-pointer shadow-xl hover:shadow-2xl group relative overflow-hidden`}
                    onClick={card.onClick}
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
                  >
                    {/* Background Pattern */}
                    <div className="absolute inset-0 opacity-5">
                      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white to-transparent rounded-full -translate-y-16 translate-x-16"></div>
                      <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-white to-transparent rounded-full translate-y-12 -translate-x-12"></div>
                    </div>
                    
                    {card.onClick ? (
                      <div className="block relative z-10">
                        <div className="flex items-center justify-between mb-6">
                          <div className={`w-16 h-16 ${card.iconBg} rounded-2xl flex items-center justify-center shadow-xl text-white group-hover:scale-110 transition-transform duration-300`}>
                            {card.icon}
                          </div>
                          <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                            <ArrowRight className="w-5 h-5 text-gray-700 dark:text-gray-300 group-hover:translate-x-1 transition-transform" />
                          </div>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-gray-800 dark:group-hover:text-gray-100 transition-colors">
                          {card.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                          {card.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">{card.stats}</span>
                        </div>
                      </div>
                    ) : (
                      <Link to={card.link} className="block relative z-10">
                        <div className="flex items-center justify-between mb-6">
                          <div className={`w-16 h-16 ${card.iconBg} rounded-2xl flex items-center justify-center shadow-xl text-white group-hover:scale-110 transition-transform duration-300`}>
                            {card.icon}
                          </div>
                          <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                            <ArrowRight className="w-5 h-5 text-gray-700 dark:text-gray-300 group-hover:translate-x-1 transition-transform" />
                          </div>
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-gray-800 dark:group-hover:text-gray-100 transition-colors">
                          {card.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                          {card.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">{card.stats}</span>
                        </div>
                      </Link>
                    )}
                  </motion.div>
                ))}
              </div>

              {/* Quick Actions */}
              <motion.div 
                className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl p-8 border border-gray-200/50 dark:border-gray-700/50 shadow-2xl"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <div className="flex items-center space-x-3 mb-8">
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                      Quick Actions
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Get started with these popular features</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <motion.button
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                    className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-300 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 shadow-xl hover:shadow-2xl flex items-center justify-center space-x-3 group"
                    onClick={() => navigate('/investment-form')}
                  >
                    <Zap className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    <span>Get Recommendations</span>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                    className="bg-gradient-to-r from-emerald-600 via-emerald-700 to-green-700 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-300 hover:from-emerald-700 hover:via-emerald-800 hover:to-green-800 shadow-xl hover:shadow-2xl flex items-center justify-center space-x-3 group"
                    onClick={() => navigate('/market-data')}
                  >
                    <Activity className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    <span>Market Data</span>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.03, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                    className="bg-gradient-to-r from-purple-600 via-purple-700 to-pink-700 text-white px-8 py-4 rounded-2xl font-semibold transition-all duration-300 hover:from-purple-700 hover:via-purple-800 hover:to-pink-800 shadow-xl hover:shadow-2xl flex items-center justify-center space-x-3 group"
                    onClick={() => navigate('/portfolio')}
                  >
                    <DollarSign className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    <span>View Portfolio</span>
                  </motion.button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.main>

      {/* Enhanced Chat Modal */}
      <AnimatePresence>
        {showChat && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4"
            onClick={() => setShowChat(false)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0, y: 50 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 50 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl shadow-2xl w-full max-w-lg h-[600px] flex flex-col border border-gray-200/50 dark:border-gray-700/50"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Enhanced Chat Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200/50 dark:border-gray-700/50">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-lg">AI Investment Assistant</h3>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Online • Ready to help</p>
                    </div>
                  </div>
                </div>
                <motion.button
                  onClick={() => setShowChat(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <XCircle className="w-6 h-6" />
                </motion.button>
              </div>

              {/* Enhanced Chat Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
                {chatMessages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-end space-x-2 max-w-xs ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
                        message.sender === 'user' 
                          ? 'bg-gradient-to-br from-blue-600 to-indigo-600' 
                          : 'bg-gradient-to-br from-gray-600 to-gray-700'
                      }`}>
                        {message.sender === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <div
                        className={`px-4 py-3 rounded-2xl shadow-lg ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{message.text}</p>
                        <p className={`text-xs mt-1 ${
                          message.sender === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                        }`}>
                          {formatTimeAgo(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
                
                {/* Typing Indicator */}
                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="flex items-end space-x-2 max-w-xs">
                      <div className="w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center shadow-lg">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-700 px-4 py-3 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-600">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Enhanced Chat Input */}
              <div className="p-6 border-t border-gray-200/50 dark:border-gray-700/50">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask about investments..."
                    className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 shadow-lg backdrop-blur-sm transition-all duration-200"
                  />
                  <motion.button
                    onClick={handleSendMessage}
                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl font-medium"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!newMessage.trim() || isTyping}
                  >
                    <Send className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Dashboard
