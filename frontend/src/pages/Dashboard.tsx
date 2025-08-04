import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { 
  TrendingUp, 
  DollarSign, 
  BarChart3, 
  MessageSquare, 
  LogOut,
  User,
  Settings,
  Bell,
  LogIn,
  Send,
  Bot,
  User as UserIcon
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

interface ChatMessage {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

const Dashboard: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI investment assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [newMessage, setNewMessage] = useState('')
  const [showChat, setShowChat] = useState(false)

  // Debug logging
  useEffect(() => {
    console.log('🏠 Dashboard Debug:', {
      user: user?.name,
      userId: user?.id,
      portfolio: user?.portfolio,
      isAuthenticated
    })
  }, [user, isAuthenticated])

  const handleLogout = async () => {
    setIsLoading(true)
    try {
      await logout()
      toast.success('Logged out successfully')
      navigate('/login')
    } catch (error) {
      console.error('Logout error:', error)
      toast.error('Logout failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = () => {
    if (!newMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setNewMessage('')

    // Simulate bot response
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Thank you for your message! I\'m here to help with your investment decisions. What specific stocks or market trends would you like to discuss?',
        sender: 'bot',
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, botResponse])
    }, 1000)
  }

  // Demo data for non-authenticated users
  const demoUser = {
    name: 'Demo User',
    portfolio: {
      totalValue: 150000,
      cashBalance: 25000,
      totalInvested: 125000
    },
    riskTolerance: 'moderate',
    investmentGoal: 'growth'
  }

  const currentUser = user || demoUser
  const isDemoMode = !isAuthenticated || !user

  const dashboardCards = [
    {
      title: 'Investment Form',
      description: 'Get AI-powered investment recommendations',
      icon: <TrendingUp className="w-8 h-8 text-blue-600" />,
      link: '/investment-form',
      color: 'bg-blue-50 border-blue-200 hover:bg-blue-100'
    },
    {
      title: 'Market Data',
      description: 'Real-time PSX market information',
      icon: <BarChart3 className="w-8 h-8 text-green-600" />,
      link: '/market-data',
      color: 'bg-green-50 border-green-200 hover:bg-green-100'
    },
    {
      title: 'Portfolio',
      description: 'Track your investments and performance',
      icon: <DollarSign className="w-8 h-8 text-purple-600" />,
      link: '/portfolio',
      color: 'bg-purple-50 border-purple-200 hover:bg-purple-100'
    },
    {
      title: 'Chat Assistant',
      description: 'Get personalized investment advice',
      icon: <MessageSquare className="w-8 h-8 text-orange-600" />,
      link: '#',
      color: 'bg-orange-50 border-orange-200 hover:bg-orange-100',
      onClick: () => setShowChat(true)
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  console.log('🎯 Dashboard: Rendering dashboard for user:', currentUser.name)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-blue-950">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  BullBearPK
                </h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                <Bell className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                <Settings className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {currentUser?.name || 'User'}
                </span>
                {isDemoMode && (
                  <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                    Demo
                  </span>
                )}
              </div>
              {isAuthenticated && user ? (
                <button
                  onClick={handleLogout}
                  disabled={isLoading}
                  className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-medium">Logout</span>
                </button>
              ) : (
                <Link
                  to="/login"
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  <span className="text-sm font-medium">Login</span>
                </Link>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Demo Mode Banner */}
      {isDemoMode && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-center space-x-2 text-yellow-800 dark:text-yellow-200">
              <div className="w-4 h-4 bg-yellow-400 rounded-full"></div>
              <span className="text-sm font-medium">
                Demo Mode - Sign in to access your personal data and save preferences
              </span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Main Content */}
      <motion.main 
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
      >
        {/* Welcome Section */}
        <motion.div variants={itemVariants} className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back, {currentUser?.name}! 👋
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Ready to make smart investment decisions? Choose your next step below.
          </p>
        </motion.div>

        {/* User Stats */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Portfolio Value</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ₨{currentUser?.portfolio?.totalValue?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cash Balance</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  ₨{currentUser?.portfolio?.cashBalance?.toLocaleString() || '10,000'}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Risk Profile</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
                  {currentUser?.riskTolerance || 'Moderate'}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Investment Goal</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
                  {currentUser?.investmentGoal || 'Growth'}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Dashboard Cards */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {dashboardCards.map((card, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`${card.color} dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-6 border transition-all duration-300 cursor-pointer`}
              onClick={card.onClick}
            >
              {card.onClick ? (
                <div className="block">
                  <div className="flex items-center justify-between mb-4">
                    {card.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {card.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {card.description}
                  </p>
                </div>
              ) : (
                <Link to={card.link} className="block">
                  <div className="flex items-center justify-between mb-4">
                    {card.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {card.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {card.description}
                  </p>
                </Link>
              )}
            </motion.div>
          ))}
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="mt-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 hover:from-blue-700 hover:to-indigo-700"
              onClick={() => navigate('/investment-form')}
            >
              Get Investment Recommendations
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 hover:from-green-700 hover:to-emerald-700"
              onClick={() => navigate('/market-data')}
            >
              View Market Data
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 hover:from-purple-700 hover:to-pink-700"
              onClick={() => navigate('/portfolio')}
            >
              Check Portfolio
            </motion.button>
          </div>
        </motion.div>
      </motion.main>

      {/* Chat Modal */}
      {showChat && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowChat(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md h-96 flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Chat Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2">
                <Bot className="w-6 h-6 text-blue-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">AI Investment Assistant</h3>
              </div>
              <button
                onClick={() => setShowChat(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                ✕
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about investments..."
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <button
                  onClick={handleSendMessage}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}

export default Dashboard