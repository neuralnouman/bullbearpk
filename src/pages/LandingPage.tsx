import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { 
  TrendingUp, 
  Brain, 
  Shield, 
  Zap, 
  BarChart3, 
  NewspaperIcon,
  Users,
  Target,
  Award,
  ChevronRight,
  Sun,
  Moon,
  Star,
  ArrowRight,
  Play,
  Sparkles,
  Rocket,
  Building2,
  Clock
} from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

const AnimatedCounter = ({ end, duration = 2 }: { end: number; duration?: number }) => {
  const [count, setCount] = useState(0)
  
  useEffect(() => {
    let startTime: number
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = (timestamp - startTime) / (duration * 1000)
      
      if (progress < 1) {
        setCount(Math.floor(end * progress))
        requestAnimationFrame(animate)
      } else {
        setCount(end)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration])
  
  return <span>{count}</span>
}

const FloatingElements = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Floating geometric shapes */}
      <motion.div
        className="absolute top-20 left-10 w-4 h-4 bg-primary-400/20 rounded-full"
        animate={{
          y: [0, -20, 0],
          opacity: [0.3, 0.8, 0.3],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute top-32 right-20 w-6 h-6 bg-emerald-400/20 rotate-45"
        animate={{
          y: [0, 15, 0],
          rotate: [45, 90, 45],
          opacity: [0.2, 0.6, 0.2],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-40 left-32 w-3 h-3 bg-purple-400/30 rounded-full"
        animate={{
          x: [0, 10, 0],
          y: [0, -10, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  )
}

const LandingPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>
        <FloatingElements />
      </div>

      {/* Navigation */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="fixed top-0 w-full bg-white/95 dark:bg-gray-900/90 backdrop-blur-xl z-50 border-b border-gray-200 dark:border-gray-700"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <motion.div 
              className="flex items-center"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <Sparkles className="w-8 h-8 text-primary-400 mr-2" />
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                BullBearPK
              </span>
            </motion.div>
            
            <div className="hidden md:flex items-center space-x-8">
              {['Features', 'About', 'Team'].map((item, index) => (
                <motion.a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-all duration-300 relative group font-medium"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 + 0.5 }}
                  whileHover={{ y: -2 }}
                >
                  {item}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-primary-500 to-blue-500 group-hover:w-full transition-all duration-300"></span>
                </motion.a>
              ))}
              
              <motion.button
                onClick={toggleTheme}
                className="p-2 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-300"
                whileHover={{ scale: 1.1, rotate: 180 }}
                whileTap={{ scale: 0.9 }}
              >
                {theme === 'light' ? <Moon size={20} className="text-gray-700" /> : <Sun size={20} className="text-gray-300" />}
              </motion.button>
              
              <motion.div className="flex items-center space-x-3">
                <Link 
                  to="/login" 
                  className="px-6 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-all duration-300 font-medium"
                >
                  Login
                </Link>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Link 
                    to="/register" 
                    className="px-6 py-3 bg-gradient-to-r from-primary-500 to-blue-500 text-white rounded-xl font-medium shadow-lg hover:shadow-primary-500/25 transition-all duration-300 border border-primary-400/50"
                  >
                    Get Started
                  </Link>
                </motion.div>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 min-h-screen flex items-center">
        <div className="max-w-7xl mx-auto w-full">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="text-center lg:text-left"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.8 }}
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-primary-500/10 to-blue-500/10 rounded-full border border-primary-400/20 mb-6"
              >
                <Rocket className="w-4 h-4 text-primary-400 mr-2" />
                <span className="text-sm text-primary-300 font-medium">AI-Powered Investment Platform</span>
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.8 }}
                className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
              >
                <span className="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-700 dark:from-white dark:via-gray-100 dark:to-blue-200 bg-clip-text text-transparent">
                  Smart Investing
                </span>
                <br />
                <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                  Made Simple
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.8 }}
                className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl leading-relaxed"
              >
                Navigate Pakistan Stock Exchange with confidence using our advanced AI analysis, 
                real-time market insights, and personalized investment recommendations.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.8 }}
                className="flex flex-col sm:flex-row gap-4 mb-12"
              >
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Link 
                    to="/register" 
                    className="group inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-blue-500 text-white rounded-xl font-semibold shadow-2xl hover:shadow-primary-500/25 transition-all duration-300 border border-primary-400/50"
                  >
                    Start Investing Today
                    <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </motion.div>
                
                <motion.div
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <button className="group inline-flex items-center px-8 py-4 bg-white/10 dark:bg-gray-700/50 text-white rounded-xl font-semibold backdrop-blur-sm border border-white/20 dark:border-gray-600 hover:bg-white/20 dark:hover:bg-gray-600/50 transition-all duration-300">
                    <Play className="mr-2 w-5 h-5" />
                    Watch Demo
                  </button>
                </motion.div>
              </motion.div>

              {/* Trust Indicators */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1, duration: 0.8 }}
                className="flex items-center justify-center lg:justify-start space-x-6"
              >
                <div className="flex items-center space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                  <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">5.0 Rating</span>
                </div>
                <div className="text-gray-500 dark:text-gray-400 text-sm">
                  Trusted by 10,000+ investors
                </div>
              </motion.div>
            </motion.div>

            {/* Right Content - Dashboard Preview */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6, duration: 1 }}
              className="relative"
            >
              <div className="relative">
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-blue-500/20 rounded-3xl blur-3xl"></div>
                
                {/* Dashboard Mock */}
                <motion.div
                  className="relative bg-white/95 dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl border border-gray-200 dark:border-gray-700 p-8 shadow-2xl dark:shadow-gray-900/50"
                  whileHover={{ y: -10 }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                  {/* Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <div className="text-gray-500 dark:text-gray-400 text-sm">BullBearPK Dashboard</div>
                  </div>

                  {/* Content */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Portfolio Value</span>
                      <span className="text-2xl font-bold text-green-400">₨2,45,000</span>
                    </div>
                    
                    <div className="h-32 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-lg flex items-end space-x-2 p-4">
                      {[...Array(7)].map((_, i) => (
                        <motion.div
                          key={i}
                          className="bg-gradient-to-t from-primary-500 to-blue-400 rounded-sm flex-1"
                          style={{ height: `${Math.random() * 80 + 20}%` }}
                          initial={{ height: 0 }}
                          animate={{ height: `${Math.random() * 80 + 20}%` }}
                          transition={{ delay: i * 0.1 + 1.2, duration: 0.8, ease: "easeOut" }}
                        />
                      ))}
                    </div>

                    <div className="space-y-3">
                      {['LUCKY', 'HBL', 'ENGRO'].map((stock, i) => (
                        <motion.div
                          key={stock}
                          className="flex items-center justify-between py-2 px-3 bg-white/5 dark:bg-gray-700/50 rounded-lg"
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 + 1.5 }}
                        >
                          <span className="text-gray-700 dark:text-gray-300">{stock}</span>
                          <span className="text-green-400">+2.4%</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {[
              { value: 500, suffix: '+', label: 'PSX Companies Tracked', icon: Building2 },
              { value: 24, suffix: '/7', label: 'Real-time Analysis', icon: Clock },
              { value: 99.9, suffix: '%', label: 'Uptime Guarantee', icon: Shield },
              { value: 10, suffix: 'K+', label: 'Active Investors', icon: Users },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="text-center group"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
              >
                <div className="bg-white dark:bg-gray-800/90 backdrop-blur-xl rounded-2xl p-6 border border-gray-200 dark:border-gray-700 group-hover:border-blue-500/30 transition-all duration-300 shadow-lg dark:shadow-gray-900/50">
                  <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-400 to-blue-400 bg-clip-text text-transparent mb-2">
                    <AnimatedCounter end={stat.value} />
                    {stat.suffix}
                  </div>
                  <div className="text-gray-600 dark:text-gray-300 font-medium">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-20">
        <div className="max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
              Powerful Features for Smart Investing
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our comprehensive platform combines AI analysis, real-time data, and expert insights 
              to give you the edge in Pakistan's stock market.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Brain,
                title: "AI-Powered Analysis",
                description: "Advanced machine learning algorithms analyze market trends, company fundamentals, and news sentiment to provide intelligent investment recommendations.",
                gradient: "from-purple-500 to-pink-500"
              },
              {
                icon: TrendingUp,
                title: "Real-Time Market Data",
                description: "Access live PSX data, price movements, volume analysis, and technical indicators updated every minute for informed decision making.",
                gradient: "from-green-500 to-emerald-500"
              },
              {
                icon: NewspaperIcon,
                title: "News Intelligence",
                description: "Automated news scraping and sentiment analysis from Pakistani financial news sources to understand market-moving events.",
                gradient: "from-blue-500 to-cyan-500"
              },
              {
                icon: BarChart3,
                title: "Portfolio Analytics",
                description: "Comprehensive portfolio tracking with performance metrics, risk analysis, and personalized recommendations based on your investment history.",
                gradient: "from-orange-500 to-red-500"
              },
              {
                icon: Shield,
                title: "Risk Management",
                description: "Sophisticated risk assessment tools help you understand and manage investment risks with position sizing and diversification recommendations.",
                gradient: "from-indigo-500 to-purple-500"
              },
              {
                icon: Zap,
                title: "Instant Notifications",
                description: "Real-time alerts for significant price movements, breaking news, and investment opportunities tailored to your preferences.",
                gradient: "from-yellow-500 to-orange-500"
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="group relative"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -10 }}
              >
                <div className="relative bg-white dark:bg-gray-800/90 backdrop-blur-xl rounded-2xl p-8 border border-gray-200 dark:border-gray-700 group-hover:border-blue-500/30 transition-all duration-500 h-full shadow-lg dark:shadow-gray-900/50">
                  {/* Glow effect on hover */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${feature.gradient} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-500`}></div>
                  
                  <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    {feature.description}
                  </p>
                  
                  <motion.div 
                    className="mt-6 inline-flex items-center text-blue-600 group-hover:text-blue-500 transition-colors cursor-pointer"
                    whileHover={{ x: 5 }}
                  >
                    Learn more <ArrowRight className="ml-2 w-4 h-4" />
                  </motion.div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* About/Motto Section */}
      <section id="about" className="relative py-20">
        <div className="max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
              Our Mission
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
              "Democratizing intelligent investing in Pakistan by making sophisticated AI-powered 
              market analysis accessible to every investor, from beginners to professionals."
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
              <div className="text-center">
                <Target className="w-16 h-16 mx-auto mb-4 text-blue-600 dark:text-blue-400 opacity-80" />
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Precision</h3>
                <p className="text-gray-600 dark:text-gray-300 opacity-90">Data-driven insights for accurate investment decisions</p>
              </div>
              <div className="text-center">
                <Users className="w-16 h-16 mx-auto mb-4 text-blue-600 dark:text-blue-400 opacity-80" />
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Accessibility</h3>
                <p className="text-gray-600 dark:text-gray-300 opacity-90">Making professional-grade analysis available to all</p>
              </div>
              <div className="text-center">
                <Award className="w-16 h-16 mx-auto mb-4 text-blue-600 dark:text-blue-400 opacity-80" />
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Excellence</h3>
                <p className="text-gray-600 dark:text-gray-300 opacity-90">Continuously improving to deliver the best results</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="relative py-20">
        <div className="max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
              Meet Our Team
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Experienced professionals combining finance expertise with cutting-edge technology 
              to revolutionize investment analysis in Pakistan.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                name: "Ahmed Ali",
                role: "CEO & Co-Founder",
                expertise: "15+ years in Pakistani financial markets",
                image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400"
              },
              {
                name: "Sarah Khan",
                role: "CTO & Co-Founder",
                expertise: "AI/ML Engineer, Ex-Google",
                image: "https://images.unsplash.com/photo-1494790108755-2616b056b8e7?w=400"
              },
              {
                name: "Dr. Hassan Sheikh",
                role: "Chief Data Scientist",
                expertise: "PhD in Financial Engineering",
                image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
              },
              {
                name: "Fatima Rashid",
                role: "Head of Product",
                expertise: "UX Design & Product Strategy",
                image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400"
              },
              {
                name: "Usman Malik",
                role: "Lead Backend Engineer",
                expertise: "Distributed Systems & APIs",
                image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400"
              },
              {
                name: "Zara Ahmed",
                role: "Financial Analyst",
                expertise: "PSX Market Specialist",
                image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400"
              }
            ].map((member, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card p-6 text-center hover:shadow-lg transition-shadow"
              >
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                />
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                  {member.name}
                </h3>
                <p className="text-blue-600 font-medium mb-2">{member.role}</p>
                <p className="text-gray-600 dark:text-gray-300 text-sm">{member.expertise}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20">
        <div className="max-w-4xl mx-auto text-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-white dark:bg-gray-800/90 backdrop-blur-xl rounded-3xl p-12 border border-gray-200 dark:border-gray-700 shadow-lg dark:shadow-gray-900/50"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
              Ready to Transform Your Investing?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
              Join thousands of smart investors who trust BullBearPK for their investment decisions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link 
                  to="/register" 
                  className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-blue-500 text-white rounded-xl font-semibold shadow-2xl hover:shadow-primary-500/25 transition-all duration-300"
                >
                  Start Free Trial
                  <Rocket className="ml-2 w-5 h-5" />
                </Link>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link 
                  to="/login" 
                  className="inline-flex items-center px-8 py-4 bg-white/10 dark:bg-gray-700/50 text-white rounded-xl font-semibold backdrop-blur-sm border border-white/20 dark:border-gray-600 hover:bg-white/20 dark:hover:bg-gray-600/50 transition-all duration-300"
                >
                  Sign In
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-16 border-t border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div className="md:col-span-2">
              <div className="flex items-center mb-4">
                <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400 mr-2" />
                <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
                  BullBearPK
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md">
                AI-powered investment intelligence for Pakistan Stock Exchange. 
                Making smart investing accessible to everyone.
              </p>
              <div className="flex space-x-4">
                <motion.a 
                  href="#" 
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.1 }}
                >
                  <i className="fab fa-twitter text-gray-700 dark:text-gray-300"></i>
                </motion.a>
                <motion.a 
                  href="#" 
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.1 }}
                >
                  <i className="fab fa-linkedin text-gray-700 dark:text-gray-300"></i>
                </motion.a>
                <motion.a 
                  href="#" 
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.1 }}
                >
                  <i className="fab fa-github text-gray-700 dark:text-gray-300"></i>
                </motion.a>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-6 text-gray-800 dark:text-white">Product</h4>
              <ul className="space-y-3 text-gray-600 dark:text-gray-300">
                <li><a href="#features" className="hover:text-primary-400 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">API</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-6 text-gray-800 dark:text-white">Company</h4>
              <ul className="space-y-3 text-gray-600 dark:text-gray-300">
                <li><a href="#about" className="hover:text-primary-400 transition-colors">About</a></li>
                <li><a href="#team" className="hover:text-primary-400 transition-colors">Team</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-primary-400 transition-colors">Contact</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                &copy; 2024 BullBearPK. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-500 dark:text-gray-400 hover:text-blue-600 text-sm transition-colors">Privacy Policy</a>
                <a href="#" className="text-gray-500 dark:text-gray-400 hover:text-blue-600 text-sm transition-colors">Terms of Service</a>
                <a href="#" className="text-gray-500 dark:text-gray-400 hover:text-blue-600 text-sm transition-colors">Cookie Policy</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage 