import React, { useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { TrendingUp, Shield, Zap, DollarSign, MessageSquare, ArrowRight, Star, Users, Award, Check, Clock, Target, TrendingDown, Sparkles, BarChart3, Brain, Globe, Activity } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const LandingPage: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore()

  const features = [
    {
      icon: <Brain className="w-8 h-8" />,
      title: 'AI-Powered Market Analysis',
      description: 'Advanced machine learning algorithms analyze 1000+ data points to predict market movements with 85% accuracy.',
      delay: 0.1,
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50/80 via-cyan-50/60 to-blue-100/40 dark:from-blue-950/40 dark:via-cyan-950/30 dark:to-blue-900/20'
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Smart Risk Management',
      description: 'AI-driven risk assessment with real-time alerts and automatic portfolio rebalancing to protect your investments.',
      delay: 0.2,
      gradient: 'from-emerald-500 to-green-500',
      bgGradient: 'from-emerald-50/80 via-green-50/60 to-emerald-100/40 dark:from-emerald-950/40 dark:via-green-950/30 dark:to-emerald-900/20'
    },
    {
      icon: <Activity className="w-8 h-8" />,
      title: 'Real-time Market Data',
      description: 'Live streaming data from PSX with 15-second delay, including volume, price alerts, and market sentiment analysis.',
      delay: 0.3,
      gradient: 'from-amber-500 to-orange-500',
      bgGradient: 'from-amber-50/80 via-orange-50/60 to-amber-100/40 dark:from-amber-950/40 dark:via-orange-950/30 dark:to-amber-900/20'
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: 'Advanced Portfolio Analytics',
      description: 'Comprehensive portfolio tracking with performance metrics, sector analysis, and predictive insights.',
      delay: 0.4,
      gradient: 'from-purple-500 to-violet-500',
      bgGradient: 'from-purple-50/80 via-violet-50/60 to-purple-100/40 dark:from-purple-950/40 dark:via-violet-950/30 dark:to-purple-900/20'
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: 'Personalized Investment Strategies',
      description: 'Custom investment plans based on your goals, risk tolerance, and market conditions with monthly rebalancing.',
      delay: 0.5,
      gradient: 'from-rose-500 to-pink-500',
      bgGradient: 'from-rose-50/80 via-pink-50/60 to-rose-100/40 dark:from-rose-950/40 dark:via-pink-950/30 dark:to-rose-900/20'
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: '24/7 AI Investment Advisor',
      description: 'Get instant answers to investment questions, market analysis, and personalized recommendations anytime.',
      delay: 0.6,
      gradient: 'from-indigo-500 to-blue-500',
      bgGradient: 'from-indigo-50/80 via-blue-50/60 to-indigo-100/40 dark:from-indigo-950/40 dark:via-blue-950/30 dark:to-indigo-900/20'
    }
  ]

  const stats = [
    { 
      number: '25,000+', 
      label: 'Active Investors', 
      icon: <Users className="w-6 h-6" />,
      gradient: 'from-blue-500 to-cyan-500'
    },
    { 
      number: '87%', 
      label: 'Success Rate', 
      icon: <Award className="w-6 h-6" />,
      gradient: 'from-emerald-500 to-green-500'
    },
    { 
      number: '15s', 
      label: 'Data Delay', 
      icon: <Clock className="w-6 h-6" />,
      gradient: 'from-purple-500 to-violet-500'
    },
    { 
      number: '₹2.5B+', 
      label: 'Assets Managed', 
      icon: <DollarSign className="w-6 h-6" />,
      gradient: 'from-amber-500 to-orange-500'
    }
  ]

  const testimonials = [
    {
      name: 'Ahmed Khan',
      role: 'Senior Portfolio Manager',
      content: 'BullBearPK\'s AI predictions have increased my portfolio returns by 23% in just 6 months. The risk management features are game-changing.',
      rating: 5,
      avatar: 'AK',
      company: 'Karachi Investment Group'
    },
    {
      name: 'Fatima Ali',
      role: 'Retail Investor',
      content: 'As a beginner, I was overwhelmed by the stock market. BullBearPK\'s AI advisor guided me to make profitable investments worth ₹50,000.',
      rating: 5,
      avatar: 'FA',
      company: 'Individual Investor'
    },
    {
      name: 'Muhammad Hassan',
      role: 'Financial Analyst',
      content: 'The real-time data and predictive analytics are unmatched. I\'ve reduced my research time by 70% while improving decision accuracy.',
      rating: 5,
      avatar: 'MH',
      company: 'Lahore Securities'
    }
  ]

  const pricingPlans = [
    {
      name: 'Free',
      price: '₹0',
      period: '/month',
      description: 'Perfect for getting started',
      features: [
        'Basic portfolio tracking',
        'Limited AI recommendations',
        'Market data (1-hour delay)',
        'Email support'
      ],
      popular: false,
      gradient: 'from-gray-500 to-gray-600'
    },
    {
      name: 'Pro',
      price: '₹999',
      period: '/month',
      description: 'For serious investors',
      features: [
        'Advanced AI analysis',
        'Real-time market data',
        'Unlimited recommendations',
        'Portfolio rebalancing',
        'Priority support',
        'Custom alerts'
      ],
      popular: true,
      gradient: 'from-blue-500 to-indigo-500'
    },
    {
      name: 'Enterprise',
      price: '₹2,499',
      period: '/month',
      description: 'For professional traders',
      features: [
        'Everything in Pro',
        'API access',
        'Custom integrations',
        'Dedicated account manager',
        'Advanced analytics',
        'White-label solutions'
      ],
      popular: false,
      gradient: 'from-purple-500 to-violet-500'
    }
  ]

  const benefits = [
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'Higher Returns',
      description: 'Average 23% better returns compared to traditional investing methods',
      gradient: 'from-emerald-500 to-green-500',
      stat: '+23%'
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: 'Save Time',
      description: 'Reduce research time by 70% with AI-powered insights',
      gradient: 'from-blue-500 to-cyan-500',
      stat: '-70%'
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Risk Reduction',
      description: 'AI-driven risk management reduces portfolio volatility by 35%',
      gradient: 'from-purple-500 to-violet-500',
      stat: '-35%'
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: 'Smart Diversification',
      description: 'Automated portfolio optimization across 15+ sectors',
      gradient: 'from-orange-500 to-red-500',
      stat: '15+'
    }
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-900 overflow-x-hidden">
      {/* Enhanced Navigation */}
      <motion.nav 
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, type: "spring", stiffness: 100 }}
        className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
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
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">AI Investment Platform</p>
              </div>
            </motion.div>
            
            <div className="flex items-center space-x-4">
              {isAuthenticated && user ? (
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Link
                    to="/dashboard"
                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    Dashboard
                  </Link>
                </motion.div>
              ) : (
                <div className="flex items-center space-x-3">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Link
                      to="/login"
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-all duration-300 font-medium px-4 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                    >
                      Sign In
                    </Link>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Link
                      to="/register"
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl"
                    >
                      Get Started
                    </Link>
                  </motion.div>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Enhanced Hero Section */}
      <motion.section 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
        className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 overflow-hidden"
      >
        {/* Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-400/20 to-indigo-400/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className="relative text-center mb-20">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-6"
          >
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 backdrop-blur-sm rounded-full px-6 py-3 border border-blue-200/50 dark:border-blue-700/50 shadow-lg">
              <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span className="text-blue-700 dark:text-blue-300 font-semibold text-sm">AI-Powered Investment Platform</span>
            </div>
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-6xl md:text-7xl lg:text-8xl font-bold mb-8 leading-tight"
          >
            <span className="bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent">
              Smart Investing for
            </span>
            <br />
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Pakistan
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-12 max-w-4xl mx-auto leading-relaxed"
          >
            AI-powered investment platform that helps you achieve{' '}
            <span className="font-bold text-emerald-600 dark:text-emerald-400">23% better returns</span>{' '}
            with intelligent market analysis, real-time data, and personalized investment strategies for Pakistan Stock Exchange.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 mb-16"
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link 
                to="/register"
                className="px-10 py-5 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white rounded-2xl font-bold text-lg hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 transition-all duration-300 flex items-center space-x-3 group shadow-2xl hover:shadow-blue-500/25"
              >
                <span>Start Investing</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" />
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link
                to="/register"
                className="px-10 py-5 border-2 border-blue-600 text-blue-600 dark:text-blue-400 rounded-2xl font-bold text-lg hover:bg-blue-600 hover:text-white transition-all duration-300 backdrop-blur-sm shadow-xl"
              >
                Create Account
              </Link>
            </motion.div>
          </motion.div>

          {/* Enhanced Stats */}
          <motion.div 
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {stats.map((stat, index) => (
              <motion.div 
                key={index}
                className="text-center group"
                whileHover={{ scale: 1.05, y: -5 }}
                transition={{ type: "spring", stiffness: 300 }}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ transitionDelay: `${index * 0.1}s` }}
              >
                <div className={`w-16 h-16 bg-gradient-to-br ${stat.gradient} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl text-white group-hover:shadow-2xl transition-all duration-300`}>
                  {stat.icon}
                </div>
                <div className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 dark:text-gray-400 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* Enhanced Features Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 backdrop-blur-sm rounded-full px-6 py-3 border border-purple-200/50 dark:border-purple-700/50 shadow-lg mb-6">
            <Brain className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            <span className="text-purple-700 dark:text-purple-300 font-semibold text-sm">Advanced Features</span>
          </div>
          <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-purple-800 to-indigo-900 dark:from-white dark:via-purple-200 dark:to-indigo-200 bg-clip-text text-transparent mb-6">
            Why Choose BullBearPK?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
            Advanced technology meets financial expertise to deliver the best investment experience in Pakistan.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: feature.delay }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.03, y: -10 }}
              className={`relative bg-gradient-to-br ${feature.bgGradient} backdrop-blur-xl rounded-3xl p-8 border border-gray-200/50 dark:border-gray-700/50 shadow-xl hover:shadow-2xl transition-all duration-500 group overflow-hidden`}
            >
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-5">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white to-transparent rounded-full -translate-y-16 translate-x-16"></div>
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-white to-transparent rounded-full translate-y-12 -translate-x-12"></div>
              </div>

              <div className="relative z-10">
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-6 shadow-xl text-white group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 group-hover:text-gray-800 dark:group-hover:text-gray-100 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Enhanced Benefits Section */}
      <section className="relative bg-gradient-to-r from-blue-50/50 via-indigo-50/50 to-purple-50/50 dark:from-gray-800/50 dark:via-gray-900/50 dark:to-gray-800/50 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-emerald-100 to-green-100 dark:from-emerald-900/30 dark:to-green-900/30 backdrop-blur-sm rounded-full px-6 py-3 border border-emerald-200/50 dark:border-emerald-700/50 shadow-lg mb-6">
              <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <span className="text-emerald-700 dark:text-emerald-300 font-semibold text-sm">Proven Results</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-emerald-800 to-green-900 dark:from-white dark:via-emerald-200 dark:to-green-200 bg-clip-text text-transparent mb-6">
              Why BullBearPK Users Outperform the Market
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Join thousands of investors who are already achieving better returns with AI-powered insights.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="text-center group"
              >
                <div className={`w-20 h-20 bg-gradient-to-br ${benefit.gradient} rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl text-white group-hover:scale-110 transition-all duration-300 relative`}>
                  {benefit.icon}
                  <div className="absolute -top-2 -right-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
                    {benefit.stat}
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 group-hover:text-gray-800 dark:group-hover:text-gray-100 transition-colors">
                  {benefit.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {benefit.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced Pricing Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 backdrop-blur-sm rounded-full px-6 py-3 border border-blue-200/50 dark:border-blue-700/50 shadow-lg mb-6">
            <DollarSign className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-blue-700 dark:text-blue-300 font-semibold text-sm">Flexible Pricing</span>
          </div>
          <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent mb-6">
            Choose Your Plan
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
            Start free and upgrade as you grow. No hidden fees, cancel anytime.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              whileHover={{ scale: plan.popular ? 1.02 : 1.05, y: -5 }}
              className={`relative bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl p-8 border-2 shadow-xl hover:shadow-2xl transition-all duration-500 ${
                plan.popular
                  ? 'border-blue-500 scale-105 shadow-blue-500/25'
                  : 'border-gray-200/50 dark:border-gray-700/50'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-2 rounded-full text-sm font-bold shadow-lg">
                    <Sparkles className="w-4 h-4 inline mr-1" />
                    Most Popular
                  </div>
                </div>
              )}
              
              <div className="text-center mb-8">
                <div className={`w-16 h-16 bg-gradient-to-br ${plan.gradient} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl`}>
                  <DollarSign className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {plan.name}
                </h3>
                <div className="flex items-baseline justify-center mb-2">
                  <span className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                    {plan.price}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 ml-2 text-lg">
                    {plan.period}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">
                  {plan.description}
                </p>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center">
                    <div className="w-6 h-6 bg-gradient-to-br from-emerald-500 to-green-500 rounded-full flex items-center justify-center mr-3 flex-shrink-0 shadow-lg">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link
                  to="/register"
                  className={`w-full py-4 px-6 rounded-2xl font-bold text-center transition-all duration-300 shadow-lg hover:shadow-xl block ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {plan.name === 'Free' ? 'Get Started Free' : 'Start Free Trial'}
                </Link>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Enhanced Testimonials Section */}
      <section className="relative bg-gradient-to-r from-gray-50/50 via-blue-50/50 to-indigo-50/50 dark:from-gray-900/50 dark:via-blue-950/50 dark:to-indigo-950/50 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 backdrop-blur-sm rounded-full px-6 py-3 border border-yellow-200/50 dark:border-yellow-700/50 shadow-lg mb-6">
              <Star className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              <span className="text-yellow-700 dark:text-yellow-300 font-semibold text-sm">Customer Stories</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-gray-900 via-yellow-800 to-orange-900 dark:from-white dark:via-yellow-200 dark:to-orange-200 bg-clip-text text-transparent mb-6">
              What Our Users Say
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Join thousands of satisfied investors who trust BullBearPK for their financial success.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.03, y: -5 }}
                className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl p-8 border border-gray-200/50 dark:border-gray-700/50 shadow-xl hover:shadow-2xl transition-all duration-500 relative overflow-hidden"
              >
                {/* Background Pattern */}
                <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-yellow-400/10 to-orange-400/10 rounded-full -translate-y-12 translate-x-12"></div>
                
                <div className="relative z-10">
                  <div className="flex items-center mb-6">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-600 dark:text-gray-400 mb-6 italic text-lg leading-relaxed">
                    "{testimonial.content}"
                  </p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg mr-4 shadow-lg">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <p className="font-bold text-gray-900 dark:text-white text-lg">{testimonial.name}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{testimonial.role}</p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">{testimonial.company}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced CTA Section */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="relative bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-3xl p-16 text-center overflow-hidden shadow-2xl"
        >
          {/* Background Elements */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
          </div>

          <div className="relative z-10">
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
              className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-xl"
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>

            <h2 className="text-5xl md:text-6xl font-bold text-white mb-8 leading-tight">
              Start Earning 23% Better Returns Today
            </h2>
            <p className="text-xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Join 25,000+ investors who are already outperforming the market with AI-powered insights. 
              Start your free trial and see the difference in just 30 days.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 mb-8">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link 
                  to="/register"
                  className="px-10 py-5 bg-white text-blue-600 rounded-2xl font-bold text-lg hover:bg-gray-100 transition-all duration-300 flex items-center space-x-3 group shadow-2xl"
                >
                  <span>Start Free Trial</span>
                  <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" />
                </Link>
              </motion.div>
              
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  to="/register"
                  className="px-10 py-5 border-2 border-white text-white rounded-2xl font-bold text-lg hover:bg-white hover:text-blue-600 transition-all duration-300 backdrop-blur-sm"
                >
                  Explore Features
                </Link>
              </motion.div>
            </div>
            
            <p className="text-blue-200 text-sm">
              No credit card required • 30-day free trial • Cancel anytime
            </p>
          </div>
        </motion.div>
      </section>

      {/* Enhanced Footer */}
      <footer className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border-t border-gray-200/50 dark:border-gray-700/50 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <motion.div 
              className="flex items-center space-x-3 mb-6 md:mb-0"
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 rounded-2xl flex items-center justify-center shadow-xl">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 bg-clip-text text-transparent">
                  BullBearPK
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-400">AI Investment Platform</p>
              </div>
            </motion.div>
            <div className="text-gray-600 dark:text-gray-400 text-center">
              <p className="mb-2">© 2024 BullBearPK. All rights reserved.</p>
              <p className="text-sm">Empowering Pakistani investors with AI-driven insights</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
