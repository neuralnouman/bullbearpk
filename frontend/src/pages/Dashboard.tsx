import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Send, 
  Menu, 
  X, 
  Plus, 
  MessageSquare, 
  TrendingUp, 
  BarChart3, 
  User, 
  Settings, 
  LogOut,
  Sun,
  Moon,
  Bot
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useTheme } from '../contexts/ThemeContext'
import toast from 'react-hot-toast'
import HybridInputForm from '../components/HybridInputForm'
import { submitHybridInput } from '../utils/api'
import RecommendationCard from '../components/RecommendationCard'

interface Message {
  id: string
  content: string
  sender: 'user' | 'assistant'
  timestamp: Date
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { theme, toggleTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'Investment Analysis',
      messages: [
        {
          id: '1',
          content: 'Welcome to BullBearPK! I\'m your AI investment assistant. How can I help you analyze the Pakistan Stock Exchange today?',
          sender: 'assistant',
          timestamp: new Date()
        }
      ],
      createdAt: new Date()
    }
  ])
  const [activeConversationId, setActiveConversationId] = useState('1')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const activeConversation = conversations.find(c => c.id === activeConversationId)

  const [formData, setFormData] = useState<any>({});
  const [backendResult, setBackendResult] = useState<any>(null);
  const [showFormModal, setShowFormModal] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [activeConversation?.messages])

  useEffect(() => {
    // Show modal if no form data in localStorage
    if (!localStorage.getItem('hybridFormData')) {
      setShowFormModal(true);
    }
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem('hybridFormData');
    if (saved) setFormData(JSON.parse(saved));
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    // Add user message
    setConversations(prev => 
      prev.map(conv => 
        conv.id === activeConversationId 
          ? { ...conv, messages: [...conv.messages, newMessage] }
          : conv
      )
    )

    setInputMessage('')
    setIsTyping(true)
    const res = await submitHybridInput(formData, inputMessage, user?.id || 'demo_user');
    setBackendResult(res);
    // Add assistant message to conversation
    setConversations(prev =>
      prev.map(conv =>
        conv.id === activeConversationId
          ? { ...conv, messages: [...conv.messages, {
              id: Date.now().toString(),
              content: res.ask || (res.recommendations ? JSON.stringify(res.recommendations, null, 2) : 'No response'),
              sender: 'assistant',
              timestamp: new Date()
            }] }
          : conv
      )
    );
    setIsTyping(false);

    if (res.ask) {
      // Add follow-up question as assistant message
      setConversations(prev =>
        prev.map(conv =>
          conv.id === activeConversationId
            ? { ...conv, messages: [...conv.messages, {
                id: Date.now().toString(),
                content: res.ask,
                sender: 'assistant',
                timestamp: new Date()
              }] }
            : conv
        )
      );
    }

    if (res.recommendations) {
      // Add a summary message to chat
      setConversations(prev =>
        prev.map(conv =>
          conv.id === activeConversationId
            ? { ...conv, messages: [...conv.messages, {
                id: Date.now().toString(),
                content: "Here are your personalized recommendations:",
                sender: 'assistant',
                timestamp: new Date()
              }] }
            : conv
        )
      );
      // Optionally, store recommendations in state for summary card display
      setBackendResult(res);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [
        {
          id: '1',
          content: 'Hello! I\'m ready to help you with investment analysis and market insights.',
          sender: 'assistant',
          timestamp: new Date()
        }
      ],
      createdAt: new Date()
    }

    setConversations(prev => [newConversation, ...prev])
    setActiveConversationId(newConversation.id)
  }

  const handleLogout = () => {
    logout()
    toast.success('Logged out successfully')
  }

  const handleFormSubmit = async (form: any) => {
    setFormData(form);
    localStorage.setItem('hybridFormData', JSON.stringify(form));
    const res = await submitHybridInput(form, 'Here are my investment preferences', user?.id || 'demo_user');
    setBackendResult(res);

    if (res.recommendations) {
      setConversations(prev =>
        prev.map(conv =>
          conv.id === activeConversationId
            ? { ...conv, messages: [
                ...conv.messages,
                {
                  id: Date.now().toString(),
                  content: "Here are your personalized recommendations:",
                  sender: 'assistant',
                  timestamp: new Date()
                },
                ...res.recommendations.map((rec: any, i: number) => ({
                  id: (Date.now() + i + 1).toString(),
                  content: `• ${rec.company}: ${rec.reason} (Risk: ${rec.risk}, Allocation: ${rec.allocation}, News: ${rec.news_sentiment})`,
                  sender: 'assistant',
                  timestamp: new Date()
                }))
              ] }
            : conv
        )
      );
    }
    setShowFormModal(false);
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold gradient-text">BullBearPK</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <X size={20} />
            </button>
          </div>
          <button
            onClick={createNewConversation}
            className="btn-primary w-full flex items-center justify-center"
          >
            <Plus size={20} className="mr-2" />
            New Chat
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => setActiveConversationId(conversation.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeConversationId === conversation.id
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center">
                  <MessageSquare size={16} className="mr-2 flex-shrink-0" />
                  <span className="truncate text-sm">{conversation.title}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* User Menu */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="space-y-2">
            <button className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <BarChart3 size={20} className="mr-3" />
              <span className="text-sm">Portfolio</span>
            </button>
            <button 
              onClick={() => window.location.href = '/market-data'}
              className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <TrendingUp size={20} className="mr-3" />
              <span className="text-sm">Market Data</span>
            </button>
            <button 
              onClick={toggleTheme}
              className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              {theme === 'light' ? <Moon size={20} className="mr-3" /> : <Sun size={20} className="mr-3" />}
              <span className="text-sm">Theme</span>
            </button>
            <button className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <Settings size={20} className="mr-3" />
              <span className="text-sm">Settings</span>
            </button>
            <button 
              onClick={handleLogout}
              className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-red-600"
            >
              <LogOut size={20} className="mr-3" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <User size={16} className="text-white" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className={`${sidebarOpen ? 'lg:hidden' : ''} p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg mr-3`}
              >
                <Menu size={20} />
              </button>
              <h1 className="text-xl font-semibold">Investment Assistant</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                PSX: <span className="text-green-600">+1.2%</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                KMI 30: <span className="text-blue-600">45,234</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto space-y-6">
            {activeConversation?.messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                  <div className={`flex items-start space-x-3 ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.sender === 'user' 
                        ? 'bg-primary-600' 
                        : 'bg-gray-200 dark:bg-gray-700'
                    }`}>
                      {message.sender === 'user' ? (
                        <User size={16} className="text-white" />
                      ) : (
                        <Bot size={16} className="text-gray-600 dark:text-gray-300" />
                      )}
                    </div>
                    <div className={`flex-1 ${message.sender === 'user' ? 'text-right' : ''}`}>
                      <div className={`inline-block p-4 rounded-lg ${
                        message.sender === 'user'
                          ? 'bg-primary-600 text-white'
                          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                      }`}>
                        <p className="text-sm leading-relaxed">{message.content}</p>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
            
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <Bot size={16} className="text-gray-600 dark:text-gray-300" />
                  </div>
                  <div className="bg-white dark:bg-gray-800/95 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white dark:bg-gray-800/95 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about stock analysis, investment recommendations, market trends..."
                  className="input w-full text-sm resize-none"
                  disabled={isTyping}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isTyping}
                className="btn-primary p-3"
              >
                <Send size={20} />
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500 text-center">
              BullBearPK can make mistakes. Consider checking important information.
            </div>
          </div>
        </div>


        {backendResult?.recommendations && (
          <div>
            <h2 className="mt-4 mb-2 font-semibold">Summary Recommendations</h2>
            {backendResult.recommendations.map((rec: any, i: number) => (
              <RecommendationCard key={i} rec={rec} />
            ))}
            <div className="mt-4">
              <span>Was this helpful?</span>
              <button
                className="ml-2 btn-primary"
                onClick={() => {
                  // Call backend to store feedback
                  fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: user?.id || 'demo_user',
                      feedback: 'yes',
                      recommendations: backendResult.recommendations
                    })
                  });
                }}
              >Yes</button>
              <button
                className="ml-2 btn-secondary"
                onClick={() => {
                  fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: user?.id || 'demo_user',
                      feedback: 'no',
                      recommendations: backendResult.recommendations
                    })
                  });
                }}
              >No</button>
            </div>
          </div>
        )}

        {showFormModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-lg">
              <h2 className="font-bold mb-2">Tell us about your investment goals</h2>
              <HybridInputForm onSubmit={form => {
                setFormData(form);
                localStorage.setItem('hybridFormData', JSON.stringify(form));
                setShowFormModal(false);
              }} />
            </div>
          </div>
        )}

        <button
          className="btn-secondary mb-2"
          onClick={() => setShowFormModal(true)}
        >
          Edit Investment Preferences
        </button>
      </div>
    </div>
  )
}

export default Dashboard